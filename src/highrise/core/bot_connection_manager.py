import time
import json
import asyncio
import websockets
from websockets import State
from typing import Any, TYPE_CHECKING

from ..models.highrise.highrise_models import Credentials
from ..constants import HIGHRISE_WS_URI, SERVER_ERRORS

from .bot_event_handlers import EVENT_HANDLERS

if TYPE_CHECKING:
    from ..base_bot import BaseBot


class ConnectionManager:
    """Manages the network lifecycle and gateway session of a Highrise bot.

    This component encapsulates low-level WebSocket operations, including
    establishing connections, routing raw frames to event dispatchers, 
    maintaining the gateway heartbeat loop, and coordinating exponential 
    backoff auto-reconnect sequences.
    """

    def __init__(self, bot: "BaseBot") -> None:
        self.bot = bot
        self._ws: websockets.ClientConnection | None = None
        
        self._is_running: bool = False
        self._is_paused: bool = False
        self._auto_reconnect: bool = True

        cfg = bot.config.connection
        self._keepalive_delay = cfg.keepalive_delay
        self._keepalive_payload = {"_type": "KeepaliveRequest"}
        self._min_reconnect_delay = cfg.min_reconnect_delay
        self._max_reconnect_delay = cfg.max_reconnect_delay
        self._reconnect_backoff_factor = cfg.reconnect_backoff_factor
        self._max_reconnect_attempts = cfg.max_reconnect_attempts

    @property
    def ws_client(self) -> websockets.ClientConnection | None:
        """Exposes the active socket instance to the requester abstraction layer."""
        return self._ws

    @property
    def state(self) -> State | None:
        return self._ws.state if self._ws is not None else None

    @property
    def is_connected(self) -> bool:
        return self._ws is not None and self.state == State.OPEN

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    async def login(self, room_id: str, api_token: str, auto_reconnect: bool = True) -> None:
        """Connects to the Highrise WebSocket API with only the requested events."""
        self._is_running = True
        self._auto_reconnect = auto_reconnect

        self.bot._tasks.on_first_start()
        await self.bot.before_start()

        delay = self._min_reconnect_delay
        self.bot._context.credentials = Credentials(room_id, api_token)
        reconnect_attempts = 0

        while self._is_running:
            try:
                await self._connect_and_listen()
                delay = self._min_reconnect_delay
                reconnect_attempts = 0

            except (websockets.exceptions.ConnectionClosed, ConnectionError, OSError) as e:
                if not self._is_running or not self._auto_reconnect:
                    break

                reconnect_attempts += 1
                if self._max_reconnect_attempts is not None and reconnect_attempts > self._max_reconnect_attempts:
                    self.bot.logger.warning(
                        f"Max reconnect attempts ({self._max_reconnect_attempts}) reached. Giving up."
                    )
                    break

                code = getattr(e, "code", "N/A")
                reason = getattr(e, "reason", str(e))
                self.bot.logger.warning(f"Connection lost (code={code} reason={reason}). Reconnecting in {delay:.1f}s...")

                await asyncio.sleep(delay)
                delay = min(delay * self._reconnect_backoff_factor, self._max_reconnect_delay)

            except Exception as e:
                if not self._is_running or not self._auto_reconnect:
                    break

                reconnect_attempts += 1
                if self._max_reconnect_attempts is not None and reconnect_attempts > self._max_reconnect_attempts:
                    self.bot.logger.warning(
                        f"Max reconnect attempts ({self._max_reconnect_attempts}) reached. Giving up."
                    )
                    break

                self.bot.logger.error(f"Unexpected error in connection loop: {e}")
                await asyncio.sleep(delay)
                delay = min(delay * self._reconnect_backoff_factor, self._max_reconnect_delay)

            finally:
                self.bot._context.requester.close()

        self.bot.logger.info("Bot session ended.")

    async def logout(self) -> None:
        """Gracefully logs out and disables automatic reconnection."""
        self.bot.logger.info("Logging out from Highrise Server...")
        self._is_running = False
        self._auto_reconnect = False

        await self._cleanup()
        self.bot.logger.info("Logged out successfully.")

    async def force_reconnect(self) -> None:
        if not self._is_running:
            self.bot.logger.warning("Cannot reconnect: Bot is not currently running.")
            return

        self.bot.logger.info("Manual reconnection requested. Resetting socket connection...")
        await self._cleanup()

    def pause(self) -> bool:
        if self.is_paused:
            return False
        self._is_paused = True
        return True

    def resume(self) -> bool:
        if not self.is_paused:
            return False
        self._is_paused = False
        return True

    async def _connect_and_listen(self) -> None:
        """Establishes a single WebSocket session and processes incoming frames."""
        await self._cleanup()

        headers = {
            "room-id": self.bot.credentials.room_id,
            "api-token": self.bot.credentials.api_token
        }

        url = f"{HIGHRISE_WS_URI}?events={self.bot._event_params}"

        self._ws = await websockets.connect(url, additional_headers=headers, compression=None)
        self.bot.logger.info("Successfully connected to Highrise!")
        self.bot._context.metrics.mark_connected()

        if self.bot.config.auto_fetch.room_users:
            self.bot._tasks.create_task(self.bot._tasks.fetch_room_users(), name="fetch_room_users")

        self.bot._tasks.create_task(self._send_keepalive(), name="keepalive")
        self.bot._tasks.start_all_loops()

        while self._is_running and self.is_connected:
            raw_frame = await self._ws.recv()
            await self._handle_raw_frame(raw_frame)

    async def _send_keepalive(self) -> None:
        try:
            while self._is_running and self.is_connected:
                await asyncio.sleep(self._keepalive_delay)

                if self.is_connected:
                    start = time.monotonic()
                    success, _ = await self.bot._context.requester.send(self._keepalive_payload)
                    if success:
                        self.bot._context.metrics.record_latency(time.monotonic() - start)

        except (asyncio.CancelledError, websockets.exceptions.ConnectionClosed):
            pass
        except Exception as e:
            self.bot.logger.debug(f"Keepalive loop encountered an error: {e}")

    async def _handle_raw_frame(self, raw_frame: str) -> None:
        """Handle the raw frame coming from highrise websocket server"""
        try:
            data = json.loads(raw_frame)
            data_message = data.get('message')
            
            if data_message in SERVER_ERRORS:
                self._handle_server_errors(data)
                return

            if self.bot._context.requester.handle_incoming_response(data):
                return

            if self.is_paused:
                return
            
            await self._dispatch_events(data)
        except json.JSONDecodeError as e:
            self.bot.logger.error(f"Failed to parse incoming frame: {e}")

    async def _dispatch_events(self, data: dict[str, Any]) -> None:
        """Route each event to its own hook to be used by the dev"""
        event_type = data.get("_type")

        if event_type == "KeepAliveResponse":
            return

        handler = EVENT_HANDLERS.get(event_type)
        if handler:
            self.bot._context.metrics.record_event()
            handler(self.bot, data)

    async def _cleanup(self) -> None:
        """Safely cleans up all states and closes tasks and socket connection handles."""
        self.bot._tasks.cancel_all_loops()

        ws = self._ws
        if ws is not None:
            await ws.close()
            self._ws = None
            self.bot._context.metrics.mark_disconnected()
            self.bot._context.metrics.reset_events()
            
        await self.bot._tasks.cancel_and_gather_tasks()
        
        self.bot._context.cache.clear_all()
        self.bot.cached_users.clear()

    def _handle_server_errors(self, error_data: dict) -> None:
        error_message = error_data.get("message")
        
        self._is_running = False
        self.bot.logger.critical(error_message)
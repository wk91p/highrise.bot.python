import time
import json
import asyncio
import inspect
import websockets
from websockets import State
from typing import Any
from collections.abc import Coroutine, Callable

from .ws_requester import WSRequester
from .event_handlers import EVENT_HANDLERS
from .tools.logger import setup_logger
from .tools.validator import Validator
from .highrise_api import HighriseApi
from .cache.cache import CacheManager
from .cache.room_users import RoomUsersCache
from .bot_hooks import BotHooks
from .configs import BotConfig
from .tools.awaiter import Awaiter
from .decorators.loop_task import LoopTask
from .tools.roles import Roles
from .metrics import Metrics
from .webapi import WebApi

from .models.events import *
from .models.highrise_models import *
from .constants import HIGHRISE_WS_URI, EVENT_HOOK_MAP

class BotContext:
    """SDK-Level shared mutable state and dependencies."""

    def __init__(self, requester: "WSRequester", validator: "Validator") -> None:
        self.requester = requester
        self.validator = validator
        self.session_metadata: SessionMetadata | None = None
        self.credentials: Credentials | None = None
        self.cache = CacheManager()
        self.metrics = Metrics()

class BaseBot(BotHooks):
    """A base class for Highrise bots.
    Bots join a room and interact with everything in it.

    Subclass this class and implement the handlers you want to use.

    The `self.highrise` attribute can be used to make requests.
    """

    def __init__(self, config: BotConfig | None = None) -> None:
        self.config = config or BotConfig()

        self._ws: websockets.ClientConnection | None = None

        self.logger = setup_logger(
            name=self.config.logger.name,
            level=self.config.logger.level,
            show_time=self.config.logger.show_time,
        )

        requester = WSRequester(lambda: self._ws, self.logger)
        validator = Validator()
        self._context = BotContext(requester, validator)

        self.highrise = HighriseApi(self._context)
        self.cached_users = RoomUsersCache()
        self.awaiter = Awaiter()
        self.roles = Roles(path=self.config.roles.path)
        self.webapi = WebApi(self._context)

        self._tasks: list[asyncio.Task] = []
        self._loops: list[LoopTask] = []
        self._is_running: bool = False
        self._is_paused: bool = False
        self._auto_reconnect: bool = True
        self._event_params = self._get_requested_events()

        self._keepalive_delay = self.config.connection.keepalive_delay
        self._keepalive_payload = {"_type": "KeepaliveRequest"}

        self._min_reconnect_delay = self.config.connection.min_reconnect_delay
        self._max_reconnect_delay = self.config.connection.max_reconnect_delay
        self._reconnect_backoff_factor = self.config.connection.reconnect_backoff_factor
        self._max_reconnect_attempts = self.config.connection.max_reconnect_attempts

    def _on_first_start(self) -> None:
        """Internal SDK setup that must run exactly once, before the
        dev's before_start() hook. Devs never call or override this."""
        task = asyncio.create_task(self._autosave_roles_loop(), name="autosave_roles")
        self._tasks.append(task)

    async def _autosave_roles_loop(self) -> None:
        """Periodically saves roles to disk. Runs for the life of the bot."""
        try:
            while self._is_running:
                await asyncio.sleep(self.config.roles.autosave_interval)
                self.roles.save()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Roles autosave loop encountered an error: {e}", exc_info=True)

    def _get_requested_events(self) -> str:
        """Dynamically builds the required Highrise WebSocket query events by checking which hook being override."""
        active_events: set[str] = set()

        for event_name, hook_names in EVENT_HOOK_MAP.items():
            for hook in hook_names:
                
                subclass_method = getattr(self, hook, None)
                base_method = getattr(BaseBot, hook, None)

                if inspect.unwrap(subclass_method) != inspect.unwrap(base_method):
                    active_events.add(event_name)
                    break

        return ",".join(active_events)

    def _is_open(self) -> bool:
        return self._ws is not None and self._ws.state == State.OPEN

    async def _send_keepalive(self) -> None:
        try:
            while self._is_running and self._ws is not None:
                await asyncio.sleep(self._keepalive_delay)

                if self._ws and self._is_open():
                    start = time.monotonic()
                    success, _ = await self._context.requester.send(self._keepalive_payload)
                    if success:
                        self._context.metrics.record_latency(time.monotonic() - start)

        except (asyncio.CancelledError, websockets.exceptions.ConnectionClosed):
            pass
        except Exception as e:
            self.logger.debug(f"Keepalive loop encountered an error: {e}")

    async def _dispatch_events(self, data):
        """Route each event to it's own hook to be used by the dev"""
        event_type = data.get("_type")

        if event_type == "KeepAliveResponse":
            return

        handler = EVENT_HANDLERS.get(event_type)
        if handler:
            self._context.metrics.record_event()
            handler(self, data)

    async def _handle_raw_frame(self, raw_frame: str) -> None:
        """Handle the raw frame coming from highrise websocket server"""
        try:
            data = json.loads(raw_frame)

            if self._context.requester.handle_incoming_response(data):
                return

            if self._is_paused:
                return

            await self._dispatch_events(data)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse incoming frame: {e}")

    async def _cleanup(self) -> None:
        """Safely cleanup all states and closes tasks and socket connection handles."""

        for registered_loop in self._loops:
            registered_loop.cancel()

        ws = self._ws
        if ws is not None:
            await ws.close()
            self._ws = None
            self._context.metrics.mark_disconnected()
            self._context.metrics.reset_events()
            
        for task in self._tasks:
            if not task.done():
                task.cancel()

        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        
        self._tasks.clear()
        self._context.cache.clear_all()
        self.cached_users.clear()

    async def _fetch_room_users(self) -> None:
        """Fetches the current room users once on connection establishment, so `self.cached_users`
        is populated before any join/leave/move events start arriving."""
        response = await self.highrise.get_room_users()
        if response.ok:
            self.cached_users = RoomUsersCache._from_response(response)
        else:
            self.logger.warning(f"Failed to fetch room users to cache: {response.error}")

    async def _connect_and_listen(self) -> None:
        """Establishes a single WebSocket session and processes incoming frames."""

        await self._cleanup()

        headers = {
            "room-id": self.credentials.room_id,
            "api-token": self.credentials.api_token
        }

        url = f"{HIGHRISE_WS_URI}?events={self._event_params}"

        self._ws = await websockets.connect(url, additional_headers=headers, compression=None)
        self.logger.info("Successfully connected to Highrise!")
        self._context.metrics.mark_connected()

        if self.config.auto_fetch.room_users:
            self._create_task(self._fetch_room_users())

        keepalive_task = asyncio.create_task(self._send_keepalive())
        self._tasks.append(keepalive_task)

        for registered_loop in self._loops:
            registered_loop.start()

        while self._is_running and self._ws is not None:
            raw_frame = await self._ws.recv()
            await self._handle_raw_frame(raw_frame)

    def _on_task_complete(self, task: asyncio.Task) -> None:
        """ 
            Callback triggered when an task completes. 
            Logs any unhandled exception without crashing the bot loop.
        """

        if not task.cancelled():
            exc = task.exception()
            if exc is not None:
                self.logger.error(f"Unhandled error in task '{task.get_name()}':", exc_info=exc)

    def _create_task(self, coro, name: str = "fn_task") -> asyncio.Task:
        """ 
            Helper to create a fire-and-forget task for each function call to keep the loop 
            running without being delayed, with automated error logging.
        """

        task = asyncio.create_task(coro, name=name)
        task.add_done_callback(self._on_task_complete)
        return task

    # -- public methods

    async def login(
        self,
        room_id: str,
        api_token: str,
        auto_reconnect: bool = True
    ) -> None:
        """Connects to the Highrise WebSocket API with only the requested events."""

        self._is_running = True
        self._auto_reconnect = auto_reconnect

        self._on_first_start()
        await self.before_start()

        delay = self._min_reconnect_delay
        self._context.credentials = Credentials(room_id, api_token)
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
                    self.logger.warning(
                        f"Max reconnect attempts ({self._max_reconnect_attempts}) reached. Giving up."
                    )
                    break

                code = getattr(e, "code", "N/A")
                reason = getattr(e, "reason", str(e))
                self.logger.warning(f"Connection lost (code={code} reason={reason}). Reconnecting in {delay:.1f}s...")

                await asyncio.sleep(delay)

                delay = min(delay * self._reconnect_backoff_factor, self._max_reconnect_delay)

            except Exception as e:
                if not self._is_running or not self._auto_reconnect:
                    break

                reconnect_attempts += 1
                if self._max_reconnect_attempts is not None and reconnect_attempts > self._max_reconnect_attempts:
                    self.logger.warning(
                        f"Max reconnect attempts ({self._max_reconnect_attempts}) reached. Giving up."
                    )
                    break

                self.logger.error(f"Unexpected error in connection loop: {e}")
                await asyncio.sleep(delay)

                delay = min(delay * self._reconnect_backoff_factor, self._max_reconnect_delay)

            finally:
                self._context.requester.close()

        self.logger.info("Bot session ended.")


    async def logout(self) -> None:
        """Gracefully logs out and disables automatic reconnection."""

        self.logger.info("Logging out from Highrise Server...")

        self._is_running = False
        self._auto_reconnect = False

        await self._cleanup()
        self.logger.info("Logged out successfully.")

    async def reconnect(self) -> None:
        """
        Manually forces a socket disconnection to trigger the network loop's 
        reconnection sequence. Useful for manual lag flushing or state resets.
        """

        if not self._is_running:
            self.logger.warning("Cannot reconnect: Bot is not currently running.")
            return

        self.logger.info("Manual reconnection requested. Resetting socket connection...")
        
        await self._cleanup()

    def pause(self) -> None:
        """Temporarily stops processing incoming events without disconnecting.
        The connection, keepalive, and reconnect logic all keep running.

        - Return `True` if success, `False` if already paused
        """
        if self._is_paused:
            return False
        
        self._is_paused = True
        return True

    def resume(self) -> None:
        """Resumes processing incoming events after pause().
        
        - Return `True` if success, `False` if already resumed
        """

        if not self._is_paused:
            return False
        
        self._is_paused = False
        return True

    ## -- decorators

    def loop(self, seconds: float):
        """Decorator factory to register an asynchronous background interval task"""
        
        def decorator(func: Callable[[], Coroutine[Any, Any, None]] = None):
            if not inspect.iscoroutinefunction(func):
                raise TypeError(f"The @loop decorator can only be used on async functions, not '{type(func).__name__}'")

            loop_task = LoopTask(
                coro_fn=func,
                seconds=seconds,
                logger=self.logger
            )

            self._loops.append(loop_task)

            return func
        return decorator

    # -- properties

    @property
    def session_metadata(self) -> "SessionMetadata | None":
        """The session metadata received once the bot connects. `None` before then."""
        return self._context.session_metadata

    @property
    def state(self) -> State | None:
        """The current WebSocket connection state, or None if not connected yet."""
        return self._ws.state if self._ws is not None else None

    @property
    def credentials(self) -> Credentials | None:
        """The `room_id`/`api_token` used for the current session. `None` before connecting."""
        return self._context.credentials

    @property
    def is_connected(self) -> bool:
        """Whether the bot currently has an open WebSocket connection."""
        return self.state == State.OPEN

    @property
    def is_paused(self) -> bool:
        """Whether the bot is currently paused."""
        return self._is_paused

    @property
    def uptime(self) -> float:
        """Seconds since the current connection was established."""
        return self._context.metrics.uptime

    @property
    def latency(self) -> float | None:
        """Round-trip time in seconds of the last keepalive."""
        return self._context.metrics.latency

    @property
    def events_processed(self) -> int:
        """The total number of events processed during this session."""
        return self._context.metrics.events_processed
    
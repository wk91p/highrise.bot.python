import asyncio
import json
import uuid
from websockets import State
from typing import Any
from collections.abc import Callable
from websockets import ClientConnection

class WSRequester:
    def __init__(self, ws_getter: Callable[[], ClientConnection], logger) -> None:
        """
        :param ws_getter: A function or lambda returning the active WebSocket connection.
        """
        self._get_ws = ws_getter
        self.logger = logger
        self._pending_requests: dict[str, asyncio.Future[tuple[bool, Any]]] = {}

    async def send(self, payload: dict[str, Any], timeout: float = 10.0) -> tuple[bool, Any]:
        """
        Sends a dictionary payload over WebSocket and awaits the response.
        """
        ws = self._get_ws()
        if not ws or not ws.state == State.OPEN:
            return False, "WebSocket is not connected."

        rid = str(uuid.uuid4())
        payload["rid"] = rid

        loop = asyncio.get_running_loop()
        future: asyncio.Future[tuple[bool, Any]] = loop.create_future()
        self._pending_requests[rid] = future

        try:
            await ws.send(json.dumps(payload))

            return await asyncio.wait_for(future, timeout=timeout)

        except asyncio.TimeoutError:
            return False, "Request timed out"

        except Exception as e:
            return False, str(e)

        finally:
            self._pending_requests.pop(rid, None)

    def handle_incoming_response(self, data: dict[str, Any]) -> bool:
        """
        Processes an incoming response from the WebSocket.
        """
        rid = data.get("rid")
        if not rid or rid not in self._pending_requests:
            return False

        future = self._pending_requests.get(rid)
        if future and not future.done():
            event_type = data.get("_type")

            if event_type == "Error":
                err_msg = data.get("message")
                future.set_result((False, err_msg))
            
            else:
                future.set_result((True, data))

        return True

    def close(self) -> None:
        """
        Called when the WebSocket connection is closed/lost.
        Resolves all pending requests immediately instead of waiting for timeout.
        """
        for rid, future in list(self._pending_requests.items()):
            if not future.done():
                future.set_result((False, "Connection closed"))
        self._pending_requests.clear()
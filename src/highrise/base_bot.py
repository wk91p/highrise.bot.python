import asyncio
import inspect
from typing import Any
from collections.abc import Coroutine, Callable
from websockets import State

from .highrise_api import HighriseApi
from .constants import EVENT_HOOK_MAP
from .webapi import WebApi

from .cache.room_users import RoomUsersCache
from .configs import BotConfig

from .tools.logger import setup_logger
from .tools.validator import Validator
from .tools.awaiter import Awaiter
from .tools.roles import Roles

from .core.ws_requester import WSRequester
from .core.bot_context import BotContext
from .core.bot_hooks import BotHooks
from .core.connection_manager import ConnectionManager
from .core.task_manager import TaskManager

from .models.highrise.highrise_models import *

class BaseBot(BotHooks):
    """A base class for Highrise bots.
    Bots join a room and interact with everything in it.
    """

    def __init__(self, config: BotConfig | None = None) -> None:
        self.config = config or BotConfig()

        self.logger = setup_logger(
            name=self.config.logger.name,
            level=self.config.logger.level,
            show_time=self.config.logger.show_time,
        )

        requester = WSRequester(lambda: self._connection.ws_client, self.logger)
        validator = Validator()
        self._context = BotContext(requester, validator)

        self.highrise = HighriseApi(self._context)
        self.cached_users = RoomUsersCache()
        self.awaiter = Awaiter()
        self.roles = Roles(path=self.config.roles.path)
        self.webapi = WebApi(self._context)

        self._connection = ConnectionManager(bot=self)
        self._tasks = TaskManager(bot=self)

        self._event_params = self._get_requested_events()

    def _get_requested_events(self) -> str:
        active_events: set[str] = set()
        for event_name, hook_names in EVENT_HOOK_MAP.items():
            for hook in hook_names:
                subclass_method = getattr(self, hook, None)
                base_method = getattr(BaseBot, hook, None)
                subclass_func = getattr(subclass_method, "__func__", subclass_method)

                if inspect.unwrap(subclass_func) != inspect.unwrap(base_method):
                    active_events.add(event_name)
                    break
        return ",".join(active_events)

    # -- Public Methods

    async def login(self, room_id: str, api_token: str, auto_reconnect: bool = True) -> None:
        await self._connection.login(room_id, api_token, auto_reconnect)

    async def logout(self) -> None:
        await self._connection.logout()

    async def reconnect(self) -> None:
        await self._connection.force_reconnect()

    def pause(self) -> bool:
        return self._connection.pause()

    def resume(self) -> bool:
        return self._connection.resume()

    ## -- Decorators

    def loop(self, seconds: float):
        def decorator(func: Callable[[], Coroutine[Any, Any, None]] = None):
            self._tasks.register_loop(seconds, func)
            return func
        return decorator

    # -- Properties

    @property
    def session_metadata(self) -> "SessionMetadata | None":
        return self._context.session_metadata

    @property
    def state(self) -> State | None:
        return self._connection.state

    @property
    def credentials(self) -> Credentials | None:
        return self._context.credentials

    @property
    def is_connected(self) -> bool:
        return self._connection.is_connected

    @property
    def is_paused(self) -> bool:
        return self._connection.is_paused

    @property
    def uptime(self) -> float:
        return self._context.metrics.uptime

    @property
    def latency(self) -> float | None:
        return self._context.metrics.latency

    @property
    def events_processed(self) -> int:
        return self._context.metrics.events_processed

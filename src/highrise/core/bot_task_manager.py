import asyncio
import inspect
from typing import Any, TYPE_CHECKING
from collections.abc import Callable, Coroutine

from ..cache.room_users import RoomUsersCache
from ..tools.loop_task import LoopTask

if TYPE_CHECKING:
    from ..base_bot import BaseBot

class TaskManager:
    """Manages background loops, concurrent worker tasks, and custom event loops for a bot."""

    def __init__(self, bot: "BaseBot") -> None:
        self.bot = bot
        self._tasks: list[asyncio.Task] = []
        self._loops: list[LoopTask] = []

    @property
    def active_tasks(self) -> list[asyncio.Task]:
        return self._tasks

    @property
    def registered_loops(self) -> list[LoopTask]:
        return self._loops

    def start_core_loops(self) -> None:
        self.create_task(self._autosave_roles_loop(), name="autosave_roles")

    def create_task(self, coro: Coroutine[Any, Any, None], name: str = "fn_task") -> asyncio.Task:
        task = asyncio.create_task(coro, name=name)
        task.add_done_callback(self._on_task_complete)
        self._tasks.append(task)
        return task

    def register_loop(self, seconds: float, func: Callable[[], Coroutine[Any, Any, None]]) -> None:
        loop_task = LoopTask(coro_fn=func, seconds=seconds, logger=self.bot.logger)
        self._loops.append(loop_task)

    def start_all_loops(self) -> None:
        for loop in self._loops:
            loop.start()

    def cancel_all_loops(self) -> None:
        for loop in self._loops:
            loop.cancel()

    async def cancel_and_gather_tasks(self) -> None:
        for task in self._tasks:
            if not task.done():
                task.cancel()

        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        self._tasks.clear()

    def _on_task_complete(self, task: asyncio.Task) -> None:
        if not task.cancelled():
            exc = task.exception()
            if exc is not None:
                self.bot.logger.error(f"Unhandled error in task '{task.get_name()}':", exc_info=exc)

    async def _autosave_roles_loop(self) -> None:
        try:
            while self.bot._connection.is_connected():
                await asyncio.sleep(self.bot.config.roles.autosave_interval)
                self.bot.roles.save()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.bot.logger.error(f"Roles autosave loop encountered an error: {e}", exc_info=True)

    def on_first_start(self) -> None:
        self.start_core_loops()
    
    async def fetch_room_users(self) -> None:
        response = await self.bot.highrise.get_room_users()
        if response.ok:
            self.bot.cached_users = RoomUsersCache._from_response(response)
        else:
            self.bot.logger.warning(f"Failed to fetch room users to cache: {response.error}")

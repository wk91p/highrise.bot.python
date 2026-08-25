import asyncio
import time
from typing import Callable, Coroutine, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..tools.logger import Logger

class LoopTask:
    def __init__(
        self,
        coro_fn: Callable[[], Coroutine[Any, Any, None]],
        seconds: float,
        logger,
    ) -> None:
        self.coro_fn = coro_fn
        self.seconds = seconds
        self.logger = logger
        self._task: asyncio.Task | None = None

    async def _run_loop(self) -> None:
        task_name = self.coro_fn.__name__

        while True:
            start_time = time.monotonic()
            try:
                await self.coro_fn()
            except asyncio.CancelledError:
                raise

            except Exception as e:
                self.logger.error(
                    f"Exception caught inside background loop '{task_name}': {e}",
                    exc_info=True,
                )

            elapsed = time.monotonic() - start_time
            remaining_sleep = max(0.0, self.seconds - elapsed)

            await asyncio.sleep(remaining_sleep)

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            self.logger.warning(f"Background loop '{self.coro_fn.__name__}' already running, start() ignored.")
            return

        self._task = asyncio.create_task(self._run_loop(), name=f"loop_{self.coro_fn.__name__}")

    def cancel(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
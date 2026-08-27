import asyncio
import time
import inspect
from typing import Callable, Coroutine, Any
from .logger import setup_logger
from logging import Logger

class LoopTask:
    """Create new loop task to run every N seconds (seconds are defaulted to `60.0` sec)"""
    def __init__(
        self,
        coro_fn: Callable[[], Coroutine[Any, Any, None]],
        seconds: float = 60.0,
        logger: Logger | None = None,
    ) -> None:
        if not inspect.iscoroutinefunction(coro_fn):
            raise TypeError(f"LoopTask requires an async function, not '{type(coro_fn).__name__}'")

        self._coro_fn = coro_fn
        self._seconds = seconds
        self._logger = logger if logger else setup_logger(name=f"{coro_fn.__name__}")
        self._task: asyncio.Task | None = None

    async def _run_loop(self) -> None:
        task_name = self._coro_fn.__name__

        while True:
            start_time = time.monotonic()
            try:
                await self._coro_fn()
            except asyncio.CancelledError:
                raise

            except Exception as e:
                self._logger.error(
                    f"Exception caught inside background loop '{task_name}': {e}",
                    exc_info=True,
                )

            elapsed = time.monotonic() - start_time
            remaining_sleep = max(0.0, self._seconds - elapsed)

            await asyncio.sleep(remaining_sleep)

    def start(self) -> None:
        """Start the loop task for N seconds until stopped using cancel()"""
        if self._task is not None and not self._task.done():
            self._logger.warning(f"Background loop '{self._coro_fn.__name__}' already running, start() ignored.")
            return

        self._task = asyncio.create_task(self._run_loop(), name=f"loop_{self._coro_fn.__name__}")

    def cancel(self) -> None:
        """Stop the loop task"""
        if self._task and not self._task.done():
            self._task.cancel()

    @property
    def get_loop_task(self) -> asyncio.Task:
        """Return the loop task"""
        return self._task if self._task is not None and not self._task.done() else None
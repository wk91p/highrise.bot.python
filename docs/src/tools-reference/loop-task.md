# LoopTask

`LoopTask` is a utility tool designed to execute an asynchronous function repeatedly on a defined background loop interval. It accurately handles drift correction by tracking code execution duration and includes robust error isolation so exceptions inside the running task never crash the main application.

# Setup

You can initialize a `LoopTask` by passing your asynchronous routine, an optional execution frequency interval, and a fallback logger instance.

```python
from highrise import LoopTask, setup_logger

async def my_background_job():
    print("Executing interval routine logic...")

# Initialize a task that executes every 10 seconds
task_loop = LoopTask(
    coro_fn=my_background_job,
    seconds=10.0,
    logger=setup_logger("JobManager")
)
```

- `coro_fn`: The asynchronous coroutine function target to run sequentially. Must be a native `async def` function reference.
- `seconds`: The desired interval duration between task cycles in seconds, defaulting to `60.0`.
- `logger`: An optional `logging.Logger` instance. If omitted, the setup defaults to spawning an isolated logger channel bound to the tracking routine's `__name__`.

# Methods

Now we will explain what each method inside `LoopTask` does and what it returns.

## `start()`
Schedules the background loop inside the active event loop if it is not already running. Ignores execution and logs a warning if called while the task is already active.

```python
# Launch the interval execution loop
task_loop.start()
```
* **Returns**: `None`

## `cancel()`
Stops the background task if it is running.

```python
# Stop the interval loop background task gracefully
task_loop.cancel()
```
* **Returns**: `None`

## Properties

### `get_loop_task`
Returns the active background task running your loop.

```python
current_task = task_loop.get_loop_task

if current_task:
    print(f"Task status: {current_task.get_name()}")
```
* **Returns**: `asyncio.Task` if the task is actively running, otherwise `None`.

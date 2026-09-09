# Command Handler

`CommandHandler` loads command files from a directory and dispatches messages into them by name. Any failure in a single command, whether it's a broken file or an exception in a handler, is caught and logged without taking down the bot's main loop.

## The Command object

Every command file defines one module-level `Command` object:

```python
class Command:
    name: str
    handler: Callable[[dict], Coroutine[Any, Any, None]]
    description: str = ""
    required_roles: list[str] = []
```

- `name`: the trigger string used to look this command up on dispatch.
- `handler`: an async function that takes a single `context: dict` argument.
- `description`: optional, for your own reference or a help command.
- `required_roles`: if set, only users holding one of these roles can run the command.

A minimal command file, `commands/ping.py`:

```python
from highrise.tools import Command

async def handle_ping(context: dict):
    bot = context["bot"]
    user = context["user"]
    await bot.highrise.chat(f"Pong, {user.username}!")

command = Command(name="ping", handler=handle_ping)
```

## Loading commands

```python
def load_directory(self, directory: str = "commands") -> None
```

Imports every `.py` file in the given directory (skipping any file starting with `_`), and registers whatever `command: Command` object it finds at module level. Files without one are skipped with a warning, not an error, so one bad file doesn't stop the rest from loading.

`CommandHandler` isn't built into `BaseBot` automatically, you create your own instance and wire it up yourself:

```python
from highrise import BaseBot, CommandHandler

class MyBot(BaseBot):
    def before_start(self):
        self.commands = CommandHandler(self)
        self.commands.load_directory("commands")
```

## Dispatching a command

```python
async def dispatch(self, trigger: str, **context: Any) -> bool
```

Looks up a command by `trigger` and runs its handler if found. `bot` is always injected into `context` automatically, everything else in `context` is exactly whatever you pass in.

```python
async def on_chat(self, user, message):
    handled = await self.commands.dispatch(
        message.command(), # <-- this is trigger
        user=user,
        message=message,
    )
```

**Return value**

- `True` if a command matching `trigger` was found (whether or not it was authorized to run).
- `False` if no command matched `trigger` at all.

## Role-gated commands

If a command sets `required_roles`, dispatch checks the calling user against those roles before running the handler:

```python
command = Command(
    name="kick",
    handler=handle_kick,
    required_roles=["mod"],
)
```

To resolve who's calling, `context` needs either a `user_id` key or a `user` object with an `.id` attribute. If neither is present, the command is treated as unauthorized and silently skipped, dispatch still returns `True` since a matching command existed, but the handler never runs.

## Error handling

Any exception raised inside a handler is caught and logged, it never propagates up to your `on_chat` (or wherever you called `dispatch` from):

```python
try:
    await command.handler(full_context)
except Exception as e:
    self.bot.logger.error(f"Error running command '{trigger}': {e}", exc_info=True)
```

This means one broken command can't crash your bot's event loop, it just logs and moves on.
# The Bot Object

Every bot you write is a subclass of `BaseBot`. This page covers what gets built when you instantiate one, and what you get access to on `self`.

## What lives on self

Once your bot is instantiated, these are available on `self`:

```python
self.highrise       # make requests: chat, whisper, moderation, inventory, and more
self.cached_users   # RoomUsersCache, a live-synced cache of who's in the room
self.awaiter        # Awaiter, for waiting on a specific event with a filter/timeout
self.roles          # Roles, role management, persisted to disk
self.webapi         # WebApi, the HTTP-based web API namespace
```

`self.highrise` is the one you'll use constantly. It's how your bot actually does things, sending messages, moving, moderating, checking wallets. Everything else supports it.

## Read-only properties

The bot also exposes several read-only properties for inspecting its own state:

```python
self.session_metadata    # metadata for the current session, or None before connecting
self.state               # the raw WebSocket connection state
self.credentials         # the room_id/api_token used for this session
self.is_connected        # True if the WebSocket connection is currently open
self.is_paused           # True if event dispatch is currently paused
self.uptime              # seconds since the current connection was established
self.latency             # round-trip time of the last keepalive, in seconds
self.events_processed    # total events processed since connecting
```

These are useful for building things like a `!status` command, or for logging connection health.

## Connection control

Unlike the official SDK that gives you no control over the bot connection, This SDK's `BaseBot` gives you finer control over the connection lifecycle:

### bot.login
```python
await bot.login(room_id: str, api_token: str, auto_reconnect: bool = True)
```

Connects the bot to the given room and starts listening for events.

This is the main entry point, everything (hooks, background loops, reconnect handling) runs from inside this call. It blocks until the bot stops running, so it's usually the last line you call, wrapped in `asyncio.run(...)`.

- `auto_reconnect`: Flag used internally to check if the connection loop should retry automatically after conneciton close or error.

### bot.logout

```python
await bot.logout(hide_logs: bool = False)
```

Gracefully disconnects the bot and disables auto-reconnect.
    
This stops the internal loop of `login()` and allows it to return. 
Use this for a clean, intentional shutdown rather than abruptly 
killing the process.

- `hide_logs`: default `False`, If `True`, suppresses the standard logout progress and success messages in the console logs.

### bot.reconnect
```python
await bot.reconnect()
```
Manually forces the current connection to drop, which triggers the bot's normal reconnect logic to kick in and establish a fresh connection. Useful for recovering from a stuck or laggy state without fully stopping the bot.

### bot.pause
```python
bot.pause()
```

Stops the bot from reacting to incoming events (`chat`, `joins`, `moves`, etc.) without disconnecting. The connection, keepalive, and reconnect logic all keep running underneath, the bot just goes quiet.

### bot.resume
```
bot.resume()
```
Undoes `pause()`, the bot starts reacting to events again.

`pause()` and `resume()` are useful when you want the bot to stay connected but temporarily stop reacting, for example during a maintenance window, without dropping the socket and losing conection to the websocket.

## Only subscribing to events you use

The bot inspects your subclass at startup and checks which hook methods you've actually overridden, like `on_chat` or `on_tip`. It only subscribes to the WebSocket events tied to hooks you implement. If you never override `on_tip`, the bot never asks the server for tip events in the first place. This keeps your bot's connection lean by default, with no configuration needed on your part.

## Running things on a loop

`BaseBot` includes a `loop` decorator for running a function repeatedly for as long as the bot is connected. Apply it in `before_start()`:

```python
from highrise import BaseBot

class MyBot(BaseBot):
    def before_start(self):
        
        @self.loop(seconds=60)
        async def announce():
            await self.highrise.chat("Still here!")
```

### Manually using LoopTask class
The `highrise` module also exposes the `LoopTask` class, which is used internally by the `@self.loop` decorator. You can use it to manually create and control a loop with `.start()` and `.cancel()`:

```python
from highrise import BaseBot, LoopTask

class MyBot(BaseBot):
    async def before_start(self):

        async def announce():
            await self.highrise.chat("Still here!")

        # Create the loop task
        loop_task = LoopTask(coro_fn=announce, seconds=5)

        loop_task.start()        # Start the loop 
        loop_task.cancel()       # Cancel and stop the loop
        loop_task.get_loop_task  # Returns the underlying asyncio task

```

These patterns are useful for things like periodic announcements, scheduled cleanup, or polling external data, without managing your own `asyncio` task.

## What is next ?

Now that you know what's on the bot itself, head to [Events](./events.md) to see how the hook methods that drive it actually work.
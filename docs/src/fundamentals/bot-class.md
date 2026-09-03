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

```python
await bot.login(room_id, api_token, auto_reconnect=True)    # connect and start listening
await bot.logout()                                          # disconnect and disable auto-reconnect
await bot.reconnect()                                       # force a fresh reconnect
bot.pause()                                                 # stop dispatching events without disconnecting
bot.resume()                                                # resume dispatching events
```

`pause()` and `resume()` are useful when you want the bot to stay connected but temporarily stop reacting, for example during a maintenance window, without dropping the socket and losing your place in the room.

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

## What is next

Now that you know what's on the bot itself, head to [Events](./events.md) to see how the hook methods that drive it actually work.
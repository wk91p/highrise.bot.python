# Highrise.bot (Python)

Unofficial Python SDK for [Highrise Virtual Reality](https://highrise.game)

1:1 with the official SDK on every core method, plus a set of tools it doesn't have: live room caching, uptime/latency/event_processed metrics, background loops, a dynamic command system with role-based permissions, local role persistence, auto message splitting, pause/resume, config-driven setup, a public web API client, and pagination support across the board.

> [!NOTE]
> **Coming from the official SDK?** A few event hooks changed shape (`on_moderate`, `on_message`, `on_tip`, `on_user_move`) and `Message` is now a class with helper methods instead of a plain string. See the [Migrating from the official SDK](#migrating-from-the-official-sdk) section below before porting an existing bot.

## Installation

```bash
pip install "git+https://github.com/wk91p/highrise.bot.python.git"
```

## Quick start

```python
import asyncio
from highrise import BaseBot

class MyBot(BaseBot):
    async def on_chat(self, user, message):
        print(f"{user.username}: {message.content}")

if __name__ == "__main__":
    ROOM_ID = "put_your_room_id_here"
    API_TOKEN = "put_your_bot_token_here"

    bot = MyBot()

    try:
        asyncio.run(bot.login(ROOM_ID, API_TOKEN))
    except KeyboardInterrupt:
        print("\nBot stopped manually by user.")
```

## BaseResponse

Every API call returns a response with `.ok` and `.error`. No exceptions to catch.

```python
response = await bot.highrise.tip_user(user_id, "gold_bar_10")

if response.ok:
    print(response.result)
else:
    print(response.error)
```

## Async for-in pagination

Anything that returns a list (`messages`, `rooms`, `items`, `posts`, `grabs`, `conversations`) can be walked page by page, no manual cursor tracking.

```python
response = await bot.highrise.get_messages(conversation_id)

async for page in response:
    for message in page.messages:
        print(message.content)
```

## Roles

Local role management, saved to disk automatically.

```python
bot.roles.add_role("mod", user_id)
bot.roles.has_role(user_id, "mod")
bot.roles.is_mod(user_id)

...
```

## CommandHandler

Drop command files in a folder, each one exposes a `Command` with a name, handler, and optional required roles, and the `CommandHandler` will read the folder recursively and register them.

```python
# ./commands/ping.py
from highrise import Command

async def handler(context: dict) -> None:
    bot = context["bot"]
    user = context["user"]

    await bot.highrise.chat(f"Pong! ({user.username})")

command = Command(
    name="ping",
    handler=handler,
    description="Replies with pong.",
)
```

## Metrics

Uptime and latency tracked automatically.

```python
print(bot.uptime)
print(bot.latency)
print(bot.events_processed)
```

## Validator

Every input is checked before it's sent. Missing values, wrong types, and out-of-range numbers are caught locally instead of failing on the server.

## Configs

One `BotConfig` object controls everything: connection behavior, logging, auto-fetching, roles. Override only what you need, everything else keeps a sane default.

```python
from highrise import BotConfig, LoggerConfig

config = BotConfig(
    logger=LoggerConfig(name="MyBot")
)

bot = MyBot(config)
```

## HttpClient

A small, reusable async HTTP wrapper built on `httpx`. Powers `WebApi`, but usable on its own for any REST API.

```python
from highrise import HttpClient
```

## WebApi

A client for Highrise's public web API, `users`, `rooms`, `posts`, `items`, and `grabs`, separate from the realtime bot API.

```python
response = await bot.webapi.get_user(user_id)

if response.ok:
    print(response.user.username)
```

## Cache system

A narrow, correctness-first cache. Only data the bot exclusively controls (like its own outfit) is cached, anything that can change from outside the bot is always fetched live.

## Awaiter

Wait for a specific event to happen, with filtering, timeout, and multi-result support built in. No manual state tracking, no juggling flags between hooks.

```python
results = await bot.awaiter.chat(
    filter_fn=lambda u, m: u.id == target_id,
    timeout=30,
)

if results:
    user, message = results[0]
```

| Method | Waits for | Returns |
|---|---|---|
| `bot.awaiter.chat()` | Room chat messages | `List[tuple[User, Message]]` |
| `bot.awaiter.whisper()` | Whispered messages | `List[tuple[User, Message]]` |
| `bot.awaiter.direct()` | Direct messages | `List[tuple[str, Optional[Message], Conversation]]` |
| `bot.awaiter.tip()` | Tips | `List[tuple[Sender, Receiver, Item]]` |
| `bot.awaiter.movement()` | User movement | `List[tuple[User, Optional[Position], Optional[AnchorPosition]]]` |
| `bot.awaiter.emote()` | Emotes | `List[tuple[User, str, Receiver]]` |

### Every method accepts:

| Parameter | Default | Description |
|---|---|---|
| `filter_fn` | `None` | Only match events that pass this function |
| `timeout` | `None` | Max seconds to wait; on timeout, returns whatever matched so far instead of raising |
| `max_count` | `1` | Wait for this many matching events before returning |
| `unique` | `False` | Deduplicate matches (e.g. one per user) |

## Public methods

```python
await bot.login(room_id: str, api_token: str, auto_reconnect: bool = True) -> None
```
Connects the bot to the given room and starts listening for events. This is the main entry point, everything (hooks, background loops, reconnect handling) runs from inside this call. It blocks until the bot stops running, so it's usually the last line you call, wrapped in `asyncio.run(...)`.

```python
await bot.logout() -> None
```
Gracefully disconnects the bot and disables auto-reconnect, so `login()` stops its internal loop and returns. Use this for a clean, intentional shutdown rather than just killing the process.

```python
await bot.reconnect() -> None
```
Manually forces the current connection to drop, which triggers the bot's normal reconnect logic to kick in and establish a fresh connection. Useful for recovering from a stuck or laggy state without fully stopping the bot.

```python
bot.pause() -> None
```
Stops the bot from reacting to incoming events (`chat`, `joins`, `moves`, etc.) without disconnecting. The connection, keepalive, and reconnect logic all keep running underneath, the bot just goes quiet.

```python
bot.resume() -> None
```
Undoes `pause()`, the bot starts reacting to events again.

## Decorators

```python
@bot.loop(seconds: float)
```
Registers a function to run automatically on a repeating interval for as long as the bot is connected, useful for things like periodic announcements or status checks. Starts automatically as soon as the bot connects.

```python
class MyBot(BaseBot):
    async def before_start(self) -> None:
        @self.loop(seconds=300.0)
        async def announce():
            await self.highrise.chat("Check out our shop!")
```

## BaseBot properties

```python
bot.is_connected: bool                       # True if the WebSocket connection is currently open
bot.is_paused: bool                          # True if event dispatch is currently paused
bot.state: State | None                      # The raw WebSocket connection state, or None if not connected
bot.uptime: float                            # Seconds since the current connection was established
bot.latency: float | None                    # Round-trip time in seconds of the last keepalive, or None
bot.events_processed: int                    # Total events processed since the current connection was established
bot.credentials: Credentials | None          # The room_id/api_token used for this session, or None before connecting
bot.session_metadata: SessionMetadata | None # The session metadata received once connected, or None before then
```

## Migrating from the official SDK

### 1. `on_moderate`

**Before:**
```python
async def on_moderate(
    self,
    moderator_id: str,
    target_user_id: str,
    moderation_type: Literal["kick", "mute", "unmute", "ban", "unban"],
    duration: int | None,
) -> None:
    """When room moderation event is triggered."""
    pass
```

**After:**
```python
async def on_moderate(
    self,
    moderator_id: str,
    target_user_id: str,
    action: ModerationAction,
) -> None:
    """Called when a moderation action occurs in the room."""
    pass
```

`moderation_type` and `duration` are now bundled into `action: ModerationAction`, which has `.type` and `.duration`.

### 2. `on_message`

**Before:**
```python
async def on_message(
    self, user_id: str, conversation_id: str, is_new_conversation: bool
) -> None:
    """On a inbox message received from a user."""
    pass
```

**After:**
```python
async def on_message(
    self, user_id: str, message: Message | None, conversation: Conversation
) -> None:
    """Called when the bot receives a Direct Message (DM)."""
    pass
```

`conversation_id` and `is_new_conversation` are now bundled into `conversation: Conversation`, which has `.id` and `.is_new_conversation`.

`message` is `None` by default. Fetching the actual message content requires an extra API call, so it's opt-in:

```python
from highrise import BotConfig, AutoFetchConfig

config = BotConfig(auto_fetch=AutoFetchConfig(direct_message=True))
bot = MyBot(config)
```

Enabling this adds one API call and a roughly `300ms` delay before `on_message` fires, this is semi-instant, not truly real-time. If you don't need the message content itself, leave it off.

### 3. `on_tip`

**Before:**
```python
async def on_tip(
    self, sender: User, receiver: User, tip: CurrencyItem | Item
) -> None:
    """On a tip received in the room."""
    pass
```

**After:**
```python
async def on_tip(self, sender: Sender, receiver: Receiver, tip: CurrencyItem) -> None:
    """Called when a tip (currency) is exchanged between two players."""
    pass
```

`sender`/`receiver` are now `Sender`/`Receiver` instead of `User`. `tip` is always `CurrencyItem` now, no longer a `CurrencyItem | Item` union. `CurrencyItem` has `.type` (`"gold"` or `"bubble"`) and `.amount`.

### 4. `on_user_move`

**Before:**
```python
async def on_user_move(
    self, user: User, destination: Position | AnchorPosition
) -> None:
    """On a user moving in the room."""
    pass
```

**After:**
```python
async def on_user_move(
    self,
    user: User,
    position: Position | None,
    anchor: AnchorPosition | None,
) -> None:
    """Called when a user moves or changes position in the room."""
    pass
```

`destination` is now split into two separate optional parameters, `position` and `anchor`, exactly one of which will be set depending on the move type.

### 5. `Message`

Every `Message` (`chat`, `whisper`, or `direct`) is now a standalone class with built-in helpers instead of a plain string:

```python
message.content        # the actual raw string
message.command()      # first word, e.g. "!kick"
message.args()         # remaining words as a list
message.args(0)        # a specific argument by index
message.mentions()     # all @username mentions, without the @
message.mentions(0)    # a specific mention by index
```
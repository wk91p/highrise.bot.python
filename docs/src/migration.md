# Migrating from the Official SDK

`self.highrise` maps directly onto the official API for almost everything, but a few things changed shape to fix real inconsistencies, or were split apart to make the API less error-prone. This page covers every difference you'll hit porting an existing bot.

## 1. `on_moderate`

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

## 2. `on_message`

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

Enabling this adds one API call and a roughly `~150ms` delay before `on_message` fires, this is semi-instant, not truly real-time. If you don't need the message content itself, leave it off.

## 3. `on_tip`

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

## 4. `on_user_move`

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

## 5. `Message`

Every `Message` (`chat`, `whisper`, or `direct`) is now a standalone class with built-in helpers instead of a plain string:

```python
message.content        # the actual raw string
message.command()      # first word, e.g. "!kick"
message.args()         # remaining words as a list
message.args(0)        # a specific argument by index
message.mentions()     # all @username mentions, without the @
message.mentions(0)    # a specific mention by index
```

See [The Message Class](./message-class.md) for the full breakdown.

## 6. Bot-level setup (`__init__`)

The official SDK's `BaseBot` has no `__init__`, just hooks, with `highrise`/`webapi` attached once before the bot connects. This SDK's `BaseBot.__init__` does real setup at construction time (`self.highrise`, `self.webapi`, `self.roles`, `self.cached_users`, etc.), so overriding `__init__` here is not the same as it was there.

**Before (official SDK):**
```python
class MyBot(BaseBot):
    def __init__(self):
        self.my_setting = "something"
```

**After (this SDK):**

`before_start()` runs once at `login()`, right before the bot connects, with the bot already fully constructed, so it's the safer place for your own setup and there's nothing to remember.

```python
class MyBot(BaseBot):
    async def before_start(self) -> None:
        self.my_setting = "something"
```

If you do override `__init__` here, call `super().__init__()` first or the bot will be missing everything it needs to run.

```python
class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.my_setting = "something"
```

## 7. `send_message` / `send_message_bulk` split into three dedicated methods

The official SDK has one generic `send_message(conversation_id, content, message_type, room_id, world_id)` plus a matching `send_message_bulk(user_ids, ...)`, where `message_type` decides whether it's a plain text message or an invite, and `room_id`/`world_id` only apply when it is.

**Before:**
```python
await bot.highrise.send_message(conversation_id, "hello")
await bot.highrise.send_message(conversation_id, "", message_type="invite", room_id=room_id)
await bot.highrise.send_message_bulk(user_ids, "hello")
```

**After:**
```python
await bot.highrise.send_message(conversation_id, "hello")
await bot.highrise.send_room_invite(conversation_id, room_id)
await bot.highrise.send_world_invite(conversation_id, world_id)

await bot.highrise.send_message(user_ids, "hello")        # bulk, up to 100 users
await bot.highrise.send_room_invite(user_ids, room_id)    # bulk, up to 100 users
await bot.highrise.send_world_invite(user_ids, world_id)  # bulk, up to 100 users
```

```python
async def send_message(recipient: str | list[str], content: str) -> AcknowledgementResponse | list[AcknowledgementResponse]
async def send_room_invite(recipient: str | list[str], room_id: str) -> AcknowledgementResponse
async def send_world_invite(recipient: str | list[str], world_id: str) -> AcknowledgementResponse
```

`send_message`, `send_room_invite`, and `send_world_invite` are now three separate methods instead of one method with an optional `message_type` flag and unused parameters depending on that flag. Each has its own required arguments, so you can't call `send_message` with a `room_id` that quietly gets ignored, or forget `world_id` on an invite and only find out at runtime. Bulk sending is no longer a separate method either, every one of the three accepts a single recipient or a list of up to `100`, and the right request is built automatically.

`send_message` also auto-splits content over `2000` characters into multiple messages, sent `400ms` apart, which the official SDK does not do.

- See [`send_message`](./api-reference/direct-messages.md#send_message) for more detailes.

## What is next?

Head to [API Reference](../api-reference/chat.md) for the full method-by-method breakdown of `self.highrise`.
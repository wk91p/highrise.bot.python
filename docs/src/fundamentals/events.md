# Events

Your bot reacts to what happens in the room by overriding hook methods from `BaseBot`. Every hook is an async no-op by default, so you only implement the ones your bot actually needs.

## Lifecycle hooks

### `before_start()`

```python
async def before_start(self) -> None
```

Fires once before the bot attempts to connect, before any login or reconnect attempt. No parameters.

```python
async def before_start(self):
    print("Booting up...")
```

### `on_start(session_metadata)`

```python
async def on_start(self, session_metadata: SessionMetadata) -> None
```

Fires once the bot has successfully connected. Use this for setup that depends on being connected, like fetching initial room state.

```python
class SessionMetadata:
    user_id: str
    room_info: RoomInfo
    rate_limits: dict[str, tuple[int, float]]
    connection_id: str
    sdk_version: str | None
```

```python
class RoomInfo:
    owner_id: str
    room_name: str
```

```python
async def on_start(self, session_metadata: SessionMetadata):
    print(f"Connected. Room owner: {session_metadata.room_info.owner_id}")
```

## Chat and messaging

### `on_chat(user, message)`

```python
async def on_chat(self, user: User, message: Message) -> None
```

Fires when a user sends a message in the room.

```python
class User:
    id: str
    username: str
```

```python
class Message:
    content: str
```

`Message` does more than just hold text, it also parses commands, arguments, and mentions out of `content`. That's covered in full on [The Message Class](./message-class.md), a couple pages ahead.

```python
async def on_chat(self, user: User, message: Message):
    if message.content == "!ping":
        await self.highrise.chat("Pong!")
```

### `on_whisper(user, message)`

```python
async def on_whisper(self, user: User, message: Message) -> None
```

Fires when the bot receives a private whisper. Same `User` and `Message` shapes as `on_chat`.

```python
async def on_whisper(self, user: User, message: Message):
    await self.highrise.whisper(user.id, "I got your whisper!")
```

### `on_message(user_id, message, conversation)`

```python
async def on_message(self, user_id: str, message: Message | None, conversation: Conversation) -> None
```

Fires when the bot receives a direct message. `message` is `None` unless you enable `AutoFetchConfig(direct_message=True)` in your `BotConfig`, since fetching the actual content costs an extra API call.

```python
class Conversation:
    id: str
    is_new_conversation: bool
```

```python
from highrise import BaseBot, BotConfig, AutoFetchConfig

config = BotConfig(
    auto_fetch=AutoFetchConfig(direct_message=True)
)

bot = MyBot(config)
```

```python
async def on_message(self, user_id: str, message: Message, conversation: Conversation):
    if message:
        print(f"DM from {user_id}: {message.content}")
```

### `on_channel(bot_id, message, tags)`

```python
async def on_channel(self, bot_id: str, message: str, tags: list[str]) -> None
```

Fires when a message is received on the hidden channel, a low-level bot-to-bot communication layer. `bot_id` and `message` are plain strings, `tags` a plain list of strings. A bot can't see its own messages here.

```python
async def on_channel(self, bot_id, message, tags):
    print(f"Channel message from {bot_id}: {message}")
```

## Presence and movement

### `on_user_join(user, position)`

```python
async def on_user_join(self, user: User, position: Position) -> None
```

Fires when a user enters the room.

```python
class Position:
    x: float
    y: float
    z: float
    facing: Facing = "FrontRight"   # "FrontRight" | "FrontLeft" | "BackRight" | "BackLeft"
```

- `x`, `y`, `z` - the player's coordinates in the room.
- `facing` - which direction the player is facing, one of `"FrontRight"`, `"FrontLeft"`, `"BackRight"`, `"BackLeft"`. Defaults to `"FrontRight"`.

`Position` also has three helper methods:

- `distance_to(other: Position)` - returns the 3D distance to another `Position`.
- `offset(dx=0, dy=0, dz=0)` - returns a new `Position` shifted by the given amounts, keeping the same `facing`.
- `as_tuple()` - returns `(x, y, z)` as a plain tuple, dropping `facing`.

```python
async def on_user_join(self, user, position):
    await self.highrise.chat(f"Welcome, {user.username}!")
```

### `on_user_leave(user)`

```python
async def on_user_leave(self, user: User) -> None
```

Fires when a user leaves the room. Same `User` shape as `on_chat`.

```python
async def on_user_leave(self, user):
    print(f"{user.username} left")
```

### `on_user_move(user, position, anchor)`

```python
async def on_user_move(self, user: User, position: Position | None, anchor: AnchorPosition | None) -> None
```

Fires when a user moves or changes position in the room. Either `position` or `anchor` will be set, the other one will be `None`, depending on whether the user moved freely or snapped to an anchor point.

```python
class AnchorPosition:
    entity_id: str   # the furniture id inside the room (can change if the furniture is removed)
    anchor_ix: int    # sitting position index, usually 0 or 1
```

```python
async def on_user_move(self, user, position, anchor):
    if position:
        print(f"{user.username} moved to {position.x}, {position.y}, {position.z}")
```

### `on_emote(user, emote_id, receiver)`

```python
async def on_emote(self, user: User, emote_id: str, receiver: Receiver) -> None
```

Fires when a user performs an emote. `emote_id` is a plain string.

```python
class Receiver(User):   # extends User
```

```python
async def on_emote(self, user, emote_id, receiver):
    print(f"{user.username} used emote {emote_id}")
```

## Currency and moderation

### `on_tip(sender, receiver, tip)`

```python
async def on_tip(self, sender: Sender, receiver: Receiver, tip: CurrencyItem) -> None
```

Fires when a tip (currency) is exchanged between two players, the bot too.

```python
class Sender(User):     # extends User
```

```python
class Receiver(User):   # extends User
```

```python
class CurrencyItem:
    type: str    # e.g. "gold", "bubbles"
    amount: int
```

```python
async def on_tip(self, sender, receiver, tip):
    await self.highrise.chat(f"{sender.username} tipped {tip.amount}!")
```

### `on_moderate(moderator_id, target_user_id, action)`

```python
async def on_moderate(self, moderator_id: str, target_user_id: str, action: ModerationAction) -> None
```

Fires when a moderation action occurs in the room, such as a kick or ban. `moderator_id` and `target_user_id` are plain strings.

```python
class ModerationAction:
    type: ModerationType   # "kick" | "mute" | "ban" | "unban" | "unmute"
    duration: int | None
```

```python
async def on_moderate(self, moderator_id, target_user_id, action):
    await self.highrise.chat(f"{moderator_id} performed {action.type} on {target_user_id}")
```

### `on_voice_change(users, seconds_left)`

```python
async def on_voice_change(self, users: list[Any], seconds_left: int) -> None
```

Fires when there's an update to the room's voice status. `seconds_left` is a plain int. Deprecated as of update `4.25.3`, still documented here since it may still fire, just shouldn't be relied on in new bots.

```python
async def on_voice_change(self, users, seconds_left):
    print(f"Voice update, {seconds_left}s left")
```

## Only what you use

The bot only subscribes to the WebSocket events tied to hooks you actually override. If your subclass never defines `on_tip`, the bot never asks the server for tip events at all. There's nothing to configure, it's automatic based on which methods you implement.

## What is next?

Head to [Requests and Responses](./requests-responses.md) to see how `self.highrise`/`self.webapi` methods return structured, ready-to-use response objects.

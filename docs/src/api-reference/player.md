# Player

Methods for interacting with players directly: emotes, movement, moderation, and tipping.

## send_emote()

```python
async def send_emote(self, emote_id: str, target_user_id: str | None = None) -> AcknowledgementResponse
```

Performs an emote. If `target_user_id` is omitted, the bot performs the emote on itself.

```python
await self.highrise.send_emote("emote-yes")

# directed at another user
await self.highrise.send_emote("emote-hug", target_user_id=user.id)
```

## walk_to()

```python
async def walk_to(self, destination: Position | AnchorPosition) -> AcknowledgementResponse
```

Moves the bot to a floor position or to an anchor point in the room.

```python
await self.highrise.walk_to(Position(x=5.0, y=0.0, z=3.0, facing="FrontRight"))
```

## teleport()

```python
async def teleport(self, user_id: str, destination: Position) -> AcknowledgementResponse
```

Teleports a user to the given floor position.

```python
await self.highrise.teleport(user.id, Position(x=0.0, y=0.0, z=0.0, facing="FrontLeft"))
```

## moderate_room()

```python
async def moderate_room(self, user_id: str, action: ModerationType, action_length: int | None = None) -> AcknowledgementResponse
```

Applies a moderation action to a user in the room.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `user_id` | `str` | The user to moderate. |
| `action` | `ModerationType` | One of `"kick"`, `"ban"`, `"unban"`, `"mute"`. |
| `action_length` | `int \| None` | Duration in seconds, for `ban`/`mute`. Must be between 60 seconds and 60 years. |

You'll usually reach for the shortcut methods below instead of calling this directly.

## Moderation shortcuts

All of these wrap `moderate_room()` internally:

```python
await self.highrise.kick(user.id)
await self.highrise.ban(user.id, action_length=24 * 3600)   # defaults to 1 day
await self.highrise.unban(user.id)
await self.highrise.mute(user.id, action_length=3600)  # defaults to 1 hour
await self.highrise.unmute(user.id)
```

## tip_user()

```python
async def tip_user(self, user_id: str, tip: TipType) -> TipUserResponse
```

Sends a single tip in one of the valid gold bar tiers: `"gold_bar_1"`, `"gold_bar_5"`, `"gold_bar_10"`, `"gold_bar_50"`, `"gold_bar_100"`, `"gold_bar_500"`, `"gold_bar_1k"`, `"gold_bar_5000"`, `"gold_bar_10k"`.

```python
response = await self.highrise.tip_user(user.id, "gold_bar_5")

if response.has_error():
    self.logger.warning(f"Tip failed: {response.error}")
```

### TipUserResponse body
Response for tipping a user.

```python
class TipUserResponse(BaseResponse):
    result: TipUserResult | None
```

```python
TipUserResult = Literal["success", "insufficient_funds"]
```
## split_tip_user()

```python
async def split_tip_user(self, user_id: str, amount: int) -> list[TipUserResponse]
```

Tips a user an arbitrary gold amount. Since tips only come in fixed tiers, this breaks the amount down into valid tiers and sends them one at a time, `400ms` apart. If a tip in the sequence fails, sending stops there, the returned list contains every tip that succeeded plus the one that failed as its last entry.

```python
responses = await self.highrise.split_tip_user(user.id, 37)

# check the last entry if stopped early using -1 index
if responses[-1].has_error():
    self.logger.warning(f"Split tip stopped early: {responses[-1].error}")
```

`list[TipUserResponse]` check [`TipUserResponse`](#tipuserresponse-body) body.

## get_user_outfit()

```python
async def get_user_outfit(self, user_id: str) -> GetUserOutfitResponse
```

Fetches a user's current outfit.

```python
outfit = await self.highrise.get_user_outfit(user.id)
```

### GetUserOutfitResponse body
Response for fetching a user's outfit.

```python
class GetUserOutfitResponse(BaseResponse):
    outfit: list[OutfitItem]
    count: int
```
`GetUserOutfitResponse` also has two built-in methods

- `has_item(self, item_id: str) -> bool` - Checks whether the outfit contains an item with the given id.
- `find_item(self, item_id: str) -> OutfitItem | None` - Finds the item with the given id in the outfit, or `None` if not present.

### OutfitItem
A single item in a user's outfit.

```python
class OutfitItem:
    type: str
    amount: int
    id: str
    account_bound: bool
    active_palette: int
```

## move_user_to_room()

```python
async def move_user_to_room(self, user_id: str, room_id: str) -> AcknowledgementResponse
```

Moves a user to a different room. Only works if the bot belongs to that room's owner, or the bot has designer privileges there.

```python
await self.highrise.move_user_to_room(user.id, other_room_id)
```
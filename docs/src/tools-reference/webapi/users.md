# Users

Public user lookups via the web API.

## get_user()

```python
async def get_user(self, identifier: str) -> GetPublicUserResponse
```

Fetches a user's public profile by ID or username.

```python
response = await self.webapi.get_user("user_123")

if response.has_error():
    self.logger.warning(f"Lookup failed: {response.error}")
```

## GetPublicUserResponse body
Response for `get_user()`.

`response.user` is a `PublicUser`, or `None` if the request failed.

```python
class GetPublicUserResponse(BaseResponse):
    user: PublicUser | None
```

### PublicUser
A user's public profile, as returned by `get_user()`.

```python
class PublicUser:
    user_id: str
    username: str
    outfit: list[WebOutfitItem]
    bio: str
    joined_at: datetime
    last_online_in: datetime | None
    num_followers: int
    num_following: int
    num_friends: int
    active_room: ActiveRoomInfo | None
    country_code: str
    crew: Crew | None
    voice_enabled: bool
    discord_id: str | None
    icon_url: str | None
    avatar_url: str | None
    avatar_svg: str | None
```
### WebOutfitItem
A single outfit item as returned by the public web API. Distinct shape from the WebSocket API's OutfitItem.

```python
class WebOutfitItem:
    item_id: str
    name: str
    rarity: Rarity
    active_palette: int
    parts: list[tuple[str str]]
    colors: WebOutfitItemColors | None
```

### WebOutfitItemColors
Color/palette data for a single web-API outfit item.

```python
class WebOutfitItemColors:
    dependent_colors: Sequence[str]
    palettes: Sequence[list]
    linked_colors: str
```

### Rarity

`Rarity` values, from most to least common:

```python
class Rarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"
    NONE = "none_"
```

## External References

### `datetime`
For tracking users timestamps, see the shared [`datetime` reference](../../references.md#datetime).
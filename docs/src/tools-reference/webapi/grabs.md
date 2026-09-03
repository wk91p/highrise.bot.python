# Grabs

Public lookups for grabs (Highrise's reward/loot events) via the web API.

## get_grab()

```python
async def get_grab(self, grab_id: str) -> GetPublicGrabResponse
```

Fetches a single grab by ID.

```python
response = await self.webapi.get_grab("grab_123")
```

### GetPublicGrabResponse body
Response for `get_grab()`

```python
class GetPublicGrabResponse(BaseResponse):
    grab: Grab | None
```

### Grab:
A Grab event, as returned by `get_grab()`

```python
class Grab:
    grab_id: str
    title: str
    description: str
    background_color: tuple
    banner_img_url: str
    starts_at: datetime | None
    expires_at: datetime | None
    rewards: list[Reward]
    primary_img_url: str | None
    secondary_img_url: str | None
    costs: list[Reward]
    kompu_rewards: list[Reward]
    is_tradable: bool
    limited_time_kompu: LimitedKompuReward | None
    progress_reward: ProgressReward | None
```

### LimitedKompuReward
a time-boxed set of rewards

```python
class LimitedKompuReward:
    expires_at: datetime | None
    rewards: list[Reward]
```

### ProgressReward
a reward unlocked at a progress threshold

```python
class ProgressReward:
    rewards_at: int
    rewards: list[Reward]
```

### Reward
A single reward or cost entry within a Grab.

```python
class Reward:
    category: LegacyRewardCategory
    amount: int
    reward_id: str
    item_id: str | None
    account_bound: bool
    metadata: ItemMetadata | None
```

### LegacyRewardCategory
Currency/reward types a Reward can grant.

```python
class LegacyRewardCategory(str, Enum):
    POPS = "pops"
    GEMS = "gems"
    OUTFIT = "outfit"
    GACHA_TOKENS = "gacha_tokens"
    FURNITURE = "furniture"
    COLLECTIBLE = "collectible"
    LUCKY_TOKENS = "lucky_tokens"
    EVENT_TICKETS = "event_tickets"
    EMOTE = "emote"
    GIFT_BOX = "gift_box"
    ENERGY = "energy"
    VIP_DAYS = "vip_days"
    CHIPS = "chips"
    PROMO_TOKENS = "promo_tokens"
    SKYPASS_STARS = "skypass_stars"
    ROOM_BOOST_TOKENS = "room_boost_tokens"
    ROOM_VOICE_TOKENS = "room_voice_tokens"
    POCKET_COINS = "pocket_coins"
    CASH = "cash"
    CUSTOM_CURRENCY = "custom_currency"
    PET = "pet"
```

### ItemMetadata
Non-fungible item metadata attached to a Reward, if applicable.

```python
class ItemMetadata:
    nfi_metadata: NFIItemMetadata | None
    nfi_template_metadata: NFITemplateMetadata | None
```

### NFIItemMetadata
Identifies a specific numbered instance of a non-fungible item.

```python
class NFIItemMetadata:
    item_number: int
    stack_id: str
```

### NFITemplateMetadata
Allocation rules for a non-fungible item template.

```python
class NFITemplateMetadata:
    strategy: NFIStrategy
    total_amount: int | None = None
```

### NFIStrategy
How a non-fungible item's numbered instances are allocated.

```python
class NFIStrategy(str, Enum):
    SEQUENTIAL = "sequential"
    TOTAL_DEFINED = "total_defined"
    POOL = "pool"
```

## get_grabs()

```python
async def get_grabs(
    self,
    starts_after: str | None = None,
    ends_before: str | None = None,
    sort_order: SortOptions = "desc",
    limit: int = 20,
    title: str | None = None,
) -> GetPublicGrabsResponse
```

Fetches a filtered, ordered, paginated list of grabs.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `starts_after` / `ends_before` | `str \| None` | Pagination cursors. |
| `sort_order` | `"desc" \| "asc"` | Sort direction. Defaults to `"desc"`. |
| `limit` | `int` | Page size, 1 to 100. Defaults to `20`. |
| `title` | `str \| None` | Filter by grab title. |

```python
response = await self.webapi.get_grabs(title="Summer Event", limit=50)
```

### GetPublicGrabsResponse body
Response for `get_grabs()` (list method).

```python
class GetPublicGrabsResponse(BaseResponse):
    grabs: list[Grab]
    total: int
    first_id: str
    last_id: str
```
see [`Grab`](#grab)

## Pagination

```python
# manually, via next_page_fn
response = await self.webapi.get_grabs(limit=20)
while response.next_page_fn:
    response = await response.next_page_fn()

# or with async for
async for page in self.webapi.get_grabs(limit=20):
    for grab in page.grabs:
        print(grab.title)
```

## External References

### `datetime`
For tracking grabs timestamps, see the shared [`datetime` reference](../../references.md#datetime).
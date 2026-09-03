# Items

Public item search and lookups via the web API.

## search_items()

```python
async def search_items(self, query: str, limit: int | None = None, skip: int | None = None) -> SearchItemsResponse
```

Searches for items by a query

**Parameters**

| Name | Type | Description |
|---|---|---|
| `query` | `str` | The search text. Required. |
| `limit` | `int \| None` | Max results per page, between 1 and 100. |
| `skip` | `int \| None` | Offset for pagination, between 0 and 100,000. Omit to start from the beginning. |

```python
response = await self.webapi.search_items("crown")
```

Page sizes aren't constant for this endpoint. When iterating, always check `if page.items:` before indexing, since the last page yielded may come back empty:

```python
async for page in self.webapi.search_items("crown"):
    if not page.items:
        break
    for item in page.items:
        print(item.item_name)
```

### SearchItemsResponse body
Response for `search_items()` (list method).

```python
class SearchItemsResponse(BaseResponse):
    items: list[ItemBasic]
```

see [`ItemBasic`](#itembasic)

## get_item()

```python
async def get_item(self, item_id: str) -> GetPublicItemResponse
```

Fetches a single item, along with related items and current storefront listings.

```python
response = await self.webapi.get_item("item_123")
```

### GetPublicItemResponse body
Response for `get_item()`.

```python
class GetPublicItemResponse(BaseResponse):
    item: Item | None
    related_items: RelatedItems | None
    storefront_listings: StorefrontListings | None
```

### Item
A full item, as returned by `get_item()`.

`Item` extends the base item fields (shared with [`ItemBasic`](#itembasic), see below) with:

```python
class Item:
    # ... ItemBasic fields

    acquisition_cost: int | None
    acquisition_amount: int | None
    acquisition_currency: str | None
```

### RelatedItems
Items related to this one.

```python
class RelatedItems:
    affiliations: list[Affiliation]
    items: list[RelatedItem]
```

### Affiliation
A collection/event an item or grab is associated with.

```python
class Affiliation:
    id: str
    title: str
    type: str
    event_type: str | None
```

### RelatedItem
A lightweight reference to another item, used in [`RelatedItems`](#relateditems).

```python
class RelatedItem:
    item_id: str
    disp_name: str
    rarity: Rarity
```

### StorefrontListings
Active sellers for an item.

```python
class StorefrontListings:
    sellers: list[Seller]
    pages: int
    total: int
```

### Sellers
A user currently selling an item on the storefront.

```python
class Seller:
    user_id: str
    username: str
    outfit: list[WebOutfitItem]
    last_connected_at: datetime | None
```

### WebOutfitItem

check [`WebOutfitItem`](./users.md#weboutfititem)

## get_items()

```python
async def get_items(
    self,
    starts_after: str | None,
    ends_before: str | None,
    sort_order: SortOptions = "desc",
    limit: int = 20,
    rarity: str | None,
    item_name: str | None,
    category: ItemCategory | None,
) -> GetPublicItemsResponse
```

Fetches a filtered, ordered, paginated list of items.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `starts_after` / `ends_before` | `str \| None` | Pagination cursors. |
| `sort_order` | `"desc" \| "asc"` | Sort direction. Defaults to `"desc"`. |
| `limit` | `int` | Page size, 1 to 100. Defaults to `20`. |
| `rarity` | `str \| None` | Comma-separated rarities to filter by, e.g. `"rare,epic,legendary"`. |
| `item_name` | `str \| None` | Filter by item name. |
| `category` | `ItemCategory \| None` | Filter by category. |

```python
response = await self.webapi.get_items(rarity="epic,legendary", limit=50)
```

### GetPublicItemsResponse body
Response for `get_items()` (list method).

```python
class GetPublicItemsResponse(BaseResponse):
    items: list[ItemBasic]
    total: int
    first_id: str
    last_id: str
```

### ItemBasic
A single item, as returned by `get_items()`

`ItemBasic` (used in [`search_items()`](#search_items) and [`get_items()`](#get_items) results) and `Item` extend it (used in [`get_item()`](#get_item)) share this shape:

```python
class ItemBasic:
    item_id: str
    item_name: str
    category: ItemCategory | None
    color_linked_categories: list
    color_palettes: list
    created_at: datetime | None
    description_key: str | None
    gems_sale_price: int | None
    inspired_by: list[str]
    is_purchasable: bool
    is_tradable: bool
    image_url: str | None
    icon_url: str | None
    link_ids: list[str]
    m_dependent_colors: list[tuple[ItemCategory, int, int]]
    m_front_skin_part_list: list[SkinPart]
    m_back_skin_part_list: list[SkinPart]
    m_hidden_skin_parts: set
    pops_sale_price: int | None
    rarity: Rarity
    release_date: datetime | None
```

### ItemCategory
Every equippable item category on Highrise.

```python
class ItemCategory(str, Enum):
    BAG = "bag"
    BLUSH = "blush"
    BODY = "body"
    DRESS = "dress"
    EARRINGS = "earrings"
    EMOTE = "emote"
    EYE = "eye"
    EYEBROW = "eyebrow"
    FACE_HAIR = "face_hair"
    FISHING_ROD = "fishing_rod"
    FRECKLE = "freckle"
    GLASSES = "glasses"
    GLOVES = "gloves"
    HAIR_BACK = "hair_back"
    HAIR_FRONT = "hair_front"
    HANDBAG = "handbag"
    HAT = "hat"
    JACKET = "jacket"
    LASHES = "lashes"
    MOLE = "mole"
    MOUTH = "mouth"
    NECKLACE = "necklace"
    NOSE = "nose"
    PANTS = "pants"
    SHIRT = "shirt"
    SHOES = "shoes"
    SHORTS = "shorts"
    SKIRT = "skirt"
    WATCH = "watch"
    FULLSUIT = "fullsuit"
    SOCK = "sock"
    TATTOO = "tattoo"
    ROD = "rod"
    AURA = "aura"
```

### SkinPart
A single skin part attachment on an item.

```python
class SkinPart:
    bone: str
    slot: str
    image_file: str
    attachment_name: str | None
    has_remote_render_layer: bool | None
```

## Pagination

Both [`search_items()`](#search_items) and [`get_items()`](#get_items) support pagination two ways:

```python
# manually, via next_page_fn
response = await self.webapi.get_items(limit=20)
while response.next_page_fn:
    response = await response.next_page_fn()

# or with async for
async for page in self.webapi.get_items(limit=20):
    for item in page.items:
        print(item.item_name)
```

## External References

### `datetime`
For tracking items timestamps, see the shared [`datetime` reference](../../references.md#datetime).
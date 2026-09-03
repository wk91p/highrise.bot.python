# Rooms

Public room lookups via the web API, single room or filtered/paginated lists.

## get_room()

```python
async def get_room(self, room_id: str) -> GetPublicRoomResponse
```

Fetches a single room by ID.

```python
response = await self.webapi.get_room("room_123")

if response.has_error():
    self.logger.warning(f"Lookup failed: {response.error}")
```

### GetPublicRoomResponse body
Response for `get_room()`

```python
class GetPublicRoomResponse(BaseResponse):
    room: PublicRoom | None
```

### PublicRoom
A room's public data, as returned by `get_room()`. Extends [`PublicRoomBasic`](#publicroombasic) with fields only present on the single-room endpoint.

```python
class PublicRoom:
    # ... PublicRoomBasic fields

    num_connected: int
    crew_id: str | None
    bots: str | None
    indicators: str | None
    thumbnail_url: str | None
    banner_url: str | None
```

## get_rooms()

```python
async def get_rooms(
    self,
    starts_after: str | None = None,
    ends_before: str | None = None,
    room_name: str | None = None,
    owner_id: str | None = None,
    sort_order: SortOptions = "desc",
    limit: int = 20,
) -> GetPublicRoomsResponse
```

Fetches a list of rooms, filtered, ordered, and paginated.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `starts_after` | `str \| None` | Cursor for pagination, fetch rooms after this ID. |
| `ends_before` | `str \| None` | Cursor for pagination, fetch rooms before this ID. |
| `room_name` | `str \| None` | Filter by room name. |
| `owner_id` | `str \| None` | Filter by owner. |
| `sort_order` | `"desc" \| "asc"` | Sort direction. Defaults to `"desc"`. |
| `limit` | `int` | Page size, between 1 and 100. Defaults to `20`. |

```python
response = await self.webapi.get_rooms(room_name="party", limit=50)
```

### GetPublicRoomsResponse body
Response for `get_rooms()` (list method)

```python
class GetPublicRoomsResponse(BaseResponse):
    rooms: list[PublicRoomBasic]
    total: int
    first_id: str
    last_id: str
```

### PublicRoomBasic
a lighter version of [`PublicRoom`](#publicroom) used for list results:

```python
class PublicRoomBasic:
    room_id: str
    disp_name: str
    description: str
    category: str
    owner_id: str
    created_at: datetime | None
    access_policy: str
    locale: list[str]
    is_home_room: bool
    designer_ids: list[str]
    moderator_ids: list[str]
```

### Pagination

When a full page comes back, you can keep pulling more results two ways:

```python
# manually, via next_page_fn
response = await self.webapi.get_rooms(limit=20)
while response.next_page_fn:
    response = await response.next_page_fn()

# or with async for
async for page in self.webapi.get_rooms(limit=20):
    for room in page.rooms:
        print(room.disp_name)
```

## External References

### `datetime`
For tracking rooms timestamps, see the shared [`datetime` reference](../../references.md#datetime).
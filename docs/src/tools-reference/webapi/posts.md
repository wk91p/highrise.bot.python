# Posts

Public post lookups via the web API.

## get_post()

```python
async def get_post(self, post_id: str) -> GetPublicPostResponse
```

Fetches a single post by ID.

```python
response = await self.webapi.get_post("post_123")
```

### GetPublicPostResponse body
Response for `get_post()`

```python
class GetPublicPostResponse(BaseResponse):
    post: PublicPost | None
```

### PublicPost
A post's public data, as returned by `get_post()`. Extends [`PublicPostBasic`](#publicpostbasic) with comments, only present on the single-post endpoint.

```python
class PublicPost:
    # ... PublicPostBasic fields

    comments: list[Comment]
```

### Comment
Single post comment

```python
class Comment:
    id: str
    content: str
    post_id: str
    author_id: str
    author_name: str
    num_likes: int
```

### PostBody:
A post's text content plus any attached inventory items.

```python
class PostBody:
    text: str
    inventory: PostInventory
```


### PostInventory
The set of items attached to a post.

```python
class PostInventory:
    items: list[PostItem]
```

### PostItem
Single post item

```python
class PostItem:
    item_id: str
    active_palette: int
    account_bound: bool
```

## get_posts()

```python
async def get_posts(
    self,
    starts_after: str | None = None,
    ends_before: str | None = None,
    sort_order: SortOptions = "desc",
    limit: int = 20,
    author_id: str | None = None,
) -> GetPublicPostsResponse
```

Fetches a filtered, ordered, paginated list of posts.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `starts_after` / `ends_before` | `str \| None` | Pagination cursors. |
| `sort_order` | `"desc" \| "asc"` | Sort direction. Defaults to `"desc"`. |
| `limit` | `int` | Page size, 1 to 100. Defaults to `20`. |
| `author_id` | `str \| None` | Filter by post author. |

```python
response = await self.webapi.get_posts(author_id="user_123", limit=50)
```

### GetPublicPostsResponse body
Response for `get_posts()` (list method)

```python
class GetPublicPostsResponse(BaseResponse):
    posts: list[PublicPostBasic]
    total: int
    first_id: str
    last_id: str
```

### PublicPostBasic
A lighter version of [`PublicPost`](#publicpost), as returned by `get_posts` (list method)


```python
class PublicPostBasic:
    post_id: str
    author_id: str
    created_at: datetime
    file_key: str | None
    type: str
    visibility: str
    num_comments: int
    num_likes: int
    num_reposts: int
    body: PostBody
    caption: str | None
    featured_user_ids: list[str]
```

## Pagination

```python
# manually, via next_page_fn
response = await self.webapi.get_posts(limit=20)
while response.next_page_fn:
    response = await response.next_page_fn()

# or with async for
async for page in self.webapi.get_posts(limit=20):
    for post in page.posts:
        print(post.post_id)
```

## External References

### `datetime`
For tracking posts timestamps, see the shared [`datetime` reference](../../references.md#datetime).
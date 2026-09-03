# Outfit

Methods for managing the bot's own outfit. These only affect the bot itself, not other users in the room.

## get_my_outfit()

```python
async def get_my_outfit(self) -> GetUserOutfitResponse
```

Fetches the bot's current outfit. Cached after the first successful call, so repeated calls don't re-fetch unless the outfit changes.

```python
outfit = await self.highrise.get_my_outfit()

for item in outfit.outfit:
    print(item.id)
```

### GetUserOutfitResponse body

The `get_my_outfit()` method uses `get_user_outfit()` method under the hood, check [`GetUserOutfitResponse`](./player.md#getuseroutfitresponse-body) in the player page for response type.

## set_outfit()

```python
async def set_outfit(self, outfit: list[OutfitItem] | None = None) -> AcknowledgementResponse
```

Sets the bot's full outfit. Pass a list of `OutfitItem`, or omit it to reset to the SDK's default outfit. The base `body-flesh` item is added automatically if it's missing from the list, so you don't have to remember it yourself.

```python
await self.highrise.set_outfit([
    OutfitItem(
        type="clothing", 
        amount=1, 
        id="shirt-blue", 
        account_bound=False, 
        active_palette=0
    )
])
```

## change_item_color()

```python
async def change_item_color(self, item_id: str, palette_index: int) -> AcknowledgementResponse
```

Changes the active color palette of an item already in the bot's outfit. Fetches the current outfit, finds the item, and re-applies the full outfit with just that item's palette changed.

```python
await self.highrise.change_item_color("shirt-blue", palette_index=2)
```

Returns an error response if the item isn't currently in the outfit.

## add_outfit_item()

```python
async def add_outfit_item(self, item: OutfitItem) -> AcknowledgementResponse
```

Adds a new item to the bot's current outfit.

```python
await self.highrise.add_outfit_item(
    OutfitItem(
        type="clothing", 
        amount=1, 
        id="hat-party", 
        account_bound=False, 
        active_palette=0
    )
)
```

Returns an error response if an item with the same ID is already in the outfit.

## remove_outfit_item()

```python
async def remove_outfit_item(self, item_id: str) -> AcknowledgementResponse
```

Removes an item from the bot's current outfit.

```python
await self.highrise.remove_outfit_item("hat-party")
```

Returns an error response if the item isn't in the outfit.
 
### Outfit Management Architecture

The functions `change_item_color()`, `add_outfit_item()`, and `remove_outfit_item()` are wrapper functions that rely on `set_outfit()` to apply changes. 

#### 1. Caching the Current Outfit
The system uses a caching mechanism to optimize performance. The first time you call `get_my_outfit()`, or invoke any bot outfit function, the system fetches and caches the current outfit state of the bot. 

#### 2. Modifying the Outfit State
When you modify an outfit, the system updates this cached state locally:
* `add_outfit_item()`: Appends a new `OutfitItem` object to the current outfit list.
* `remove_outfit_item()`: Identifies and removes the specified `OutfitItem` from the list.
* `change_item_color()`: Locates the target `OutfitItem` and updates its color property.

#### 3. Saving Changes via `set_outfit()`
After the local cache is updated by any of the actions above, the system automatically calls `set_outfit()` under the hood. This pushes the modified outfit state back to the server, ensuring the bot's visual appearance updates instantly.

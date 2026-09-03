# Inventory

Methods for the bot's own inventory: buying items and checking what it owns.

## buy_item()

```python
async def buy_item(self, item_id: str) -> BuyItemResponse
```

Buys an item for the bot.

```python
response = await self.highrise.buy_item("shirt-f_marchingband")

if response.has_error():
    self.logger.warning(f"Purchase failed: {response.error}")
```

### BuyItemResponse body
Response for buying an item.

```python
class BuyItemResponse(BaseResponse):
    result: ItemPurchaseResult | None
```

## get_inventory()

```python
async def get_inventory(self) -> GetInventoryResponse
```

Fetches the bot's own inventory.

```python
inventory = await self.highrise.get_inventory()
```

### GetInventoryResponse body
The bot's inventory.

```python
class GetInventoryResponse(BaseResponse):
    items: list[OutfitItem]
```

`GetInventoryResponse` also has two built-in methods.

- `has_item(self, item_id: str) -> bool` - Checks whether the outfit contains an item with the given id.
- `find_item(self, item_id: str) -> OutfitItem | None` - Finds the item with the given id in the outfit, or `None` if not present.

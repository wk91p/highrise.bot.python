# Wallet

A single method for checking the bot's own currency balances.

## get_wallet()

```python
async def get_wallet(self) -> GetWalletResponse
```

Fetches the bot's wallet.

```python
wallet = await self.highrise.get_wallet()
```

### GetWalletResponse body
The bot's wallet. Contains Highrise currencies.

```python
class GetWalletResponse(BaseResponse):
    content: list[CurrencyItem]
```

### CurrencyItem
A Highrise currency amount. Common types: `gold`, `bubbles`.

```python
class CurrencyItem:
    type: CurrencyType
    amount: int
```

```python
CurrencyType = Literal['gold', 'bubble']
```

`GetWalletResponse` also has a built-in method:
- `get(currency_type: WalletCurrency) -> int | None` - Returns the amount held for the given currency type, or `None` if not present.
# Utils

`Utils` is a collection of stateless helper functions used across the SDK to perform common conversions, formatting, and math operations.

# Methods

Now we will explain what each helper method inside `Utils` does and what it returns.

## `split_tip(amount: int)`
Decomposes a total gold currency amount into a list of the largest possible valid tip tiers using a greedy algorithm.

```python
from highrise import Utils

# Split 550 gold into optimal tip tiers
tips = Utils.split_tip(550)
# Output: ["gold_bar_500", "gold_bar_50"]
```
* **Returns**: `list[TipType]` matching the split values, or an empty list if the amount is less than or equal to `0`.

- Check [`TipType`](../api-reference/player.md#tiptype)

## `format_time(seconds: float)`
Formats a raw duration in seconds into a clean, comma-separated human-readable string.

```python
from highrise import Utils

# Format 397212 seconds
readable_time = Utils.format_time(397212.5)
# Output: "4d, 14h, 20m, 12s"
```
* **Returns**: `str` representing the formatted duration breaking down into days (`d`), hours (`h`), minutes (`m`), and seconds (`s`).

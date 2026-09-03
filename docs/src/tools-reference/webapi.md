# WebApi

`self.webapi` is a separate namespace from `self.highrise`. Where `self.highrise` talks over the bot's live WebSocket connection, `self.webapi` talks over plain HTTP, fetching public data from the Highrise Web API. It works the same way whether the bot is connected to a room or not.

## How it works

Every method on `self.webapi` follows the same pattern under the hood: validate the arguments, make a GET request, and return a structured response. A request that fails, whether from bad input, a network error, or a non-2xx status, comes back as a response with `ok=False` and `error` set, exactly like `self.highrise` methods. Nothing raises to your bot code here either.

```python
response = await self.webapi.get_user("user_123")

if response.has_error():
    self.logger.warning(f"Lookup failed: {response.error}")
```

## Sections

`WebApi` is organized into sections by what they fetch:

- [Users](./webapi/users.md)
- [Rooms](./webapi/rooms.md)
- [Items](./webapi/items.md)
- [Posts](./webapi/posts.md)
- [Grabs](./webapi/grabs.md)
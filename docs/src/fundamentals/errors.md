# Error Handling

`highrise.bot` never raises exceptions up into your bot code for request failures. Whether the problem is bad input on your end or something the server rejected, you always get the same thing back: a response with `ok=False` and `error` set. Nothing to try/except, just a value to check.

## Everything comes back as a response

```python
response = await self.highrise.chat("Hello!")

if response.has_error():
    self.logger.warning(f"Chat failed: {response.error}")
```

This is covered in full on Requests and Responses. The important part here: this same check works no matter what actually went wrong.

## Bad input is caught too

Every method on `self.highrise` validates its own arguments internally before sending anything. If validation fails, that failure is caught and folded into the response as `ok=False`, not raised as a `ValueError` in your code.

```python
response = await self.highrise.chat("")

if response.has_error():
    print(response.error)  # "message must be a non-empty string"
```

There's no separate exception-handling path to write. Whether the request failed because you passed an empty string, or because the server rejected it, or because the response couldn't be parsed, it all lands in the same place: `response.error`.

## The Validator

Internally, every SDK method builds its checks from a shared `Validator`. It's chainable, each check returns itself, so several checks can run in one expression, and any failed check becomes the message you'll see in `response.error`.

see [Validator](../tools-reference/validator.md) in Tools Reference for the full method list.

## A safe command pattern

```python
async def on_chat(self, user, message):
    if message.command() != "!setname":
        return

    new_name = message.args(0)
    if not new_name:
        await self.highrise.chat("Usage: !setname <name>")
        return

    response = await self.highrise.chat(f"Name set to {new_name}")

    if response.has_error():
        self.logger.warning(f"Request failed: {response.error}")
```

One check, `response.has_error()`, covers bad input and server-side failures alike.
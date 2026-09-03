# Requests and Responses

Every method you call on `self.highrise`/`self.webapi` sends a request over the WebSocket/HTTP and gives you back a structured response object. No raw dicts to dig through.

## The base contract

Every response is built on `BaseResponse`:

```python
@dataclass
class BaseResponse:
    ok: bool
    error: str | None = None

    def has_error(self) -> bool:
        return not self.ok
```

Two fields, always there: `ok` tells you if the request succeeded, `error` holds the reason if it didn't. Specific response types add their own fields on top of this by overriding `_build()`, which only runs when `ok` is `True`. If parsing the server's data fails for any reason, the response is automatically marked `ok=False` with the parse error attached, so a malformed response never crashes your bot, it just comes back as a failed response you can check.

## Checking a response

```python
response = await self.highrise.chat("Hello!")

if response.has_error():
    print(f"Chat failed: {response.error}")
else:
    print("Sent!")
```

## AcknowledgementResponse

Most actions, like sending a chat message or performing a moderation action, don't return data. They just need to confirm the server accepted the request. For those, you get an `AcknowledgementResponse`: nothing but `ok` and `error`, inherited straight from `BaseResponse`.

## A real example: chat()

Here's what actually happens when you call `self.highrise.chat(message)`:

```python
response = await self.highrise.chat("Hello everyone!")
```

Under the hood:

1. The message is validated, empty or non-string input raises before anything is sent.
2. If the message is 256 characters or under, it's sent as a single request and you get back one `AcknowledgementResponse`.
3. If it's longer than 256 characters, it's automatically split into chunks and sent `400ms` apart. In that case you get back a `list[AcknowledgementResponse]`, one per chunk.

```python
async def on_chat(self, user, message):
    if message.content == "!long":
        result = await self.highrise.chat("a" * 500)
        if isinstance(result, list):
            print(f"Sent as {len(result)} chunks")
```

You never have to think about chunking yourself. Send whatever string you want, and the SDK handles splitting it safely.

## Why this matters

Because every response follows the same `ok`/`error` shape, you can write one pattern and reuse it everywhere, regardless of which method you called or what data it returns:

```python
response = await self.highrise.some_action(...)
if response.has_error():
    self.logger.warning(f"Action failed: {response.error}")
    return
```

## What is next

Head to The [Message Class](./message-class.md) to see the structure of the `message` argument your chat, whisper and direct hooks receive.
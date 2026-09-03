# Chat

Methods for sending messages in the room, either publicly or as a whisper to one user.

## chat()

```python
async def chat(self, message: str) -> AcknowledgementResponse | list[AcknowledgementResponse]
```

Sends a message to the room's chat.

**Returns**

`AcknowledgementResponse` if the message was sent as a single request. `list[AcknowledgementResponse]` if it was longer than `256` characters and had to be split into chunks, one response per chunk, sent `400ms` apart..

**Example**

Single response:

```python
response = await self.highrise.chat("Hello everyone!")

if response.has_error():
    self.logger.warning(f"Chat failed: {response.error}")
```

Chunked response, for messages over `256` characters:

```python
result = await self.highrise.chat("a" * 500)

if isinstance(result, list):
    for response in result:
        if response.has_error():
            self.logger.warning(f"Chunk failed: {response.error}")
else:
    if result.has_error():
        self.logger.warning(f"Chat failed: {result.error}")
```

## send_whisper()

```python
async def send_whisper(self, user_id: str, message: str) -> AcknowledgementResponse | list[AcknowledgementResponse]
```

Sends a private whisper to a specific user in the room. Only that user sees it.

**Returns**

Same as `chat()`: a single `AcknowledgementResponse`, or a `list[AcknowledgementResponse]` if the message was split into chunks.

**Example**

```python
async def on_chat(self, user, message):
    if message.command() == "!secret":
        await self.highrise.send_whisper(user.id, "Only you can see this.")
```

## Long messages are handled automatically

Both methods split messages over `256` characters into multiple chunks and send them `400ms` apart. You never need to chunk a long message yourself, just call `chat()` or `send_whisper()` with the full string.

```python
result = await self.highrise.chat("a" * 500)

if isinstance(result, list):
    print(f"Sent as {len(result)} chunks")
```
# Channel

A hidden channel for sending messages that don't appear in the visible room chat, meant for bot-to-bot communication.

## send_channel()

```python
async def send_channel(self, message: str, tags: list[str] | None = None) -> AcknowledgementResponse
```

Sends a hidden channel message to the room.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `message` | `str` | The channel payload to send. Required, must be a non-empty string. |
| `tags` | `list[str] \| None` | Optional tags attached to the message, for routing or filtering on the receiving end. Defaults to an empty list. |

```python
response = await self.highrise.send_channel("sync_state", tags=["internal"])

if response.has_error():
    self.logger.warning(f"Channel send failed: {response.error}")
```

## Receiving channel messages

Channel messages sent by other bots (or your own) are received through the `on_channel` hook, covered on the Events page (bots can't see their own messages):

```python
async def on_channel(self, bot_id, message, tags):
    print(f"Channel message from {bot_id}: {message}")
```
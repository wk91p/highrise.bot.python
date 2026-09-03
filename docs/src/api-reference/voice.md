# Voice

Methods for checking and managing the room's voice chat.

## get_voice_status()

```python
async def get_voice_status(self) -> CheckVoiceChatResponse
```

Fetches the current voice chat status for the room.

```python
status = await self.highrise.get_voice_status()
```

### CheckVoiceChatResponse body
The status of voice chat in the room.

```python
class CheckVoiceChatResponse(BaseResponse):
    seconds_left: int
    auto_speakers: set[str]
    users: dict[str, VoiceStatus]
```

- `users` keyed by user_id

## add_user_to_voice()

```python
async def add_user_to_voice(self, user_id: str) -> AcknowledgementResponse
```

Adds a user to voice chat as a speaker.

```python
await self.highrise.add_user_to_voice(user.id)
```

## remove_user_from_voice()

```python
async def remove_user_from_voice(self, user_id: str) -> AcknowledgementResponse
```

Removes a user from voice chat.

```python
await self.highrise.remove_user_from_voice(user.id)
```
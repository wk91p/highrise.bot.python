# Direct Messages

Methods for messaging users outside the room: sending DMs, invites, and reading conversation/messages history.

## send_message()

```python
async def send_message(self, recipient: str | list[str], content: str) -> AcknowledgementResponse | list[AcknowledgementResponse]
```

Sends a text message to a single conversation, or in bulk to multiple users at once.

**Returns**

`AcknowledgementResponse` if sent as a single request. `list[AcknowledgementResponse]` if `content` was over `2000` characters and had to be split into chunks, sent `400ms` apart.

**Example**

```python
# to a conversation
response = await self.highrise.send_message("conv_123", "Hey there!")

# bulk, to multiple users
response = await self.highrise.send_message(["user_id1", "user_id2"], "Announcement!")
```

## send_room_invite()

```python
async def send_room_invite(self, recipient: str | list[str], room_id: str) -> AcknowledgementResponse
```

Sends an invite to a room. Same `recipient` rules as `send_message()`: a single conversation ID, or up to 100 user IDs for bulk.

```python
await self.highrise.send_room_invite("conv_123", room_id)
```

## send_world_invite()

```python
async def send_world_invite(self, recipient: str | list[str], world_id: str) -> AcknowledgementResponse
```

Sends an invite to a world. Same `recipient` rules as `send_message()`.

```python
await self.highrise.send_world_invite("conv_123", world_id)
```

## leave_conversation()

```python
async def leave_conversation(self, conversation_id: str) -> AcknowledgementResponse
```

Leaves a conversation.

```python
await self.highrise.leave_conversation("conv_123")
```

## get_messages()

```python
async def get_messages(self, conversation_id: str, last_message_id: str | None = None) -> GetMessagesResponse
```

Retrieves messages from a conversation, newest page first. Pass `last_message_id` to page backward from a specific message.

**Pagination**

When a full page of 20 messages comes back, the response carries its own `next_page_fn` for fetching the next page, so you can walk through history with `async for`:

```python
async for page in self.highrise.get_messages("conv_123"):
    for message in page.messages:
        print(message.content)
```

### GetMessagesResponse body
Response for fetching messages from a single conversation.

```python
class GetMessagesResponse(BaseResponse):
    messages: list[MessageEntry]
    next_page_fn: Callable[[], Coroutine[Any, Any, "GetMessagesResponse"]] | None
```

### MessageEntry
A single message entry, as returned by `get_messages` or nested inside a `Conversation` as its `last_message`.

```python
class MessageEntry:
    message_id: str
    conversation_id: str
    createdAt: str
    content: str
    sender_id: str
    category: str
```
## get_conversations()

```python
async def get_conversations(self, not_joined: bool = False, last_id: str | None = None) -> GetConversationsResponse
```

Retrieves the bot's conversations. Set `not_joined=True` to only get conversations the bot hasn't joined yet, useful for finding pending DM requests.

**Pagination**

Same pattern as `get_messages()`, a full page of 20 attaches `next_page_fn` automatically:

```python
async for page in self.highrise.get_conversations(not_joined=True):
    for conversation in page.conversations:
        print(conversation.id)
```

### GetConversationsResponse body
Response for fetching the bot's list of conversations.

```python
class GetConversationsResponse(BaseResponse):
    conversations: list[ConversationEntry]
    not_joined: int = 0
    next_page_fn: Callable[[], Coroutine[Any, Any, "GetConversationsResponse"]] | None
```

### ConversationEntry
A single conversation entry as returned by `get_conversations`.

```python
class ConversationEntry:
    id: str
    did_join: bool
    unread_count: int
    last_message: MessageEntry | None
    muted: bool
    member_ids: list[str] | None
    name: str | None
    owner_id: str | None
```

for `MessageEntry` type, check [here](#messageentry)
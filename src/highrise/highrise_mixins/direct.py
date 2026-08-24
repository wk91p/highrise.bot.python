from typing import TYPE_CHECKING, Any
from collections.abc import Callable
import asyncio
import textwrap

if TYPE_CHECKING:
    from ..base_bot import BotContext

from ..models.responses import AcknowledgementResponse, GetMessagesResponse, GetConversationsResponse
from ..models.requests import SendMessageRequest, LeaveConversationRequest, GetMessagesRequest, GetConversationsRequest

DM_MAX_LENGTH = 2000
SPLIT_DELAY = 0.4

class DirectMixin:
    """Direct message-related methods: send/bulk send messages, send room/world invites, get messages/conversations."""

    _context: "BotContext"

    async def _send_request(self, response_cls: Any, build_payload: Callable[[], dict]) -> Any: ...

    async def send_message(
        self,
        recipient: str | list[str],
        content: str,
    ) -> AcknowledgementResponse | list[AcknowledgementResponse]:
        """Sends a text message to a `conversation_id`, or to multiple `userIds` at once (bulk, max 100).
        Messages over `2000` characters are automatically split into multiple
        chunks, sent with a `400ms` delay between each. Returns a single
        response normally, or a list of responses if the message was split."""
        self._context.validator.required(recipient, "recipient")
        self._context.validator.required(content, "content")
        self._context.validator.string(content, "content")

        is_bulk = isinstance(recipient, list)

        if is_bulk:
            self._context.validator.max_items(recipient, 100, "recipient")
        else:
            self._context.validator.string(recipient, "recipient")

        def build_request(chunk: str) -> SendMessageRequest:
            if is_bulk:
                return SendMessageRequest(user_ids=recipient, type="text", content=chunk, is_bulk=True)
            return SendMessageRequest(conversation_id=recipient, type="text", content=chunk)

        if len(content) <= DM_MAX_LENGTH:
            def build() -> dict:
                return build_request(content).to_dict()

            return await self._send_request(AcknowledgementResponse, build)

        chunks = textwrap.wrap(content, width=DM_MAX_LENGTH)
        responses: list[AcknowledgementResponse] = []

        for i, chunk in enumerate(chunks):
            def build(chunk=chunk) -> dict:
                return build_request(chunk).to_dict()

            response = await self._send_request(AcknowledgementResponse, build)
            responses.append(response)

            if i < len(chunks) - 1:
                await asyncio.sleep(SPLIT_DELAY)

        return responses

    async def send_room_invite(
        self,
        recipient: str | list[str],
        room_id: str,
    ) -> AcknowledgementResponse:
        """Sends a room invitation to a `conversation_id`, or to multiple `userIds` at once (bulk, max 100)."""

        def build() -> dict:
            self._context.validator.required(recipient, "recipient")
            self._context.validator.required(room_id, "room_id")
            self._context.validator.string(room_id, "room_id")

            is_bulk = isinstance(recipient, list)
 
            if is_bulk:
                self._context.validator.max_items(recipient, 100, "recipient")
                request = SendMessageRequest(user_ids=recipient, type="invite", room_id=room_id, is_bulk=True)
            else:
                self._context.validator.string(recipient, "recipient")
                request = SendMessageRequest(conversation_id=recipient, type="invite", room_id=room_id)

            return request.to_dict()

        return await self._send_request(AcknowledgementResponse, build)

    async def send_world_invite(
        self,
        recipient: str | list[str],
        world_id: str,
    ) -> AcknowledgementResponse:
        """Sends a world invitation to a `conversation_id`, or to multiple `userIds` at once (bulk, max 100)."""

        def build() -> dict:
            self._context.validator.required(recipient, "recipient")
            self._context.validator.required(world_id, "world_id")
            self._context.validator.string(world_id, "world_id")

            is_bulk = isinstance(recipient, list)

            if is_bulk:
                self._context.validator.max_items(recipient, 100, "recipient")
                request = SendMessageRequest(user_ids=recipient, type="invite", world_id=world_id, is_bulk=True)
            else:
                self._context.validator.string(recipient, "recipient")
                request = SendMessageRequest(conversation_id=recipient, type="invite", world_id=world_id)

            return request.to_dict()

        return await self._send_request(AcknowledgementResponse, build)

    async def leave_conversation(self, conversation_id: str) -> AcknowledgementResponse:
        """Leaves a conversation."""

        def build() -> dict:
            self._context.validator.required(conversation_id, "conversation_id")
            self._context.validator.string(conversation_id, "conversation_id")

            request = LeaveConversationRequest(conversation_id=conversation_id)
            return request.to_dict()

        return await self._send_request(AcknowledgementResponse, build)

    async def get_messages(
        self, conversation_id: str, last_message_id: str | None = None
    ) -> GetMessagesResponse:
        """Retrieves messages from a conversation. Supports `async for` pagination."""

        def build() -> dict:
            self._context.validator.required(conversation_id, "conversation_id")
            self._context.validator.string(conversation_id, "conversation_id")

            if last_message_id is not None:
                self._context.validator.string(last_message_id, "last_message_id")

            request = GetMessagesRequest(conversation_id=conversation_id, last_message_id=last_message_id)
            return request.to_dict()

        response = await self._send_request(GetMessagesResponse, build)

        if response.ok and len(response.messages) == 20:
            last_id = response.messages[-1].message_id
            response.next_page_fn = lambda: self.get_messages(conversation_id, last_id)

        return response

    async def get_conversations(
        self, not_joined: bool = False, last_id: str | None = None
    ) -> GetConversationsResponse:
        """Retrieves the bot's conversations. Supports `async for` pagination."""

        def build() -> dict:
            self._context.validator.boolean(not_joined, "not_joined")

            if last_id is not None:
                self._context.validator.string(last_id, "last_id")

            request = GetConversationsRequest(not_joined=not_joined, last_id=last_id)
            return request.to_dict()

        response = await self._send_request(GetConversationsResponse, build)

        if response.ok and response.conversations and len(response.conversations) == 20:
            last_conversation_id = response.conversations[-1].id
            response.next_page_fn = lambda: self.get_conversations(not_joined, last_conversation_id)

        return response
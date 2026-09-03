from typing import TYPE_CHECKING, Any
from collections.abc import Callable
import asyncio
import textwrap

if TYPE_CHECKING:
    from ...base_bot import BotContext

from ...models.websocket.responses import AcknowledgementResponse
from ...models.websocket.requests import ChatRequest

MAX_MESSAGE_LENGTH = 256
SPLIT_DELAY = 0.4


class ChatMixin:
    """Chat-related methods: room chat, whispers."""

    _context: "BotContext"

    async def _send_request(self, response_cls: Any, build_payload: Callable[[], dict]) -> Any: ...

    async def _send_chunks(self, chunks: list[str], build_request: Callable[[str], Any]) -> list[AcknowledgementResponse]:
        """Sends each chunk in order with a delay between sends, collecting all responses."""
        responses: list[AcknowledgementResponse] = []

        for i, chunk in enumerate(chunks):
            def build(chunk=chunk) -> dict:
                request = build_request(chunk)
                return request.to_dict()

            response = await self._send_request(AcknowledgementResponse, build)
            responses.append(response)

            if i < len(chunks) - 1:
                await asyncio.sleep(SPLIT_DELAY)

        return responses

    async def chat(self, message: str) -> AcknowledgementResponse | list[AcknowledgementResponse]:
        """Sends a message to the room's chat. Messages over `256` characters
        are automatically split into multiple chunks, sent with a `400ms`
        delay between each. Returns a single response normally, or a list
        of responses if the message was split."""
        self._context.validator.required(message, "message")
        self._context.validator.string(message, "message")

        if len(message) <= MAX_MESSAGE_LENGTH:
            def build() -> dict:
                request = ChatRequest(message=message)
                return request.to_dict()

            return await self._send_request(AcknowledgementResponse, build)

        chunks = textwrap.wrap(message, width=MAX_MESSAGE_LENGTH)
        return await self._send_chunks(chunks, lambda chunk: ChatRequest(message=chunk))

    async def send_whisper(self, user_id: str, message: str) -> AcknowledgementResponse | list[AcknowledgementResponse]:
        """Sends a whisper to a user in the room's chat. Messages over `256`
        characters are automatically split into multiple chunks, sent with
        a `400ms` delay between each. Returns a single response normally, or
        a list of responses if the message was split."""
        self._context.validator.required(user_id, "user_id")
        self._context.validator.string(user_id, "user_id")
        self._context.validator.required(message, "message")
        self._context.validator.string(message, "message")

        if len(message) <= MAX_MESSAGE_LENGTH:
            def build() -> dict:
                request = ChatRequest(message=message, whisper_target_id=user_id)
                return request.to_dict()

            return await self._send_request(AcknowledgementResponse, build)

        chunks = textwrap.wrap(message, width=MAX_MESSAGE_LENGTH)
        return await self._send_chunks(chunks, lambda chunk: ChatRequest(message=chunk, whisper_target_id=user_id))
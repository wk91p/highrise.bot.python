import asyncio
from collections.abc import Callable
from typing import Any, Optional, TypeVar, List, Tuple

from ..models.events import (
    AnchorPosition,
    Conversation,
    Item,
    Message,
    Position,
    Receiver,
    Sender,
    User,
)

ChatFilter = Callable[[User, Message], bool]
DirectFilter = Callable[[str, Optional[str], Conversation], bool]
TipFilter = Callable[[Sender, Receiver, Item], bool]
MovementFilter = Callable[[User, Optional[Position], Optional[AnchorPosition]], bool]
EmoteFilter = Callable[[User, str, Receiver], bool]

T = TypeVar("T", bound=tuple)

def _default_key_extractor(event_type: str, payload: tuple) -> Any:
    """Safely extracts deduplication keys based on registered event strings."""
    if event_type == "on_message":
        return payload[0]
    user = payload[0]
    return user.id

class _PendingWait:
    """Internal state for a single wait_for() call."""

    def __init__(
        self,
        event_type: str,
        filter_fn: Optional[Callable[..., bool]],
        max_count: int,
        unique: bool,
    ) -> None:
        self.event_type = event_type
        self.filter_fn = filter_fn
        self.max_count = max_count
        self.unique = unique

        self.results: list[Any] = []
        self._seen_keys: set = set()
        
        self.future: asyncio.Future = asyncio.get_running_loop().create_future()

    def try_add(self, payload: tuple) -> None:
        """Checks a matching event against unique/filter_fn rules, adds it if valid."""
        if self.future.done():
            return

        if self.unique:
            key = _default_key_extractor(self.event_type, payload)
            if key in self._seen_keys:
                return

        if self.filter_fn and not self.filter_fn(*payload):
            return

        if self.unique:
            self._seen_keys.add(key)

        self.results.append(payload)

        if len(self.results) >= self.max_count:
            self.future.set_result(self.results)

class Awaiter:
    """Manages event-based waits with filtering, timeout, max-count, and uniqueness."""

    def __init__(self) -> None:
        self._pending: dict[str, list[_PendingWait]] = {}

    def _feed(self, event_type: str, payload: tuple) -> None:
        """Routes an incoming parsed event to all pending waits registered for its type."""
        waits = self._pending.get(event_type)
        if not waits:
            return

        for wait in waits:
            wait.try_add(payload)

    async def _wait_for(
        self,
        event_type: str,
        filter_fn: Optional[Callable[..., bool]] = None,
        timeout: Optional[float] = None,
        max_count: int = 1,
        unique: bool = False,
    ) -> list[T]:
        """Core engine: registers, awaits, and ensures reliable cleanup."""
        wait = _PendingWait(event_type, filter_fn, max_count, unique)
        self._pending.setdefault(event_type, []).append(wait)

        try:
            if timeout is not None:
                return await asyncio.wait_for(wait.future, timeout)
            return await wait.future
        except asyncio.TimeoutError:
            return wait.results
        finally:
            if event_type in self._pending:
                self._pending[event_type].remove(wait)
                if not self._pending[event_type]:
                    del self._pending[event_type]

    async def chat(
        self,
        filter_fn: Optional[ChatFilter] = None,
        timeout: Optional[float] = None,
        max_count: int = 1,
        unique: bool = False,
    ) -> List[tuple[User, Message]]:
        """Wait for chat messages."""
        return await self._wait_for(
            "on_chat", filter_fn=filter_fn, timeout=timeout, max_count=max_count, unique=unique
        )

    async def whisper(
        self,
        filter_fn: Optional[ChatFilter] = None,
        timeout: Optional[float] = None,
        max_count: int = 1,
        unique: bool = False,
    ) -> List[tuple[User, Message]]:
        """Wait for whispered messages."""
        return await self._wait_for(
            "on_whisper", filter_fn=filter_fn, timeout=timeout, max_count=max_count, unique=unique
        )

    async def direct(
        self,
        filter_fn: Optional[DirectFilter] = None,
        timeout: Optional[float] = None,
        max_count: int = 1,
        unique: bool = False,
    ) -> List[tuple[str, Optional[Message], Conversation]]:
        """Wait for direct messages."""
        return await self._wait_for(
            "on_message", filter_fn=filter_fn, timeout=timeout, max_count=max_count, unique=unique
        )

    async def tip(
        self,
        filter_fn: Optional[TipFilter] = None,
        timeout: Optional[float] = None,
        max_count: int = 1,
        unique: bool = False,
    ) -> List[tuple[User, User, Item]]:
        """Wait for tips."""
        return await self._wait_for(
            "on_tip", filter_fn=filter_fn, timeout=timeout, max_count=max_count, unique=unique
        )

    async def movement(
        self,
        filter_fn: Optional[MovementFilter] = None,
        timeout: Optional[float] = None,
        max_count: int = 1,
        unique: bool = False,
    ) -> List[tuple[User, Optional[Position], Optional[AnchorPosition]]]:
        """Wait for user movement."""
        return await self._wait_for(
            "on_user_move", filter_fn=filter_fn, timeout=timeout, max_count=max_count, unique=unique
        )

    async def emote(
        self,
        filter_fn: Optional[EmoteFilter] = None,
        timeout: Optional[float] = None,
        max_count: int = 1,
        unique: bool = False,
    ) -> List[tuple[User, str, Receiver]]:
        """Wait for emotes."""
        return await self._wait_for(
            "on_emote", filter_fn=filter_fn, timeout=timeout, max_count=max_count, unique=unique
        )

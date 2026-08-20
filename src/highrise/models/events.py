from dataclasses import dataclass, field
from typing import Optional, List, Union
from .highrise_models import Facing, ModerationType, CurrencyType

@dataclass
class User:
    """A user in the room."""
    id: str
    username: str

@dataclass
class Sender(User):
    """The user who sent a tip."""

@dataclass
class Receiver(User):
    """The user who received a tip."""

@dataclass
class Position:
    """A player's position in the room."""
    x: int
    y: int
    z: int
    facing: Facing

@dataclass
class AnchorPosition:
    """Position when a user is anchored to an object (sitting, etc.)."""
    entity_id: str
    anchor_ix: int

@dataclass
class Message:
    """A chat, whisper, or direct message."""

    content: str
    """The full text content of the message."""

    _args: List[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._args = self.content.strip().split() if self.content else []

    def command(self) -> Optional[str]:
        """Returns the first word of the message, treated as the
        command name if this message is a command."""
        return self._args[0] if self._args else None

    def args(self, index: Optional[int] = None) -> Union[List[str], str, None]:
        """Returns the message arguments (excluding the command itself).
        Pass an index to get a specific argument, or omit it to get
        the full list."""
        rest = self._args[1:] if self._args else []

        if index is None:
            return rest

        return rest[index] if index < len(rest) else None

    def mentions(self, index: Optional[int] = None) -> Union[List[str], str, None]:
        """Returns all mentioned usernames (words starting with '@',
        with the '@' stripped). Pass an index to get a specific
        mention, or omit it to get the full list."""
        all_mentions = [
            word[1:] for word in self._args if word.startswith("@")
        ]

        if index is None:
            return all_mentions

        return all_mentions[index] if index < len(all_mentions) else None


@dataclass
class Conversation:
    """A direct message conversation."""
    id: str
    is_new_conversation: bool

@dataclass
class Item:
    """A currency amount exchanged in a tip."""
    type: CurrencyType
    amount: int

@dataclass
class ModerationAction:
    """The type of moderation action taken."""
    type: ModerationType
    duration: Optional[int] = None


@dataclass
class RoomInfo:
    """Room information included in the session metadata."""
    owner_id: str
    room_name: str

    @classmethod
    def _from_raw(cls, data: dict) -> "RoomInfo":
        room_info = data.get("room_info") or {}
        return cls(
            owner_id=room_info.get("owner_id", ""),
            room_name=room_info.get("room_name", ""),
        )

@dataclass
class SessionMetadata:
    """Initial session data.

    Sent once, as the first message when a connection is established.

    - user_id: the bot's user id.
    - room_info: additional information about the connected room.
    - rate_limits: a dict of rate limits, keyed by rate limit name, each value a (limit, period) tuple.
    - connection_id: the connection id of the websocket used in this bot connection.
    - sdk_version: the SDK version recommended by the server, if the client identified itself as an SDK.
    """
    user_id: str
    room_info: RoomInfo
    rate_limits: dict[str, tuple[int, float]]
    connection_id: str
    sdk_version: str | None = None

    @classmethod
    def _from_raw(cls, data: dict) -> "SessionMetadata":
        raw_rate_limits = data.get("rate_limits") or {}
        rate_limits = {
            key: tuple(value) for key, value in raw_rate_limits.items()
        }

        return cls(
            user_id=data.get("user_id", ""),
            room_info=RoomInfo._from_raw(data),
            rate_limits=rate_limits,
            connection_id=data.get("connection_id", ""),
            sdk_version=data.get("sdk_version"),
        )
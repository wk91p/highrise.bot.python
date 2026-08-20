from typing import Literal
from dataclasses import dataclass

Facing = Literal["FrontRight", "FrontLeft", "BackRight", "BackLeft"]
ModerationType = Literal["kick", "mute", "ban", "unban", "unmute"]
Reaction = Literal["clap", "heart", "thumbs", "wave", "wink"]
MessageType = Literal["text", "invite"]
CurrencyType = Literal['gold', 'bubble']
WalletCurrency = Literal["gold", "room_boost_tokens", "room_voice_tokens"]
ItemPurchaseResult = Literal["success", "insufficient_funds"]
TipUserResult = Literal["success", "insufficient_funds"]
VoiceStatus = Literal["invited", "voice", "muted"]
TipType = Literal[
    "gold_bar_1",
    "gold_bar_5",
    "gold_bar_10",
    "gold_bar_50",
    "gold_bar_100",
    "gold_bar_500",
    "gold_bar_1k",
    "gold_bar_5000",
    "gold_bar_10k",
]
TIP_VALUES: dict[int, TipType] = {
    1: "gold_bar_1",
    5: "gold_bar_5",
    10: "gold_bar_10",
    50: "gold_bar_50",
    100: "gold_bar_100",
    500: "gold_bar_500",
    1000: "gold_bar_1k",
    5000: "gold_bar_5000",
    10000: "gold_bar_10k",
}

@dataclass(frozen=True)
class MessageEntry:
    """A single message entry, as returned by `get_messages` or nested
    inside a `Conversation` as its `last_message`."""
    message_id: str
    conversation_id: str
    createdAt: str
    content: str
    sender_id: str
    category: str

@dataclass
class ConversationEntry:
    """A single conversation entry as returned by `get_conversations`."""
    id: str
    did_join: bool
    unread_count: int
    last_message: MessageEntry | None
    muted: bool
    member_ids: list[str] | None = None
    name: str | None = None
    owner_id: str | None = None

@dataclass(frozen=True)
class OutfitItem:
    """A single item in a user's outfit."""
    type: str
    amount: int
    id: str
    account_bound: bool
    active_palette: int

@dataclass(frozen=True)
class RoomPermissions:
    """Room privilege flags to assign to a user."""
    moderator: bool | None = None
    designer: bool | None = None

@dataclass(frozen=True)
class CurrencyItem:
    """A Highrise currency amount. Common types: `gold`, `bubbles`."""
    type: str
    amount: int

@dataclass(frozen=True)
class Credentials:
    """Room/token pair used for the current session."""
    room_id: str
    api_token: str
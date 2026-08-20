from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .base_bot import BaseBot

from .models.events import *
from .models.highrise_models import *


def _parse_user(data: dict | None) -> "User":
    data = data or {}
    return User(data.get("id", ""), data.get("username", ""))


def _parse_position(pos_data: dict) -> "Position":
    """Parses position coordinates rounded to exactly one decimal place."""
    return Position(
        round(float(pos_data.get("x", 0.0)), 1),
        round(float(pos_data.get("y", 0.0)), 1),
        round(float(pos_data.get("z", 0.0)), 1),
        pos_data.get("facing"),
    )


def handle_session_metadata(bot: "BaseBot", data: dict[str, Any]) -> None:
    metadata = SessionMetadata._from_raw(data)
    bot._context.session_metadata = metadata
    bot._create_task(bot.on_start(metadata), "on_start")


def handle_chat_event(bot: "BaseBot", data: dict[str, Any]) -> None:
    user_data = data.get("user") or {}
    is_whisper = user_data.get("whisper", False)
    user = _parse_user(user_data)
    message = Message(data.get("message"))

    if is_whisper:
        bot.awaiter._feed("on_whisper", (user, message))
        bot._create_task(bot.on_whisper(user, message), "on_whisper")
    else:
        bot.awaiter._feed("on_chat", (user, message))
        bot._create_task(bot.on_chat(user, message), "on_chat")


def handle_user_join(bot: "BaseBot", data: dict[str, Any]) -> None:
    user = _parse_user(data.get("user"))
    position = _parse_position(data.get("position") or {})

    bot.cached_users._add(user, position)

    bot._create_task(bot.on_user_join(user, position), "on_user_join")


def handle_user_leave(bot: "BaseBot", data: dict[str, Any]) -> None:
    user = _parse_user(data.get("user"))

    bot.cached_users._remove(user.id)

    bot._create_task(bot.on_user_leave(user), "on_user_leave")


def handle_user_moved(bot: "BaseBot", data: dict[str, Any]) -> None:
    user = _parse_user(data.get("user"))

    pos_data = data.get("position") or {}
    position = None
    anchor = None

    if pos_data:
        if "entity_id" in pos_data:
            anchor = AnchorPosition(
                pos_data.get("entity_id"),
                pos_data.get("anchor_ix"),
            )
            bot.cached_users._update(user.id, anchor)
        else:
            position = _parse_position(pos_data)
            bot.cached_users._update(user.id, position)

    bot._create_task(bot.on_user_move(user, position, anchor), "on_user_move")


def handle_reaction_event(bot: "BaseBot", data: dict[str, Any]) -> None:
    user = _parse_user(data.get("sender"))
    reaction = data.get("reaction", "")
    receiver = _parse_user(data.get("receiver"))

    bot._create_task(bot.on_reaction(user, reaction, receiver), "on_reaction")


def handle_tip_reaction(bot: "BaseBot", data: dict[str, Any]) -> None:
    sender = _parse_user(data.get("sender"))
    receiver = _parse_user(data.get("receiver"))
    item_data = data.get("item") or {}
    item = Item(item_data.get("type"), item_data.get("amount"))

    bot.awaiter._feed("on_tip", (sender, receiver, item))
    bot._create_task(bot.on_tip(sender, receiver, item), "on_tip")


def handle_emote_event(bot: "BaseBot", data: dict[str, Any]) -> None:
    user = _parse_user(data.get("user"))
    emote_id = data.get("emote_id", "")
    receiver = _parse_user(data.get("receiver"))

    bot.awaiter._feed("on_emote", (user, emote_id, receiver))
    bot._create_task(bot.on_emote(user, emote_id, receiver), "on_emote")

async def _handle_message_event(bot: "BaseBot", data: dict[str, Any]) -> None:
    conversation_id = data.get("conversation_id", "")
    conversation = Conversation(
        id=conversation_id,
        is_new_conversation=data.get("is_new_conversation", False),
    )
    user_id = data.get("user_id", "")

    message = None
    if bot.config.auto_fetch.direct_message:
        response = await bot.highrise.get_messages(conversation_id)
        if response.ok and response.messages:
            message = Message(response.messages[0].content)

    bot.awaiter._feed("on_message", (user_id, message, conversation))
    bot._create_task(
        bot.on_message(user_id, message, conversation),
        "on_message",
    )


def handle_message_event(bot: "BaseBot", data: dict[str, Any]) -> None:
    bot._create_task(_handle_message_event(bot, data), "handle_message_event")


def handle_room_moderate(bot: "BaseBot", data: dict[str, Any]) -> None:
    moderator_id = data.get("moderatorId", "")
    target_id = data.get("targetUserId", "")
    moderation_type = data.get("moderationType", "unknown")
    duration = data.get("duration", 0)

    if moderation_type == "mute" and duration == 1:
        moderation_type = "unmute"

    action = ModerationAction(type=moderation_type, duration=duration)
    bot._create_task(bot.on_moderate(moderator_id, target_id, action), "on_moderate")


def handle_channel_event(bot: "BaseBot", data: dict[str, Any]) -> None:
    message = data.get("message", "")
    bot._create_task(
        bot.on_channel(data.get("sender_id", ""), message, data.get("tags", [])),
        "on_channel",
    )


EVENT_HANDLERS = {
    "SessionMetadata": handle_session_metadata,
    "ChatEvent": handle_chat_event,
    "UserJoinedEvent": handle_user_join,
    "UserLeftEvent": handle_user_leave,
    "UserMovedEvent": handle_user_moved,
    "ReactionEvent": handle_reaction_event,
    "TipReactionEvent": handle_tip_reaction,
    "EmoteEvent": handle_emote_event,
    "MessageEvent": handle_message_event,
    "RoomModeratedEvent": handle_room_moderate,
    "ChannelEvent": handle_channel_event,
}
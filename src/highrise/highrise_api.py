from typing import TYPE_CHECKING, Any
from collections.abc import Callable

if TYPE_CHECKING:
    from .base_bot import BotContext

from .highrise_mixins.chat import ChatMixin
from .highrise_mixins.direct import DirectMixin
from .highrise_mixins.channel import ChannelMixin
from .highrise_mixins.player import PlayerMixin
from .highrise_mixins.room import RoomMixin
from .highrise_mixins.voice import VoiceMixin
from .highrise_mixins.wallet import WalletMixin
from .highrise_mixins.inventory import InventoryMixin
from .highrise_mixins.outfit import OutfitMixin

class HighriseApi(
    ChatMixin, 
    DirectMixin, 
    ChannelMixin, 
    PlayerMixin, 
    RoomMixin, 
    VoiceMixin, 
    WalletMixin, 
    InventoryMixin,
    OutfitMixin
    ):
    def __init__(self, context: "BotContext") -> None:
        self._context = context

    async def _send_request(self, response_cls: Any, build_payload: Callable[[], dict]) -> Any:
        try:
            payload = build_payload()
            success, data = await self._context.requester.send(payload)
            return response_cls._from_raw(success, data)
        except ValueError as error:
            return response_cls._from_raw(success=False, data=str(error))
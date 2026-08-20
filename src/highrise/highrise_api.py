from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .base_bot import BotContext

from .mixins.chat import ChatMixin
from .mixins.direct import DirectMixin
from .mixins.channel import ChannelMixin
from .mixins.player import PlayerMixin
from .mixins.room import RoomMixin
from .mixins.voice import VoiceMixin
from .mixins.wallet import WalletMixin
from .mixins.inventory import InventoryMixin
from .mixins.outfit import OutfitMixin

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
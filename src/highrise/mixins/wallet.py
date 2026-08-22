from typing import TYPE_CHECKING, Any
from collections.abc import Callable

if TYPE_CHECKING:
    from ..base_bot import BotContext

from ..models.responses import GetWalletResponse
from ..models.requests import GetWalletRequest

class WalletMixin:
    """Wallet-related methods: fetch the bot's currency balances."""

    _context: "BotContext"

    async def _send_request(self, response_cls: Any, build_payload: Callable[[], dict]) -> Any: ...

    async def get_wallet(self) -> GetWalletResponse:
        """Fetches the bot's wallet."""

        def build() -> dict:
            request = GetWalletRequest()
            return request.to_dict()

        return await self._send_request(GetWalletResponse, build)
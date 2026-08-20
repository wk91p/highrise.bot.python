from ..models.webapi_responses import GetPublicUserResponse
from typing import Any, Callable, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..base_bot import BotContext

class UsersWebMixin:
    """Public web API methods for user lookups."""

    _context : "BotContext"

    async def _send_request(
        self, endpoint: str, response_cls: Any, validate_fn: Callable, params: Optional[dict] = None
    ) -> Any: ...

    async def get_user(self, identifier: str) -> GetPublicUserResponse:
        """Fetches a user's public profile by id or username."""
        
        def validate():
            self._context.validator.required(identifier, "identifier")
            self._context.validator.string(identifier, "identifier")

        return await self._send_request(f"/users/{identifier}", GetPublicUserResponse, validate)
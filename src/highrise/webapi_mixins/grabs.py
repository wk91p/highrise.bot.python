from typing import TYPE_CHECKING, Any, Callable, Optional
from ..models.webapi_models import SortOptions

if TYPE_CHECKING:
    from ..base_bot import BotContext

from ..models.webapi_responses import GetPublicGrabResponse, GetPublicGrabsResponse

class GrabsWebMixin:
    """Public web API methods for grab lookups."""

    _context: "BotContext"

    async def _send_request(
        self, endpoint: str, response_cls: Any, validate_fn: Callable, params: Optional[dict] = None
    ) -> Any: ...

    async def get_grab(self, grab_id: str) -> GetPublicGrabResponse:
        """Fetch a single grab given its grab_id."""

        def validate():
            self._context.validator.required(grab_id, "grab_id")
            self._context.validator.string(grab_id, "grab_id")

        return await self._send_request(f"/grabs/{grab_id}", GetPublicGrabResponse, validate)

    async def get_grabs(
        self,
        starts_after: str | None = None,
        ends_before: str | None = None,
        sort_order: SortOptions = "desc",
        limit: int = 20,
        title: str | None = None,
    ) -> GetPublicGrabsResponse:
        """Fetch a list of grabs, can be filtered, ordered, and paginated."""

        def validate():
            self._context.validator.string(sort_order, "sort_order")
            self._context.validator.one_of(sort_order, ("desc", "asc"), "sort_order")

            self._context.validator.integer(limit, "limit")
            self._context.validator.range(limit, 1, 100, "limit")

            if starts_after is not None:
                self._context.validator.string(starts_after, "starts_after")
            if ends_before is not None:
                self._context.validator.string(ends_before, "ends_before")
            if title is not None:
                self._context.validator.string(title, "title")

        params = {
            "starts_after": starts_after,
            "ends_before": ends_before,
            "sort_order": sort_order,
            "limit": limit,
            "title": title,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._send_request("/grabs", GetPublicGrabsResponse, validate, params=params)

        if response.ok and len(response.grabs) == limit:
            last_id = response.last_id
            response.next_page_fn = lambda: self.get_grabs(
                starts_after=last_id, sort_order=sort_order, limit=limit, title=title,
            )

        return response
import httpx
from .http_client import HttpClient
from .constants import WEBAPI_BASE_URL
from typing import Any, TYPE_CHECKING
from collections.abc import Callable

from .webapi_mixins.users import UsersWebMixin
from .webapi_mixins.rooms import RoomsWebMixin
from .webapi_mixins.posts import PostsWebMixin
from .webapi_mixins.items import ItemsWebMixin
from .webapi_mixins.grabs import GrabsWebMixin

if TYPE_CHECKING:
    from .base_bot import BotContext

class WebApi(
    UsersWebMixin,
    RoomsWebMixin,
    ItemsWebMixin,
    PostsWebMixin,
    GrabsWebMixin
    ):
    """A class for interacting with the Highrise Web API.

    This class provides asynchronous methods for fetching data from the Highrise API.
    It supports fetching single and multiple `users`, `rooms`, `posts`, `grabs` and `items`

    Each method corresponds to a specific endpoint on the Highrise API, and returns a
    structured response based on the response JSON and webapi models.
    """

    def __init__(self, context: "BotContext", base_url: str = WEBAPI_BASE_URL) -> None:
        self._http = HttpClient(base_url)
        self._context = context

    async def _send_request(
        self, endpoint: str, response_cls: Any, validate_fn: Callable, params: dict | None = None
    ) -> Any:
        try:
            validate_fn()
            resp = await self._http.get(endpoint, params=params)
        except (httpx.RequestError, ValueError) as e:
            return response_cls._from_raw(False, str(e))

        if 200 <= resp.status_code < 300:
            return response_cls._from_raw(True, resp.json())

        return response_cls._from_raw(False, resp.text)
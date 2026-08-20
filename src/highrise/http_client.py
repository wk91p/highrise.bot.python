from typing import Any, Optional
import httpx


class HttpClient:
    """A generic, reusable async `HTTP` client wrapper. Not tied to any
    specific API, can be used for any base URL and any set of
    endpoints. Owns a single `httpx.AsyncClient` for its lifetime."""

    def __init__(self, base_url: str = "", timeout: float = 10.0, headers: Optional[dict] = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=timeout, headers=headers or {})

    @property
    def client(self) -> httpx.AsyncClient:
        return self._client

    @property
    def base_url(self) -> str:
        return self._base_url

    def url(self, path: str) -> str:
        """Builds a full URL from a path relative to base_url."""
        return f"{self._base_url}/{path.lstrip('/')}"

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client.get(self.url(path), **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client.post(self.url(path), **kwargs)

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client.put(self.url(path), **kwargs)

    async def patch(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client.patch(self.url(path), **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client.delete(self.url(path), **kwargs)

    async def close(self) -> None:
        """Closes the underlying client. Call when the client is no
        longer needed (e.g. process shutdown), not required for
        normal operation."""
        await self._client.aclose()
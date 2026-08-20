import time
from typing import Optional


class Metrics:
    """Tracks runtime stats for the bot session: `uptime` and `keepalive
    latency`, `..etc`, Updated directly by `BaseBot` as connection and keepalive
    events happen."""

    def __init__(self) -> None:
        self._connected_at: Optional[float] = None
        self._last_latency: Optional[float] = None
        self._events_processed: int = 0

    def mark_connected(self) -> None:
        """Called when a connection is successfully established."""
        self._connected_at = time.monotonic()

    def mark_disconnected(self) -> None:
        """Called when the connection drops, resetting uptime tracking."""
        self._connected_at = None

    def record_latency(self, seconds: float) -> None:
        """Records the round-trip time of the most recent keepalive."""
        self._last_latency = seconds

    def record_event(self, count: int = 1) -> None:
        """Increments the count of processed events by the given amount."""
        self._events_processed += count

    def reset_events(self) -> None:
        """Resets the processed events counter back to zero."""
        self._events_processed = 0

    @property
    def uptime(self) -> float:
        """Seconds since the current connection was established. 0 if not connected."""
        if self._connected_at is None:
            return 0.0
        return time.monotonic() - self._connected_at

    @property
    def latency(self) -> Optional[float]:
        """Round-trip time in seconds of the last keepalive, or None if not yet measured."""
        return self._last_latency

    @property
    def events_processed(self) -> int:
        """The total number of events processed (not received) during this session."""
        return self._events_processed

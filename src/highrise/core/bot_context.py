from .bot_ws_requester import WSRequester
from ..tools.validator import Validator
from ..cache.cache import CacheManager
from ..tools.metrics import Metrics
from ..models.highrise.highrise_models import SessionMetadata, Credentials

class BotContext:
    """SDK-Level shared mutable state and dependencies."""

    def __init__(self, requester: "WSRequester", validator: "Validator") -> None:
        self.requester = requester
        self.validator = validator
        self.session_metadata: SessionMetadata | None = None
        self.credentials: Credentials | None = None
        self.cache = CacheManager()
        self.metrics = Metrics()
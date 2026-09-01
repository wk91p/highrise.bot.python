from dataclasses import dataclass, field
from .tools.logger import LoggerLevel

@dataclass
class ConnectionConfig:
    keepalive_delay: int = 15
    min_reconnect_delay: float = 5.0
    max_reconnect_delay: float = 30.0
    reconnect_backoff_factor: float = 2.0
    max_reconnect_attempts: int | None = None

@dataclass
class LoggerConfig:
    name: str = "HighriseBot"
    level: int = LoggerLevel.DEBUG
    show_time: bool = True

@dataclass
class AutoFetchConfig:
    room_users: bool = False
    direct_message: bool = False

@dataclass
class RolesConfig:
    path: str = "./jsons/roles.json"
    autosave_interval: float = 600.0

@dataclass
class BotConfig:
    connection: ConnectionConfig = field(default_factory=ConnectionConfig)
    logger: LoggerConfig = field(default_factory=LoggerConfig)
    auto_fetch: AutoFetchConfig = field(default_factory=AutoFetchConfig)
    roles: RolesConfig = field(default_factory=RolesConfig)
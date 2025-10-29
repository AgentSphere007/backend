from .config import _server, _database
from .config import init_config
from .types import ServerConfig, DatabaseConfig


class Config:
    server: ServerConfig
    database: DatabaseConfig

    def __init__(self, server: ServerConfig, db: DatabaseConfig):
        self.server = server
        self.database = db


config = Config(_server, _database)


__all__ = ["config"]

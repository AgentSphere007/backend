from .config import _server, _database, _app
from .types import AppConfig, ServerConfig, DatabaseConfig


class Config:
    server: ServerConfig
    database: DatabaseConfig
    app: AppConfig

    def __init__(self, server: ServerConfig, db: DatabaseConfig, app: AppConfig):
        self.server = server
        self.database = db
        self.app = app


config = Config(_server, _database, _app)


__all__ = ["config"]

import os
import tomllib
from pathlib import Path
from .types import SecurityConfig, ServerConfig, DatabaseConfig

CONFIG_PATH = (
    Path(str(os.getenv("CONFIG_FILE")))
    if os.getenv("CONFIG_FILE")
    else Path(__file__).parent.parent.parent / "config.toml"
)


def init_config():
    with open(CONFIG_PATH, "rb") as f:
        cfg = tomllib.load(f)

    server = ServerConfig(
        host=cfg["server"]["host"],
        port=cfg["server"]["port"],
        production=cfg["server"]["production"],
        security=SecurityConfig(jwt_secret=cfg["server"]["security"]["jwt-secret"]),
    )

    database = DatabaseConfig(
        host=cfg["database"]["host"],
        port=cfg["database"]["port"],
        username=cfg["database"]["username"],
        password=cfg["database"]["password"],
        dbname=cfg["database"]["db-name"],
        sslmode=cfg["database"]["ssl-mode"],
        maxtries=cfg["database"]["max-tries"],
    )

    return server, database


_server, _database = init_config()

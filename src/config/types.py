from dataclasses import dataclass
from datetime import timedelta
from typing import List
import re


@dataclass
class SecurityConfig:
    jwt_secret: str
    token_expiry: timedelta

    @staticmethod
    def parse_expiry(value: str) -> timedelta:
        pattern = r"^(?P<num>\d+)(?P<unit>[smhd])$"
        match = re.match(pattern, value.strip().lower())
        if not match:
            raise ValueError(f"Invalid token-expiry format: {value}")
        num = int(match.group("num"))
        unit = match.group("unit")
        return {
            "s": timedelta(seconds=num),
            "m": timedelta(minutes=num),
            "h": timedelta(hours=num),
            "d": timedelta(days=num),
        }[unit]


@dataclass
class AppConfig:
    gemini_api_key: str
    temp_dir_path: str
    image_dir_path: str


@dataclass
class ServerConfig:
    host: str
    port: int
    production: bool
    cors_url: List[str]
    security: SecurityConfig


@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    dbname: str
    sslmode: str
    maxtries: int


__all__ = ["ServerConfig", "DatabaseConfig", "SecurityConfig", "AppConfig"]

from dataclasses import dataclass


@dataclass
class SecurityConfig:
    jwt_secret: str


@dataclass
class ServerConfig:
    host: str
    port: int
    production: bool
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


__all__ = ["ServerConfig", "DatabaseConfig", "SecurityConfig"]

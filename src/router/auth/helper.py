from datetime import datetime, timezone
from sqlalchemy import exc as error
from jose import jwt, JWTError

from src.config import config


def is_unique_violation(e: error.IntegrityError) -> bool:
    msg = str(getattr(e, "orig", e)).lower()
    return "unique" in msg or "duplicate" in msg


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + config.server.security.token_expiry
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.server.security.jwt_secret, algorithm="HS256"
    )
    return encoded_jwt


def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, config.server.security.jwt_secret, algorithms=["HS256"]
        )
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token")


__all__ = ["is_unique_violation", "create_access_token", "verify_access_token"]

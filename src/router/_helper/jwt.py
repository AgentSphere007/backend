from datetime import datetime, timezone
from jose import jwt, JWTError

from src.config import config


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


__all__ = ["create_access_token", "verify_access_token"]

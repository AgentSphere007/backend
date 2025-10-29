from functools import wraps
from fastapi import HTTPException, status, Request
import src.router._helper as helper


def require_auth_endpoint(handler):
    @wraps(handler)
    async def wrapper(request: Request, *args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        token = auth.removeprefix("Bearer ").strip()
        try:
            payload = helper.jwt.verify_access_token(token)
            request.state.user = payload
            return payload
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    return wrapper

from fastapi import Request, HTTPException, status
from sqlalchemy import select
from src.router.user.middleware import require_auth_endpoint
from src.db import DB
from src.models import User
from .schema import UserMeResponse


@require_auth_endpoint
async def get_me(request: Request) -> UserMeResponse:
    """
    Get details of the currently authenticated user.
    Requires a valid JWT token.
    """
    payload = getattr(request.state, "user", None)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )

    user_id = payload["sub"]

    async with DB.session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return UserMeResponse(id=user.id, username=user.username)

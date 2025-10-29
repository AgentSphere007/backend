from fastapi import Request, HTTPException, status
from src.router.user import userRouter
from src.router.user.middleware import require_auth_endpoint
from src.db import DB
from sqlalchemy import select
from src.models import User


@userRouter.get("/me")
@require_auth_endpoint
async def get_me(request: Request):
    payload = getattr(request.state, "user", None)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    user_id = payload["sub"]
    async with DB.session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return {"id": user.id, "username": user.username}

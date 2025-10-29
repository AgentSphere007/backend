from fastapi import APIRouter
from .auth import authRouter
from .user import userRouter

router = APIRouter(prefix="/api")
router.include_router(authRouter)
router.include_router(userRouter)


@router.get("/ping")
async def ping():
    return {"msg": "pong"}


__all__ = ["router"]

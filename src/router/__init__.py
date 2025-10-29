from fastapi import APIRouter
from .auth import authRouter
from .user import userRouter
from .repo import repoRouter

router = APIRouter(prefix="/api")
router.include_router(authRouter)
router.include_router(userRouter)
router.include_router(repoRouter)


@router.get("/ping")
async def ping():
    return {"msg": "pong"}


__all__ = ["router"]

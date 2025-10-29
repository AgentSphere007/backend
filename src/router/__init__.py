from fastapi import APIRouter
from .auth import authRouter

router = APIRouter(prefix="/api")
router.include_router(authRouter)


@router.get("/ping")
async def ping():
    return {"msg": "pong"}

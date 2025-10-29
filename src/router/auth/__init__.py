from fastapi import APIRouter
from . import handlers

authRouter = APIRouter(prefix="/auth", tags=["auth"])
authRouter.post("/signup")(handlers.user_signup)
authRouter.post("/login")(handlers.user_login)

__all__ = ["authRouter"]

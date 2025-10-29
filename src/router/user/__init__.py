from fastapi import APIRouter
from . import handlers

userRouter = APIRouter(prefix="/user", tags=["user"])

userRouter.get("/me")(handlers.get_me)

__all__ = ["userRouter"]

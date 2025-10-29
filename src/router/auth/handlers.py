from sqlalchemy import exc as error, select
from fastapi import HTTPException, status
import src.router._helper as helper
from src.db import DB
from src.models import User
from .schema import AuthTokenResponse, UserLoginRequest, UserSignupRequest


async def user_signup(body: UserSignupRequest) -> AuthTokenResponse:
    user = User(username=body.username)
    user.set_password(body.password)

    async with DB.session() as session:
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
            data = {"uid": user.id, "sub": user.username}
            return AuthTokenResponse(token=helper.jwt.create_access_token(data))
        except error.IntegrityError as e:
            await session.rollback()
            if helper.sql_error.is_unique_violation(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity error",
            ) from e


async def user_login(body: UserLoginRequest) -> AuthTokenResponse:
    async with DB.session() as session:
        stmt = select(User).where(User.username == body.username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not user.verify_password(body.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        data = {"uid": user.id, "sub": user.username}
        return AuthTokenResponse(token=helper.jwt.create_access_token(data))

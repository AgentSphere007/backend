from pydantic import BaseModel, EmailStr, Field


class UserLoginRequest(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="Desired username"
    )
    password: str = Field(
        ..., min_length=6, max_length=100, description="User password"
    )


class UserSignupRequest(BaseModel):
    email: EmailStr = Field(..., description="Valid user email")
    username: str = Field(
        ..., min_length=3, max_length=50, description="Desired username"
    )
    password: str = Field(
        ..., min_length=6, max_length=100, description="User password"
    )


class AuthTokenResponse(BaseModel):
    token: str = Field(..., description="JWT access token for authentication")

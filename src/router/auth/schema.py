from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="Desired username"
    )
    password: str = Field(
        ..., min_length=6, max_length=100, description="User password"
    )


class AuthTokenResponse(BaseModel):
    token: str = Field(..., description="JWT access token for authentication")

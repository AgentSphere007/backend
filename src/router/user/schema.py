from pydantic import BaseModel, Field


class UserMeResponse(BaseModel):
    id: int = Field(..., description="Unique ID of the authenticated user")
    username: str = Field(..., description="Username of the authenticated user")

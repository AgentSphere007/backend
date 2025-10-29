from pydantic import BaseModel, HttpUrl, Field


class NewRepoRequest(BaseModel):
    model_name: str = Field(..., description="Name of the model or project")
    repo_url: HttpUrl = Field(
        ..., description="Valid repository URL (e.g. GitHub link)"
    )
    is_private: bool = Field(
        False, description="Whether the repository should be private"
    )

from pydantic import BaseModel, HttpUrl, Field


class NewRepoRequest(BaseModel):
    model_name: str = Field(..., description="Name of the model or project")
    repo_url: HttpUrl = Field(
        ..., description="Valid repository URL (e.g. GitHub link)"
    )
    short_description: str = Field(..., description="Description of the repo")
    createdBy: str = Field(..., description="Creator of the repo")
    createdAt: str = Field(..., description="Created at time of the repo")
    is_private: bool = Field(
        False, description="Whether the repository should be private"
    )

from fastapi import APIRouter
from . import handlers

repoRouter = APIRouter(prefix="/repo", tags=["repository"])

repoRouter.get("/all")(handlers.all_repos)
repoRouter.post("/new")(handlers.new_repo)
repoRouter.get("/{user}")(handlers.user_repos)
repoRouter.get("/{user}/{model}")(handlers.model_repo)

__all__ = ["repoRouter"]

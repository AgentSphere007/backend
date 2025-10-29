import json
from .security import check_secure
from .cloner import clone
from src.models import Repository, RepositoryStatus
from src.db import DB


async def verify_repo(repo: Repository):
    repo_name = repo.repo_name
    if not repo_name:
        repo.status = RepositoryStatus.failed
        repo.issues = json.dumps({"issue": "failed to get repo name from url"})
    else:
        try:
            clone(repo.repo_url)
            is_secure = check_secure(repo_name).get("core_issues", [])
            repo.status = (
                RepositoryStatus.success if not is_secure else RepositoryStatus.failed
            )
            repo.issues = None if not is_secure else json.dumps({"issues": is_secure})
        except Exception as e:
            repo.status = RepositoryStatus.failed
            repo.issues = json.dumps({"issue": str(e)})
    async with DB.session() as session:
        merged_repo = await session.merge(repo)
        await session.commit()
        await session.refresh(merged_repo)
        return merged_repo


__all__ = ["verify_repo"]

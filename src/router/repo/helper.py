from pathlib import Path

from src.models import Repository, RepositoryStatus
from src.utils import verify
from src.utils import sandbox


async def setup_repo(repo: Repository) -> bool:
    try:
        verified_repo = await verify.verify_repo(repo)
        if verified_repo.status != RepositoryStatus.success:
            return False
        is_done_setup: Path | None = await sandbox.setup_sandbox(verified_repo)
        if not is_done_setup:
            return False
        return True
    except:
        return False

from pathlib import Path
from .replace_model import replaceWithCustomModel
from src.models import Repository
from src.config import config


async def setup_sandbox(repo: Repository):
    temp_dir = Path(config.app.temp_dir_path)
    repo_name: str | None = getattr(repo, "repo_name", None)
    if not repo_name:
        raise ValueError("Repository has no valid repo name")
    repo_path = temp_dir / repo_name
    replaceWithCustomModel(repo_path)

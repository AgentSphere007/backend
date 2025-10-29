from pathlib import Path
from .replace_model import replaceWithCustomModel
from .make_req import generate_requirements
from src.models import Repository
from src.config import config
from src.utils import docker


async def setup_sandbox(repo: Repository) -> Path | None:
    try:
        temp_dir = Path(config.app.temp_dir_path)
        repo_name: str | None = getattr(repo, "repo_name", None)
        if not repo_name:
            raise ValueError("Repository has no valid repo name")
        repo_path = temp_dir / repo_name
        replaceWithCustomModel(repo_path)
        generate_requirements(repo_path)

        image = docker.create_image(repo_path, repo.model_name)
        docker.export_and_compress_image(image, "latest")
    except:
        return None

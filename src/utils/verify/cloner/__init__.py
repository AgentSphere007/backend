import os
import git
from urllib.parse import urlparse


def clone(repo_url: str):
    BASE_DIR = os.path.join("temp")
    repo_name = os.path.splitext(os.path.basename(urlparse(repo_url).path))[0]
    repo_dir = os.path.join(BASE_DIR, repo_name)
    os.makedirs(BASE_DIR, exist_ok=True)
    if os.path.exists(repo_dir):
        # print(f"Removing existing folder: {repo_dir}") TODO: switch with logger
        os.system(f'rm -rf "{repo_dir}"')
    # print(f"Cloning {repo_url} into {repo_dir}...") TODO: switch with logger
    git.Repo.clone_from(repo_url, repo_dir)
    # print("Repo cloned successfully!") TODO: logger
    return repo_name


__all__ = ["clone"]

import os
import git
from dotenv import load_dotenv
from urllib.parse import urlparse
load_dotenv()

def cloner():
    repo_url = input("Enter GitHub repo URL: ")
    BASE_DIR= os.getenv('repo_stor')

    repo_name = os.path.splitext(os.path.basename(urlparse(repo_url).path))[0]
    repo_dir = os.path.join(BASE_DIR, repo_name)

    os.makedirs(BASE_DIR, exist_ok=True)
    if os.path.exists(repo_dir):
        print(f"Removing existing folder: {repo_dir}")
        os.system(f"rm -rf \"{repo_dir}\"")

    print(f"Cloning {repo_url} into {repo_dir}...")
    git.Repo.clone_from(repo_url, repo_dir)

    print("Repo cloned successfully!")

    return repo_name
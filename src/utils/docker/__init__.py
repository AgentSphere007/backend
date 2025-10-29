from pathlib import Path
import docker
import os
import subprocess
from docker.errors import ImageNotFound, APIError, BuildError
from docker.models.images import Image

from src.config import config


def get_docker_client():
    try:
        return docker.from_env()
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Docker daemon: {e}")


def create_image(repo_path: Path, image_name: str, tag: str = "latest"):
    client = get_docker_client()
    try:
        image, _ = client.images.build(
            path=str(repo_path), tag=f"{image_name}:{tag}", rm=True
        )  # export logs to a file later
        return image
    except (BuildError, APIError) as e:
        raise ValueError("Failed to create image or access client")


def image_exists(image_name: str, tag: str = "latest") -> bool:
    client = get_docker_client()
    try:
        client.images.get(f"{image_name}:{tag}")
        return True
    except ImageNotFound:
        return False
    except APIError:
        return False


def pull_image(image_name: str, tag: str = "latest"):
    client = get_docker_client()
    try:
        image = client.images.pull(image_name, tag=tag)
        return image
    except APIError as e:
        raise RuntimeError(f"Failed to pull image '{image_name}:{tag}': {e}") from e


def export_and_compress_image(image: Image, tag: str) -> Path:
    client = get_docker_client()
    export_dir = Path(config.app.image_dir_path)
    export_dir.mkdir(parents=True, exist_ok=True)

    image_name = (
        image.tags[0] if image.tags else f"untagged_{image.short_id.replace(':', '_')}"
    )
    safe_name = image_name.replace("/", "_").replace(":", "_")

    tar_path = export_dir / f"{safe_name.replace('/', '_')}_{tag}.tar"
    zip_path = export_dir / f"{safe_name.replace('/', '_')}_{tag}.7z"

    try:
        image = client.images.get(f"{safe_name}:{tag}")
    except ImageNotFound:
        raise RuntimeError(f"Image {safe_name}:{tag} not found.")
    except APIError as e:
        raise RuntimeError(f"Failed to access Docker image: {e}")

    try:
        with open(tar_path, "wb") as f:
            for chunk in image.save(named=True):
                f.write(chunk)
    except Exception as e:
        raise RuntimeError(f"Failed to export image: {e}")
    try:
        result = subprocess.run(
            ["7z", "a", str(zip_path), str(tar_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"7z compression failed: {result.stderr}")
    except FileNotFoundError:
        raise RuntimeError("7z binary not found — please install p7zip or 7-Zip CLI.")
    finally:
        if tar_path.exists():
            os.remove(tar_path)

    return zip_path

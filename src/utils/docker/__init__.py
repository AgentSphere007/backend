from pathlib import Path
import docker
from docker.errors import ImageNotFound, APIError, BuildError


def get_docker_client():
    """
    Returns a Docker client connected to the local Docker daemon.
    """
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
        raise


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

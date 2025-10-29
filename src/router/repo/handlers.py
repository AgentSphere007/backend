# /repo/all
# /repo/new
# /repo/<user>
# /repo/<user>/<model>

from fastapi import Request, HTTPException, status
from src.models.repository import RepositoryStatus
from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload
import sqlalchemy.exc as error
from urllib.parse import urlparse

from src.router.user.middleware import require_auth_endpoint
from src.models import Repository, User
from src.db import DB
import src.router._helper as helper
from .helper import setup_repo
from .schema import NewRepoRequest


async def all_repos():
    async with DB.session() as session:
        try:
            stmt = select(Repository).options(selectinload(Repository.user))
            result = await session.execute(stmt)
            repos = result.scalars().all()
            return [
                {
                    "id": repo.id,
                    "model_name": repo.model_name,
                    "repo_url": repo.repo_url,
                    "user_name": repo.user.username if repo.user else None,
                    "rating": repo.rating,
                    "status": repo.status,
                    "description":repo.description,
                }
                for repo in repos
            ]
        except error.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )


@require_auth_endpoint
async def new_repo(request: Request, body: NewRepoRequest):
    model_name = body.model_name
    repo_url = str(body.repo_url)
    is_private = body.is_private
    description = body.short_description

    if not model_name or not repo_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="model_name and repo_url are required",
        )

    user_id = request.state.user["uid"]
    async with DB.session() as session:
        try:
            repo = Repository(
                user_id=user_id,
                model_name=model_name,
                repo_url=repo_url,
                is_private=is_private,
                status=RepositoryStatus.pending,
                description=description
            )
            session.add(repo)
            await session.commit()
            await session.refresh(repo)
            await setup_repo(repo)
            return {
                "id": repo.id,
                "model_name": repo.model_name,
                "repo_url": repo.repo_url,
                "rating": repo.rating,
            }
        except error.IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Repository already exists or invalid foreign key",
            )
        except error.SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )

@require_auth_endpoint
async def user_repos(request: Request, user: str):
    requester_uid = None
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.removeprefix("Bearer ").strip()
        try:
            payload = helper.jwt.verify_access_token(token)
            requester_uid = payload.get("uid")
        except ValueError:
            requester_uid = None

    async with DB.session() as session:
        user_obj = await session.scalar(select(User).where(User.username == user))
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{user}' not found",
            )

        stmt = (
            select(Repository)
            .options(selectinload(Repository.user))
            .where(Repository.user_id == user_obj.id)
        )
        if requester_uid != user_obj.id:
            stmt = stmt.where(Repository.is_private == False)

        result = await session.execute(stmt)
        repos = result.scalars().all()
        # if not repos:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"No repositories found for user '{user}'",
        #     )
        if not repos:
            return []

        return [
            {
                "id": repo.id,
                "model_name": repo.model_name,
                "repo_url": repo.repo_url,
                "rating": repo.rating,
                "is_private": repo.is_private,
                "user_name": repo.user.username,
                "status": repo.status,
            }
            for repo in repos
        ]

@require_auth_endpoint
async def model_repo(request: Request, user: str, model: str):
    requester_uid = None
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.removeprefix("Bearer ").strip()
        try:
            payload = helper.jwt.verify_access_token(token)
            requester_uid = payload.get("uid")
        except ValueError:
            requester_uid = None

    async with DB.session() as session:
        user_obj = await session.scalar(select(User).where(User.username == user))
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{user}' not found",
            )

        stmt = (
            select(Repository)
            .join(User)
            .options(selectinload(Repository.user))
            .where(
                and_(
                    Repository.model_name == model,
                    Repository.user_id == user_obj.id,
                )
            )
        )
        if requester_uid != user_obj.id:
            stmt = stmt.where(Repository.is_private == False)

        repo = (await session.execute(stmt)).scalars().first()
        if not repo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model '{model}' not found for user '{user}'",
            )

        return {
            "id": repo.id,
            "model_name": repo.model_name,
            "repo_url": repo.repo_url,
            "rating": repo.rating,
            "description": repo.description,
            "is_private": repo.is_private,
            "user_name": repo.user.username,
            "status": repo.status,
        }

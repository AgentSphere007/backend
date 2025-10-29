import enum
from sqlalchemy import Boolean, Enum, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models import User
from src.db import Base


class RepositoryStatus(enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"


class Repository(Base):
    __tablename__ = "repository"

    repo_url: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    model_name: Mapped[str] = mapped_column(String, nullable=False)

    rating: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(String)
    is_private: Mapped[bool] = mapped_column(Boolean)
    status: Mapped[RepositoryStatus] = mapped_column(
        Enum(RepositoryStatus), default=RepositoryStatus.pending
    )
    issues: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship(back_populates="repositories")

    @property
    def repo_name(self) -> str | None:
        if not self.repo_url:
            return None
        from urllib.parse import urlparse

        parsed = urlparse(self.repo_url)
        repo_path = parsed.path.strip("/")
        if repo_path.endswith(".git"):
            repo_path = repo_path[:-4]
        return repo_path

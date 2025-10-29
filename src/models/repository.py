from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.db import Base


class Repository(Base):
    __tablename__ = "repository"
    repo_url: Mapped[str] = mapped_column(String, nullable=False)

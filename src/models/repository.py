from sqlalchemy import Boolean, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models import User
from src.db import Base


class Repository(Base):
    __tablename__ = "repository"
    repo_url: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(String)
    is_private: Mapped[bool] = mapped_column(Boolean)

    user: Mapped["User"] = relationship(back_populates="repositories")

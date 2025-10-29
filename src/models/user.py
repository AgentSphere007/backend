from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base
from argon2 import PasswordHasher, exceptions

ph = PasswordHasher()


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    repositories = relationship("Repository", back_populates="user")


    def set_password(self, password: str) -> None:
        self.password = ph.hash(password)

    def verify_password(self, password: str) -> bool:
        try:
            return ph.verify(self.password, password)
        except exceptions.VerifyMismatchError:
            return False

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src.db import Base
from argon2 import PasswordHasher, exceptions

ph = PasswordHasher()


class User(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    def set_password(self, password: str) -> None:
        self.password = ph.hash(password)

    def verify_password(self, password: str) -> bool:
        try:
            return ph.verify(self.password, password)
        except exceptions.VerifyMismatchError:
            return False

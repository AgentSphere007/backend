# from sqlalchemy import String
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from src.db import Base
# from argon2 import PasswordHasher, exceptions

# ph = PasswordHasher()


# class User(Base):
#     __tablename__ = "users"

#     username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
#     password: Mapped[str] = mapped_column(String, nullable=False)

#     # repositories = relationship("Repository", back_populates="user")


#     def set_password(self, password: str) -> None:
#         self.password = ph.hash(password)

#     def verify_password(self, password: str) -> bool:
#         try:
#             return ph.verify(self.password, password)
#         except exceptions.VerifyMismatchError:
#             return False


from __future__ import annotations  # enables forward references safely

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from argon2 import PasswordHasher, exceptions
from src.db import Base

ph = PasswordHasher()


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    # 👇 forward reference — avoids circular import
    repositories: Mapped[list["Repository"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password = ph.hash(password)

    def verify_password(self, password: str) -> bool:
        try:
            return ph.verify(self.password, password)
        except exceptions.VerifyMismatchError:
            return False

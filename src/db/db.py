import asyncio
from contextlib import asynccontextmanager
import os
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)
from datetime import datetime
from sqlalchemy import DateTime, Integer, exc, func

from src.config import config


class _Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}


class _Database:
    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None
    _connected: bool = False

    async def connect(self) -> None:
        if self._connected:
            return
        db_cfg = config.database
        db_url: str
        raw_url: str | None = os.getenv("DATABASE_URL")
        if raw_url is not None:
            db_url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif config.server.production:
            db_url = (
                f"postgresql+asyncpg://{db_cfg.username}:{db_cfg.password}@"
                f"{db_cfg.host}:{db_cfg.port}/{db_cfg.dbname}"
            )
        else:
            if not os.path.exists("./temp"):
                os.makedirs("./temp", exist_ok=True)
            db_url = "sqlite+aiosqlite:///./temp/dev.db"

        max_tries = getattr(db_cfg, "maxtries", 3)
        delay = 2

        for attempt in range(1, max_tries + 1):
            try:
                self._engine = create_async_engine(
                    db_url, echo=not config.server.production
                )
                self._session_factory = async_sessionmaker(
                    bind=self._engine, expire_on_commit=False, class_=AsyncSession
                )
                async with self._engine.begin() as conn:
                    await conn.run_sync(lambda _: None)
                self._connected = True
                print(f"[DB] Connected successfully on attempt {attempt}")
                break

            except exc.OperationalError as e:
                print(f"[DB] Connection attempt {attempt} failed: {e}")
                if attempt < max_tries:
                    await asyncio.sleep(delay)
                else:
                    raise RuntimeError(
                        "[DB] Could not connect after max retries"
                    ) from e

    @asynccontextmanager
    async def session(self):
        if not self._connected:
            await self.connect()
        if not self._session_factory:
            raise RuntimeError("[DB] Session factory not initialized.")
        async with self._session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    async def create_all(self) -> None:
        if not self._connected:
            await self.connect()
        engine: AsyncEngine | None = self._engine
        if engine is not None:
            async with engine.begin() as conn:
                await conn.run_sync(_Base.metadata.create_all)
                print("[DB] Tables created successfully.")
        else:
            raise RuntimeError("[DB] Database engine is not initialized")

    async def dispose(self) -> None:
        if self._engine:
            await self._engine.dispose()
            print("[DB] Connection closed.")
        self._connected = False


DB = _Database()

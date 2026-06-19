"""Асинхронный движок SQLAlchemy + SQLite."""
import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.models import Base

engine = create_async_engine(f"sqlite+aiosqlite:///{settings.db_path}")
Session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    """Создаёт папку для БД и таблицы, если их ещё нет."""
    db_dir = os.path.dirname(settings.db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

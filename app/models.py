"""Модели БД."""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    """Настройки пользователя: язык ответа и длина выжимки."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # telegram user id
    lang: Mapped[str] = mapped_column(String(2), default="ru")
    length: Mapped[str] = mapped_column(String(10), default="medium")  # short|medium|detailed
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

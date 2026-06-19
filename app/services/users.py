"""Работа с пользователями в БД."""
from app.db import Session
from app.models import User


async def get_or_create_user(user_id: int) -> User:
    async with Session() as session:
        user = await session.get(User, user_id)
        if user is None:
            user = User(id=user_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user


async def update_user(user_id: int, **fields: str) -> User:
    async with Session() as session:
        user = await session.get(User, user_id)
        if user is None:
            user = User(id=user_id)
            session.add(user)
        for key, value in fields.items():
            setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
        return user

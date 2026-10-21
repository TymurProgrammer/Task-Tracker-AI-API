from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from task_tracker_basics.models import UserORM


async def get_user_by_id(session: AsyncSession, user_id: int) -> UserORM | None:
    return await session.get(UserORM, user_id)


async def get_user_by_email(session: AsyncSession, email: str) -> UserORM | None:
    result = await session.execute(select(UserORM).where(UserORM.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(session: AsyncSession, username: str) -> UserORM | None:
    result = await session.execute(
        select(UserORM).where(UserORM.username == username)
    )
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession, username: str, email: str, hashed_password: str
) -> UserORM:
    user = UserORM(username=username, email=email, hashed_password=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
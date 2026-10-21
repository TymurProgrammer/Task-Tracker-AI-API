from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from task_tracker_basics.models import TaskORM
from task_tracker_basics.schemas import TaskCreate, TaskUpdate


async def create_task(
    session: AsyncSession, user_id: int, data: TaskCreate
) -> TaskORM:
    task = TaskORM(**data.model_dump(), user_id=user_id)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_task(
    session: AsyncSession, task_id: int, user_id: int
) -> TaskORM | None:
    result = await session.execute(
        select(TaskORM).where(TaskORM.id == task_id, TaskORM.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_tasks(
    session: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> list[TaskORM]:
    result = await session.execute(
        select(TaskORM)
        .where(TaskORM.user_id == user_id)
        .order_by(TaskORM.id)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_task(
    session: AsyncSession, task: TaskORM, data: TaskUpdate
) -> TaskORM:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task: TaskORM) -> None:
    await session.delete(task)
    await session.commit()
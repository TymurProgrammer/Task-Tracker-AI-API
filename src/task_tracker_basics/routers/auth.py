from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from task_tracker_basics.schemas import UserCreate
from typing import Annotated
from sqlalchemy.exc import IntegrityError

from task_tracker_basics.database import get_db_session
from task_tracker_basics.schemas import UserResponse
from task_tracker_basics.crud import get_user_by_email, create_user, get_user_by_username
from task_tracker_basics.auth.security import hash_password
from task_tracker_basics.models import UserORM


router = APIRouter(prefix = "/auth", tags = ["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED,)
async def register(
    user: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserORM:

    hashed_password = hash_password(user.password)

    try:
        return await create_user(session, user.username, user.email, hashed_password)
    except IntegrityError as exc:
        await session.rollback()

        if await get_user_by_email(session, user.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            ) from exc
        if await get_user_by_username(session, user.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered",
            ) from exc
        raise
    

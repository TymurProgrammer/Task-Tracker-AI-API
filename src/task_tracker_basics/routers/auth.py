from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from task_tracker_basics.schemas import UserCreate
from sqlalchemy.exc import IntegrityError
import jwt

from task_tracker_basics.database import get_db_session
from task_tracker_basics.schemas import UserResponse, TokenResponse, RefreshRequest
from task_tracker_basics.crud import get_user_by_email, create_user, get_user_by_username, get_user_by_id
from task_tracker_basics.auth.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from task_tracker_basics.models import UserORM


auth_router = APIRouter(prefix = "/auth", tags = ["auth"])

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED,)
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


@auth_router.post("/login", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession,Depends(get_db_session)]
    ) -> TokenResponse:
    
    user = await get_user_by_email(session, form.username)

    login_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="There is no such user or bad password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise login_exception

    if not verify_password(form.password, user.hashed_password):
        raise login_exception
        
    return TokenResponse(
        access_token=create_access_token(user.id), 
        refresh_token=create_refresh_token(user.id))


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshRequest,
    session: Annotated[AsyncSession,Depends(get_db_session)]
    ) -> TokenResponse:

    refresh_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh problem",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = decode_token(request.refresh_token, "refresh")
    except jwt.InvalidTokenError:
        raise refresh_exception

    user = await get_user_by_id(session, user_id)
    if not user:
        raise refresh_exception

    return TokenResponse(
        access_token=create_access_token(user_id), 
        refresh_token=create_refresh_token(user_id))




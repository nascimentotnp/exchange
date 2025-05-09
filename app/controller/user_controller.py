from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repository.user_repository import UserRepository
from app.entities.entity import User
from app.gateways.database.connector import get_db
from app.schemas.user_schema import UserResponse, UserCreate, UserUpdate
from app.utils.auth_deps import get_current_user
from app.utils.config.log import current_user_id, current_username

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/", response_model=UserResponse)
async def create_user(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    try:
        return await repo.create(user_data.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@user_router.get("/me", response_model=UserResponse)
async def read_current_user(
        current_user: User = Depends(get_current_user)
):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int,
        user_data: UserUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other users"
        )
    current_user_id.set(str(current_user.id))
    current_username.set(current_user.username)

    repo = UserRepository(db)
    return await repo.update(user_id, user_data.dict())


@user_router.delete("/{user_id}")
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other users"
        )

    current_user_id.set(str(current_user.id))
    current_username.set(current_user.username)

    repo = UserRepository(db)
    await repo.delete(user_id)
    return {"message": "User deleted successfully"}

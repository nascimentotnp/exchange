from fastapi import APIRouter, Depends

from entities.entity import User
from utils.auth_deps import get_current_user

protected_router = APIRouter()


@protected_router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Hello {current_user.username}",
        "user_id": current_user.id,
        "is_active": current_user.is_active
    }

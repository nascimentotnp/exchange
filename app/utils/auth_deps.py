from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from entities.entity import User, UserSession
from gateways.database.connector import get_db
from sqlalchemy.future import select


async def get_current_user(
        session_id: str = Cookie(None),
        db: AsyncSession = Depends(get_db)
) -> User:
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    result = await db.execute(
        select(UserSession)
        .filter(UserSession.session_id == session_id)
    )
    user_session = result.scalars().first()

    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )

    result = await db.execute(
        select(User)
        .filter(User.id == user_session.user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

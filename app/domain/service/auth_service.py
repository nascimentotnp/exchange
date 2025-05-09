import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status, Response
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repository.user_repository import UserRepository
from app.entities.entity import UserSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def login(self, username: str, password: str, response: Response):
        user = await self.user_repo.find_by_username(username)
        if not user or not pwd_context.verify(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        session_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        user_session = UserSession(
            session_id=session_id,
            user_id=user.id,
            expires_at=expires_at
        )

        self.db.add(user_session)
        await self.db.commit()
        await self.db.refresh(user_session)

        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=3600
        )

        return {
            "user": user,
            "session_id": session_id
        }

import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from entities.entity import User, UserSession
from utils.password import hash_password

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: int):
        try:
            query = select(User).where(User.id == id)
            result = await self.db.execute(query)
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            return user
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
            ) from ex

    async def create(self, user_data: dict):
        try:
            logger.info(f"Trying to create user with data: {user_data}")

            existing_user = await self.db.execute(select(User).where(User.username == user_data["username"]))
            if existing_user.scalars().first():
                logger.warning(f"Username {user_data['username']} already exists.")
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

            user_data["password_hash"] = hash_password(user_data["password_hash"])
            logger.info(f"Password hashed: {user_data['password_hash'][:30]}...")

            user = User(**user_data)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"User {user.username} created successfully")
            return user
        except SQLAlchemyError as ex:
            await self.db.rollback()
            logger.error(f"Error creating user: {str(ex)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
            ) from ex

    async def update(self, id: int, user_data: dict):
        try:
            user = await self.find_by_id(id)
            for key, value in user_data.items():
                setattr(user, key, value)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError as ex:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
            ) from ex

    async def delete(self, id: int):
        try:
            user = await self.find_by_id(id)
            await self.db.delete(user)
            await self.db.commit()
            return {"detail": "User: Deleted Success"}
        except SQLAlchemyError as ex:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
            ) from ex

    async def find_by_username(self, username: str):
        try:
            query = select(User).where(User.username == username)
            result = await self.db.execute(query)
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            return user
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
            ) from ex

    async def find_by_session(self, session_id: str):
        try:
            session = await self.db.execute(
                select(User)
                .join(UserSession, User.id == UserSession.user_id)
                .where(UserSession.session_id == session_id)
            )
            user_session = session.scalars().first()
            user = await self.db.execute(select(User).filter(User.id == user_session.user_id))
            user = user.scalars().first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            if not user_session:
                raise HTTPException(status_code=401, detail="User session not found")
            if user_session.is_expired:
                raise HTTPException(status_code=401, detail="Session expired")

            return user
        except Exception as e:
            logger.error(f"Error finding user by session: {str(e)}")
            return None

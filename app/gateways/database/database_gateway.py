import os
from typing import Any, Type, TypeVar, Optional
from dotenv import load_dotenv
from fastapi import HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from sqlalchemy.orm import DeclarativeBase, declared_attr
from contextlib import asynccontextmanager

load_dotenv()

T = TypeVar('T', bound='Base')


class Base(AsyncAttrs, DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    @asynccontextmanager
    async def get_session(cls):
        async with SessionFactory() as session:
            try:
                yield session
            except SQLAlchemyError as ex:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database error: {str(ex)}"
                )
            finally:
                await session.close()

    async def save(self, db: AsyncSession):
        try:
            db.add(self)
            await db.commit()
            await db.refresh(self)
            return self
        except IntegrityError as ex:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Integrity error: {str(ex)}"
            )
        except SQLAlchemyError as ex:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Database operation failed: {str(ex)}"
            )

    @classmethod
    async def find_by_id(cls: Type[T], db: AsyncSession, id: Any) -> Optional[T]:
        try:
            result = await db.execute(select(cls).where(cls.id == id))
            return result.scalars().first()
        except NoResultFound:
            return None
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(ex)}"
            )

    @classmethod
    async def update(cls: Type[T], db: AsyncSession, id: Any, **kwargs) -> Optional[T]:
        try:
            await db.execute(
                update(cls)
                .where(cls.id == id)
                .values(**kwargs)
            )
            await db.commit()
            return await cls.find_by_id(db, id)
        except IntegrityError as ex:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Integrity error: {str(ex)}"
            )
        except SQLAlchemyError as ex:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Update failed: {str(ex)}"
            )

    @classmethod
    async def delete(cls, db: AsyncSession, id: Any) -> bool:
        try:
            await db.execute(delete(cls).where(cls.id == id))
            await db.commit()
            return True
        except SQLAlchemyError as ex:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Delete failed: {str(ex)}"
            )


USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"
DB_ENGINE = os.getenv("DB_ENGINE", "postgresql").lower()

if USE_SQLITE or DB_ENGINE == "sqlite":
    DB_NAME = os.getenv("DB_NAME", "database")
    DB_URL = f"sqlite+aiosqlite:///./{DB_NAME}.db"
else:
    DB_USER = os.getenv("DB_USERNAME")
    DB_PASS = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")

    if not all([DB_USER, DB_PASS, DB_NAME]):
        raise ValueError("Missing required database configuration in .env file")

    DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(
    DB_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600
)

SessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)

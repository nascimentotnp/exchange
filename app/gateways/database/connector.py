import logging
from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from entities.entity import Base
from gateways.database.database_gateway import engine, SessionFactory

logger = logging.getLogger(__name__)


async def init_db():
    async with engine.begin() as conn:
        try:
            def sync_inspect(connection):
                inspector = inspect(connection)
                return inspector.get_table_names()

            existing_tables = await conn.run_sync(sync_inspect)
            required_tables = [table.name for table in Base.metadata.tables.values()]

            if any(table not in existing_tables for table in required_tables):
                logger.info("Some tables do not exist, creating...")
                await conn.run_sync(Base.metadata.create_all)
            else:
                logger.info("All tables are found.")
        except SQLAlchemyError as ex:
            logger.error(f"Database creation error: {ex}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Database initialization error")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()

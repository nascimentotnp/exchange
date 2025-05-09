import os
import uuid

from dotenv import load_dotenv
from fastapi import HTTPException, status, Depends, Cookie
from fastapi import Response
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from entities.entity import User, UserSession
from gateways.database.connector import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_user_from_cookie(session_id: str = Cookie(None)):
    if session_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return session_id



from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response

from app.domain.service.auth_service import AuthService
from app.entities.entity import UserSession
from app.gateways.database.connector import get_db
from app.schemas.user_schema import UserLogin
from app.utils.config.log import get_logger, current_user_id, current_username

logger = get_logger(__name__)

login_router = APIRouter(prefix="/auth", tags=["auth"])


@login_router.post("/login")
async def login(
        login_request: UserLogin,
        response: Response,
        db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    try:
        login_result = await auth_service.login(
            login_request.username,
            login_request.password,
            response
        )

        logger.info(f"User {login_result['user'].username} logged in successfully")

        current_user_id.set(str(login_result["user"].id))
        current_username.set(login_result["user"].username)
        return {
            "message": "Login successful",
            "user_id": login_result["user"].id,
            "username": login_result["user"].username
        }

    except HTTPException as ex:
        logger.error(f"Login failed for user {login_request.username}: {ex.detail}")
        raise ex


@login_router.post("/logout")
async def logout(
        request: Request,
        response: Response,
        db: AsyncSession = Depends(get_db)
):
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if session_id:
        try:
            result = await db.execute(
                select(UserSession)
                .where(UserSession.session_id == session_id)
            )
            user_session = result.scalars().first()

            if user_session:
                user_session.expires_at = datetime.now(timezone.utc)
                await db.commit()
                logger.info(f"User session expired for session {session_id}")
        except Exception as e:
            logger.error(f"Error expiring session: {str(e)}")
            await db.rollback()

    response.delete_cookie("session_id")

    current_user_id.set("None")
    current_username.set("None")

    return {"message": "Logout successful"}

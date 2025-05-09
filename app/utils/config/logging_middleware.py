import uuid
from fastapi import Request
from app.utils.config.log import correlation_id, current_user_id, current_username, get_logger
from app.gateways.database.connector import SessionFactory
from app.domain.repository.user_repository import UserRepository

logger = get_logger(__name__)


async def logging_middleware(request: Request, call_next):
    correlation_id.set(str(uuid.uuid4()))

    if current_user_id.get() == "system" and request.cookies.get("session_id"):
        try:
            async with SessionFactory() as session:
                user_repo = UserRepository(session)
                user = await user_repo.find_by_session(request.cookies.get("session_id"))
                if user:
                    current_user_id.set(str(user.id))
                    current_username.set(user.username)
                    logger.debug(f"User context set: {user.username}")
        except Exception as e:
            logger.warning(f"Failed to set user context: {str(e)}")

    response = await call_next(request)

    current_user_id.set("system")
    current_username.set("system")

    return response

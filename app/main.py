import asyncio
import uvicorn
from fastapi import FastAPI


import sys
import os

from app.controller.exchange_controller import exchange_router
from app.controller.health_check_controller import health_check_router
from app.controller.login_controller import login_router
from app.controller.transactions_controller import transaction_router
from app.controller.user_controller import user_router
from app.gateways.database.connector import init_db
from app.utils.config.log import setup_logging
from app.utils.config.logging_middleware import logging_middleware

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = setup_logging()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Exchange API",
        version="1.0.0",
        openapi_tags=[
            {"name": "health_check", "description": "System health check operations"},
            {"name": "users", "description": "Users routes"},
            {"name": "auth", "description": "Authorization routes"},
            {"name": "exchange", "description": "Currency conversion operations"},
            {"name": "transaction", "description": "Get conversion operations in a List"}
        ]
    )

    app.middleware("http")(logging_middleware)
    app.include_router(health_check_router)
    app.include_router(exchange_router)
    app.include_router(user_router)
    app.include_router(login_router)
    app.include_router(transaction_router)

    return app


async def start_application():
    logger.info("Starting application initialization")
    await init_db()

    config = uvicorn.Config(
        "main:app",
        host="localhost",
        port=8081,
        reload=True,
        log_config=None
    )

    server = uvicorn.Server(config)
    logger.info("Application started successfully")
    await server.serve()


app = create_app()

if __name__ == "__main__":
    try:
        asyncio.run(start_application())
    except KeyboardInterrupt:
        logger.info("Application shutdown by user")
    except Exception as e:
        logger.critical(f"Application failed to start: {str(e)}")
        raise

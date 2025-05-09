import os

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

health_check_router = APIRouter(prefix="/health", tags=["health_check"])

health_path = os.getenv("HEALTH_CHECK", "health")


@health_check_router.get(f'/{health_path}')
def health_check():
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=jsonable_encoder({"message": "OK"}))

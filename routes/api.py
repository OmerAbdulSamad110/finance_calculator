from fastapi import APIRouter
from app.Http.Responses import ValidationResponse

api_router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={
        404: {"description": "Not found"},
        400: {"model": ValidationResponse},
        422: {"model": None},
    },
)

v1_router = APIRouter(prefix="/v1", tags=["v1"])

# Controllers

routes = []

for path, handler, methods in routes:
    v1_router.add_api_route(path, handler, methods=methods)

api_router.include_router(v1_router)

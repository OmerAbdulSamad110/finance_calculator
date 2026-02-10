from fastapi import FastAPI
from .api import api_router


def setup_routes(app: FastAPI) -> FastAPI:
    app.include_router(api_router)
    return app

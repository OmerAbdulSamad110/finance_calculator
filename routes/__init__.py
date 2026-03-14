from fastapi import FastAPI
from .commands import command_router


def setupRoutes(app: FastAPI):
    app.include_router(command_router)

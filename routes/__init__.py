from fastapi import FastAPI
from .api import registerRoutes
from .commands import command_router


def setupRoutes(app: FastAPI):
    app.include_router(registerRoutes())
    app.include_router(command_router)

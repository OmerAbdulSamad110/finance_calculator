from fastapi import FastAPI
from app.Core.Database import engine
from app.Core.Scheduler import setupScheduler
from app.Core.Logger import setupLogger
from app.Http.Middlewares import setupMiddlewares
from routes import setupRoutes
from .exception.handler import setupExceptions
from contextlib import asynccontextmanager
from app.Core.Mailer import setupMailer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    with setupScheduler():  # ✅ context manager, shutdown runs on exit
        yield
    # Shutdown
    await engine.dispose()


setupLogger()
app = FastAPI(lifespan=lifespan)
setupExceptions(app)
setupMiddlewares(app)
setupMailer(app)
setupRoutes(app)

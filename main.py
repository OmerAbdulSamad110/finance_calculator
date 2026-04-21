from fastapi import FastAPI
from app.Core.Database import engine
from app.Core.Scheduler import setupScheduler
from app.Core.Logger import setupLogger
from app.Http.Middlewares import setupMiddlewares
from routes import setupRoutes
from bootstrap.exception.handler import setupExceptions
from contextlib import asynccontextmanager
from app.Core.Mailer import setupMailer
from app.Core.Redis import setupRedis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with setupRedis():  # ✅ context manager, close runs on exit
        with setupScheduler():  # ✅ context manager, shutdown runs on exit
            yield  # App runs until shutdown signal
    # Shutdown
    await engine.dispose()


setupLogger()
app = FastAPI(lifespan=lifespan)
setupExceptions(app)
setupMiddlewares(app)
setupMailer(app)
setupRoutes(app)

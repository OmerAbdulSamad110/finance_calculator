from fastapi import FastAPI
from app.Core.Database import Base, engine
from app.Console.Scheduler import setupScheduler
from logs.logger import setupLogger
from app.Http.Middlewares import setupMiddlewares
from routes import setupRoutes
from .exception.handler import setupExceptions
from app.Models import *  # Ensure models are imported for table creation
from contextlib import asynccontextmanager
from app.Core.Mailer import setupMailer


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
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

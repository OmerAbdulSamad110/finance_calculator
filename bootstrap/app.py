from fastapi import FastAPI
from app.Http.Middlewares import setupMiddlewares
from routes import setupRoutes
from .exception.handler import setupExceptions
from app.Core.Database import Base, engine
from app.Models import *  # Ensure models are imported for table creation
from contextlib import asynccontextmanager
from app.Core.Mailer import setupMailer


# DO THIS INSTEAD:
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Or if you prefer lifespan (FastAPI 0.93+):


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
setupExceptions(app)
setupMiddlewares(app)
setupMailer(app)
setupRoutes(app)

from fastapi import FastAPI
from app.Http.Middlewares import setup_middlewares
from routes import setup_routes
from .exception.handler import setup_exceptions
from app.Core.Database import Base, engine
from app.Models import *  # Ensure models are imported for table creation
from contextlib import asynccontextmanager


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
app = setup_exceptions(app)
app = setup_middlewares(app)
app = setup_routes(app)

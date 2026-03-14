from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import getAsyncDb
from database.seeders.PermissionSeeder import seedPermissions

command_router = APIRouter(prefix="/commands", tags=["Commands"])


@command_router.get("/seed/permissions")
async def seed_Permissions(db: AsyncSession = Depends(getAsyncDb)):
    return await seedPermissions(db)

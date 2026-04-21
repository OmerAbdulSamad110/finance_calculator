from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import getAsyncDb
from database.seeders.PermissionSeeder import seedPermissions
from database.seeders.FinanceCategorySeeder import seedFinancialCategories
from database.seeders.RoleSeeder import seedRoles

command_router = APIRouter(prefix="/commands", tags=["Commands"])


@command_router.get("/seed/roles")
async def seed_Roles(db: AsyncSession = Depends(getAsyncDb)):
    return await seedRoles(db)


@command_router.get("/seed/permissions")
async def seed_Permissions(db: AsyncSession = Depends(getAsyncDb)):
    return await seedPermissions(db)


@command_router.get("/seed/financial/categories")
async def seed_FinancialCategories(db: AsyncSession = Depends(getAsyncDb)):
    return await seedFinancialCategories(db)

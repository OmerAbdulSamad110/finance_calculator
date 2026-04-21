from sqlalchemy.ext.asyncio import AsyncSession
from app.Http.Responses.JsonResponse import JsonResponse
from app.Models import Role

roles = [
    {"label": "Super Admin", "is_active": True},
    {"label": "Admin", "is_active": True},
    {"label": "Client", "is_active": True},
]


async def seedRoles(db: AsyncSession):
    for role in roles:
        db.add(Role(**role))
    await db.commit()
    return JsonResponse(message="Roles seeded successfully.")

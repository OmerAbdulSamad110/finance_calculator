from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import getAsyncDb
from app.Models.Permission import Permission
from app.Http.Requests.PermissionRequest import PermissionRequest
from app.Http.Responses.PermissionResponse import PermissionDetailResponse
from app.Http.Responses.JsonResponse import JsonResponse
from sqlalchemy.engine import RowMapping
from bootstrap.exception.exceptions import raiseNotFound, raiseUnprocessableContent
from bootstrap.exception.validations import exists


class PermissionController:
    def __init__(self) -> None:
        pass

    async def index(self, db: AsyncSession = Depends(getAsyncDb)) -> JsonResponse:
        query = await db.execute(select(Permission))
        permissions = query.mappings().all()

        list = {
            "permissions": [
                PermissionDetailResponse(**self.__formatPermission(permission))
                for permission in permissions
            ]
        }

        return JsonResponse(data={"list": list})

    async def show(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        query = await db.execute(select(Permission).where(Permission.id == id))
        permission = query.mappings().first()
        if not permission:
            raiseNotFound("Permission not found.")
        return JsonResponse(
            data={
                "permission": PermissionDetailResponse(
                    **self.__formatPermission(permission)
                )
            }
        )

    async def store(
        self, request: PermissionRequest, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        errors: dict = {}
        if request.parent_id is not None and not await exists(
            db, Permission, "parent_id", request.parent_id, {"parent_id": None}
        ):
            errors["parent_id"] = "Invalid parent id selected."
        permission = Permission(**request.model_dump())
        if await exists(db, Permission, "slug", permission.slug):
            errors["slug"] = ["Permission label already exists."]
        if len(permission) > 0:
            raiseUnprocessableContent(errors)
        db.add(permission)
        await db.commit()
        return JsonResponse(message="Permission created successfully.")

    async def update(
        self,
        request: PermissionRequest,
        id: int,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        permission = await self.__findPermissionForWrite(db, id)
        permission.label = request.label
        errors: dict = {}
        if request.parent_id is not None and not await exists(
            db, Permission, "parent_id", request.parent_id, {"parent_id": None}
        ):
            errors["parent_id"] = "Invalid parent id selected."
        if await exists(db, Permission, "slug", permission.slug, {"id__ne", id}):
            errors["slug"] = ["Permission label already exists."]
        if len(permission) > 0:
            raiseUnprocessableContent(errors)
        permission.parent_id = request.parent_id
        await db.commit()
        return JsonResponse(message="Permission updated successfully.")

    async def delete(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        permission = await self.__findPermissionForWrite(db, id)
        await db.delete(permission)
        await db.commit()
        return JsonResponse(message="Permission deleted successfully.")

    def __formatPermission(permission: RowMapping) -> dict:
        return {
            "id": permission["id"],
            "label": permission["label"],
            "slug": permission["slug"],
            "parent_id": permission["parent_id"],
            "created_at": permission["created_at"],
            "updated_at": permission["updated_at"],
        }

    async def __findPermissionForWrite(self, db: AsyncSession, id: int):
        query = await db.execute(select(Permission).where(Permission.id == id))
        permission = query.scalar_one_or_none()
        if not permission:
            raiseNotFound("Permission not found.")
        return permission

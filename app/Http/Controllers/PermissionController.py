from fastapi import Depends
from sqlalchemy import select, or_, asc, desc
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import getAsyncDb
from app.Models.Permission import Permission
from app.Http.Requests.PermissionRequest import PermissionRequest, PermissionFormRequest
from app.Http.Responses.PermissionResponse import PermissionDetailResponse
from app.Http.Responses.JsonResponse import JsonResponse
from sqlalchemy.engine import RowMapping
from bootstrap.exception.exceptions import raiseNotFound, raiseUnprocessableContent
from bootstrap.exception.validations import exists
from app.Http.Requests.DtRequest import DtRequest
from libs.Paginate import paginate
from app.Http.Responses.CommonResponse import SimpleListItemResponse


class PermissionController:
    def __init__(self) -> None:
        pass

    async def index(
        self, request: DtRequest = Depends(), db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        Parent = aliased(Permission)
        query = select(Permission, Parent.label.label("parent_label")).join(
            Parent, Parent.id == Permission.parent_id, isouter=True
        )
        if request.search is not None:
            query = query.where(
                or_(
                    Permission.label.like(f"%{request.search}%"),
                    Parent.label.like(f"%{request.search}%"),
                )
            )
        columns = {"label": Permission.label, "parent.label": Parent.label}
        order_by = Permission.created_at
        if request.order_by is not None:
            order_by = columns.get(request.order_by)
        direction = asc if request.order_dir == "asc" else desc
        query = query.order_by(direction(order_by))

        data = await paginate(db, query, request)
        data.list = [
            PermissionDetailResponse(**self.__formatPermission(permission))
            for permission in data.list
        ]
        return JsonResponse(data={"permissions": data})

    async def list(
        self,
        request: PermissionRequest = Depends(),
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        list_type = request.list_type
        query = select(Permission)
        if list_type == "parent":
            query = query.where(Permission.parent_id == None)
        stmt = await db.execute(query)
        query = query.order_by(asc(Permission.label))
        permissions = stmt.mappings().all()

        if list_type is None:
            list = {
                "permissions": [
                    PermissionDetailResponse(**self.__formatPermission(permission))
                    for permission in permissions
                ]
            }
        elif list_type == "parent":
            list = [
                SimpleListItemResponse(
                    label=permission["Permission"].label,
                    value=str(permission["Permission"].id),
                )
                for permission in permissions
            ]
        elif list_type == "groupedby_parent":
            parents = [
                permission
                for permission in permissions
                if permission["Permission"].parent_id is None
            ]
            list = {}
            for parent in parents:
                list[parent["Permission"].slug] = [
                    {
                        "id": permission["Permission"].id,
                        "label": permission["Permission"].label,
                    }
                    for permission in permissions
                    if permission["Permission"].parent_id == parent["Permission"].id
                ]
        return JsonResponse(data={"list": list})

    async def show(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        stmt = await db.execute(select(Permission).where(Permission.id == id))
        permission = stmt.mappings().first()
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
        self, request: PermissionFormRequest, db: AsyncSession = Depends(getAsyncDb)
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
        request: PermissionFormRequest,
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

    def __formatPermission(self, permission: RowMapping) -> dict:
        item = {
            "id": permission["Permission"].id,
            "label": permission["Permission"].label,
            "slug": permission["Permission"].slug,
            "parent_id": permission["Permission"].parent_id,
            "created_at": permission["Permission"].created_at,
            "updated_at": permission["Permission"].updated_at,
        }
        if "parent_label" in permission:
            item["parent_label"] = permission["parent_label"]
        return item

    async def __findPermissionForWrite(self, db: AsyncSession, id: int):
        stmt = await db.execute(select(Permission).where(Permission.id == id))
        permission = stmt.scalar_one_or_none()
        if not permission:
            raiseNotFound("Permission not found.")
        return permission

from sqlalchemy import select, insert, delete as deleteSql
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import getAsyncDb
from app.Models.Role import Role
from app.Models.Permission import Permission
from app.Http.Requests.RoleRequest import RoleFormRequest
from app.Http.Responses.JsonResponse import JsonResponse
from app.Http.Responses.RoleResponse import RoleDetailResponse
from app.Http.Responses.CommonResponse import SimpleListResponse
from bootstrap.exception.exceptions import raiseUnprocessableContent, raiseNotFound
from bootstrap.exception.validations import exists
from app.Models.PermissionRole import permission_role
from app.Http.Requests.PermissionRequest import PermissionIdsRequest
from app.Http.Requests.DtRequest import CursorPaginateRequest
from libs.Paginate import cursorPaginate


class RoleController:
    def __init__(self) -> None:
        pass

    async def list(
        self,
        request: CursorPaginateRequest = Depends(),
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        data = await cursorPaginate(db, select(Role), request)
        data.list = [
            SimpleListResponse(
                label=role["Role"].label, value=role["Role"].slug
            ).model_dump(exclude_unset=True)
            for role in data.list
        ]
        return JsonResponse(data={"roles": data})

    async def index(
        self, list_only: bool = False, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        query = await db.execute(select(Role))
        roles = query.scalars().all()
        if list_only == False:
            list = {"roles": [RoleDetailResponse(**role.toDict()) for role in roles]}
        else:
            list = [SimpleListResponse(role.label, role.slug) for role in roles]
        return JsonResponse(data={"list": list})

    async def show(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        role = await self.__findRoleForWrite(id, db)
        return JsonResponse(data=RoleDetailResponse(**role.toDict()).model_dump())

    async def store(
        self, request: RoleFormRequest, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        role = Role(**request.model_dump())
        if await exists(db, Role, "slug", role.slug):
            raiseUnprocessableContent({"label": ["Role label already exists."]})
        db.add(role)
        await db.commit()
        return JsonResponse(message="Role created successfully.")

    async def update(
        self,
        request: RoleFormRequest,
        id: int,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        role: Role = await self.__findRoleForWrite(id, db)
        role.label = request.label
        if await exists(db, Role, "slug", role.slug, {"id__ne": id}):
            raiseUnprocessableContent({"label": ["Role label already exists."]})
        role.is_active = request.is_active

        await db.commit()
        return JsonResponse(message="Role updated successfully.")

    async def delete(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        role: Role = await self.__findRoleForWrite(id, db)
        await db.delete(role)
        await db.commit()
        return JsonResponse(message="Role deleted successfully.")

    async def syncRolePermissions(
        self,
        request: PermissionIdsRequest,
        role_id: int,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        if len(request.permission_ids) > 0:
            errors: dict = {}
            role_query = await db.execute(select(Role).where(Role.id == role_id))
            role = role_query.scalar_one_or_none()
            if not role:
                raiseNotFound("Role not found.")
            permissions_query = await db.execute(
                select(Permission.id, Permission.parent_id).where(
                    Permission.id.in_(request.permission_ids)
                )
            )
            permissions = permissions_query.all()
            permission_dict = {perm[0]: perm[1] for perm in permissions}
            permission_id_set = set(request.permission_ids)

            for index, permission_id in enumerate(request.permission_ids):
                if permission_id not in permission_dict:
                    errors[f"permission_ids.{index}"] = (
                        "Invalid permission id selected."
                    )
                elif (
                    permission_dict[permission_id] is not None
                    and permission_dict[permission_id] not in permission_id_set
                ):
                    errors[f"permission_ids.{index}"] = (
                        "Permission parent id must be selected."
                    )

            if errors:
                raiseUnprocessableContent(errors)

            insert_data = [
                {"role_id": role_id, "permission_id": perm_id}
                for perm_id in request.permission_ids
            ]
            async with db.begin_nested():
                await db.execute(
                    deleteSql(permission_role).where(
                        permission_role.c.role_id == role_id
                    )
                )
                await db.execute(insert(permission_role), insert_data)
            await db.commit()
        return JsonResponse(message="Role permissions synced successfully.")

    async def __findRoleForWrite(self, role_col: str | int, db: AsyncSession) -> Role:
        query = await db.execute(
            select(Role).where(
                Role.slug == role_col
                if isinstance(role_col, str)
                else Role.id == role_col
            )
        )
        role = query.scalar_one_or_none()
        if role is None:
            raiseNotFound("Role not found.")
        return role

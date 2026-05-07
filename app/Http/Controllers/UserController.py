from app.Http.Requests.UserRequest import (
    UserStoreRequest,
    UserUpdateInfoRequest,
    UserUpdatePasswordRequest,
)
from app.Http.Responses.UserResponse import UserDetailResponse
from app.Models.User import User
from app.Models.Role import Role
from sqlalchemy import select, or_, asc, desc
from sqlalchemy.engine import RowMapping
from bootstrap.exception.exceptions import raiseUnprocessableContent, raiseNotFound
from bootstrap.exception.validations import exists
from app.Core.Database import getAsyncDb
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.Http.Responses.JsonResponse import JsonResponse
from libs.Paginate import Paginate, PaginationDependency


class UserController:
    def __init__(self) -> None:
        pass

    async def index(
        self, request: PaginationDependency, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        query = select(
            User, Role.label.label("role_label"), Role.slug.label("role_slug")
        ).join(Role, Role.id == User.role_id)
        if request.search is not None:
            query = query.where(
                or_(
                    User.name.like(f"%{request.search}%"),
                    User.email.like(f"%{request.search}%"),
                    Role.label.like(f"%{request.search}%"),
                )
            )
        columns = {
            "name": User.name,
            "email": User.email,
            "is_active": User.is_active,
            "created_at": User.created_at,
            "roles.label": Role.label,
        }
        order_by = User.created_at
        if request.order_by is not None:
            order_by = columns.get(request.order_by)
        direction = asc if request.order_dir == "asc" else desc
        query = query.order_by(direction(order_by))

        data = await Paginate.offset(db, query, request)
        data.list = [
            UserDetailResponse(**self.__formatItem(user)).model_dump(exclude_unset=True)
            for user in data.list
        ]
        return JsonResponse(data={"users": data})

    async def show(
        self, id: int, with_role: bool = False, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        stmt = (
            select(User)
            if not with_role
            else select(
                User, Role.label.label("role_label"), Role.slug.label("role_slug")
            ).join(Role, Role.id == User.role_id)
        )
        query = await db.execute(stmt.where(User.id == id))
        user = query.mappings().first()
        if not user:
            raiseNotFound("User not found.")
        return JsonResponse(
            data=UserDetailResponse(**self.__formatItem(user)).model_dump(
                exclude_unset=True
            )
        )

    async def store(
        self, request: UserStoreRequest, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        errors = {}
        if await exists(db, User, "email", request.email):
            errors["email"] = ["Email already exists."]
        if not await exists(db, Role, "id", request.role_id):
            errors["role_id"] = ["Role does not exist."]
        if len(errors) > 0:
            raiseUnprocessableContent(errors)
        user = User(**request.model_dump())
        db.add(user)
        await db.commit()
        return JsonResponse(message="User created successfully.")

    async def updateInfo(
        self,
        request: UserUpdateInfoRequest,
        id: int,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        errors = {}
        user = await self.__findItemForWrite(id, db)
        if await exists(db, User, "email", request.email, {"id__ne": id}):
            errors["email"] = ["Email already exists."]
        if request.role_id != user.role_id and not await exists(
            db, Role, "id", request.role_id
        ):
            errors["role_id"] = ["Role does not exist."]

        if len(errors) > 0:
            raiseUnprocessableContent(errors)
        user.name = request.name
        user.email = request.email
        user.role_id = request.role_id
        await db.commit()

        return JsonResponse(message=f"User information updated successfully.")

    async def updatePassword(
        self,
        request: UserUpdatePasswordRequest,
        id: int,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        user = await self.__findItemForWrite(id, db)
        if request.password != request.confirm_password:
            raiseUnprocessableContent(
                {"password": ["The password field confirmation does not match."]}
            )
            user.password = request.password
        await db.commit()

        return JsonResponse(message=f"User password updated successfully.")

    async def delete(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        user = await self.__findItemForWrite(id, db)
        await db.delete(user)
        await db.commit()
        return JsonResponse(message="User deleted successfully.")

    async def __findRole(self, role_col: str | int, db: AsyncSession) -> Role:
        query = await db.execute(
            select(Role).where(
                Role.slug == role_col
                if isinstance(role_col, str)
                else Role.id == role_col
            )
        )
        role = query.scalar_one_or_none()
        if not role:
            raiseNotFound("Role not found.")
        return role

    async def __findItemForWrite(self, id: int, db: AsyncSession) -> User:
        query = await db.execute(select(User).where(User.id == id))
        user = query.scalar_one_or_none()
        if user is None:
            raiseNotFound("User not found.")
        return user

    def __formatItem(self, user: RowMapping) -> dict:
        user_dict = {
            "id": user["User"].id,
            "name": user["User"].name,
            "email": user["User"].email,
            "role_id": user["User"].role_id,
            "is_active": user["User"].is_active,
            "created_at": user["User"].created_at,
            "updated_at": user["User"].updated_at,
        }
        if "role_label" in user:
            user_dict["role"] = {
                "id": user["User"].role_id,
                "label": user["role_label"],
                "slug": user["role_slug"],
            }
        return user_dict

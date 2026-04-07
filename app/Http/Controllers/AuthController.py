from fastapi import Request, Depends
from app.Http.Requests.AuthRequest import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.Core.Database import getAsyncDb
from bootstrap.exception.validations import exists
from bootstrap.exception.exceptions import (
    raiseBadRequest,
    raiseUnprocessableContent,
)
from libs.Hash import Hash
from libs.Auth import Auth
from app.Models.User import User
from app.Models.Role import Role
from app.Http.Responses.JsonResponse import JsonResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security
from app.Http.Responses.UserResponse import UserDetailResponse, UserAuthResponse
from bootstrap.config import config

# Use HTTPBearer instead of OAuth2PasswordBearer
security = HTTPBearer()


class AuthController:
    def __init__(self) -> None:
        pass

    async def login(
        self, request: LoginRequest, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        query = await db.execute(select(User).where(User.email == request.email))
        user = query.scalar_one_or_none()
        if (
            user is None
            or Hash.verify(request.password, user.password) is False
            or user.is_active is False
        ):
            raiseUnprocessableContent(
                {
                    "email": [
                        (
                            "User account is disabled."
                            if user is not None and not user.is_active
                            else "Invalid email or password."
                        )
                    ]
                }
            )
        minutes = (
            config("access_token_expire_minutes") if request.remember is False else 60
        )
        access_token = await Auth.createAccessToken(db, user, minutes)
        return JsonResponse(
            message="User logged in successfully.", data=access_token, status=True
        )

    async def register(
        self, request: RegisterRequest, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        errors: dict = {}
        if await exists(db, User, "email", request.email):
            errors["email"] = ["Email already exists."]
        if request.password != request.confirm_password:
            errors["password"] = ["The password field confirmation does not match."]
        query = await db.execute(
            select(Role).where(Role.slug == "client").where(Role.is_active == True)
        )
        if len(errors) > 0:
            raiseUnprocessableContent(errors)
        client_role = query.scalar_one_or_none()
        if client_role is None:
            raiseBadRequest("Client registration is currently closed.")

        user = User(**request.model_dump(exclude=["confirm_password"]))
        user.password = Hash.make(request.password)
        user.role_id = client_role.id
        db.add(user)
        await db.commit()
        return JsonResponse(message="User registered successfully.")

    async def logout(
        self, request: Request, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        user: UserAuthResponse | None = getattr(request.state, "user", None)
        if user is None:
            raiseBadRequest("Token not found.")
        await Auth.deleteToken(db, user.current_token)
        return JsonResponse(message="User logged out successfully.")

    def me(self, request: Request) -> JsonResponse:
        user: UserAuthResponse | None = getattr(request.state, "user", None)
        return JsonResponse(
            data=UserDetailResponse(
                **user, role={"id": user.role_id, "slug": user.role_slug}
            ).model_dump(exclude_unset=True)
        )

    async def forgotPassword(
        self, request: ForgetPasswordRequest, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        if not await exists(db, User, "email", request.email):
            raiseUnprocessableContent({"email": ["Invalid email given."]})
        await Auth.sendPasswordResetLink(db, request.email)
        return JsonResponse(message="Password reset link sent successfully.")

    async def resetPassword(
        self,
        request: ResetPasswordRequest,
        token: str,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        errors: dict = {}
        if not await exists(db, User, "email", request.email):
            errors["email"] = ["Invalid email given."]
        if len(errors) > 0:
            raiseUnprocessableContent(errors)
        if request.password != request.confirm_password:
            errors["password"] = ["The password field confirmation does not match."]
        if len(errors) > 0:
            raiseUnprocessableContent(errors)
        await Auth.resetPassword(db, token, request.email, request.password)
        return JsonResponse(message="Password reseted successfully.")

    def verify(self, request: Request):
        return {"message": "user verify email"}

    async def refreshToken(
        self,
        refresh_token: str,
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        token = await Auth.refreshToken(db, refresh_token, credentials.credentials)
        return JsonResponse(
            message="Token refreshed successfully.",
            data=token,
        )

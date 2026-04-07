from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from bootstrap.config import config
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.User import User
from app.Models.Role import Role
from app.Models.Permission import Permission
from app.Models.PermissionRole import permission_role
from app.Models.PasswordResetToken import PasswordResetToken
from app.Models.PersonalAccessToken import PersonalAccessToken
from sqlalchemy import select, update, delete, func
from app.Http.Responses.UserResponse import UserAuthResponse
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.engine import RowMapping
from app.Http.Responses.AccessTokenResponse import (
    GenerateAccessTokenResponse,
    AccessTokenResponse,
)
from bootstrap.exception.exceptions import (
    raiseNotFound,
    raiseBadRequest,
    raiseUnauthenticated,
    raiseUnprocessableContent,
)
from bootstrap.exception.validations import exists
from app.Core.Mailer import mailer
from app.Mail.ForgetPasswordMail import ForgetPasswordMail
from libs.Hash import Hash


class Auth:

    @staticmethod
    async def createAccessToken(
        db: AsyncSession,
        user: User | str,
        minutes: int,
        abilities: list = ["*"],
    ) -> AccessTokenResponse:
        if isinstance(user, str):
            query = await db.execute(select(User).where(User.email == user))
            user = query.scalar_one_or_none()
            if user is None:
                raise raiseNotFound("User not found.")

        jti = str(uuid4())
        access_token = Auth.__generateToken(
            {
                "refresh_jiti": jti,
                "sub": user.email,
                "type": "access",
                "abilities": abilities,
                "minutes": minutes,
            },
            timedelta(minutes=minutes),
        )
        refresh_token = Auth.__generateToken(
            {
                "sub": user.email,
                "type": "refresh",
                "jti": jti,
            },
            timedelta(hours=1),
        )
        pat = PersonalAccessToken(
            user_id=user.id,
            token=jti,
            expires_at=refresh_token.expires_at,
        )
        db.add(pat)
        await db.commit()
        return AccessTokenResponse(
            access_token=access_token.token,
            refresh_token=refresh_token.token,
            expires_at=access_token.expires_at,
        )

    @staticmethod
    async def getUser(db: AsyncSession, token: str) -> UserAuthResponse:
        try:
            payload = Auth.__decodeToken(token)
            username: str = payload["sub"]
            if username is None or payload["type"] != "access":
                raiseUnauthenticated()
        except jwt.ExpiredSignatureError:
            raiseBadRequest("Access token has expired.")
        except JWTError:
            raiseUnauthenticated()
        query = await db.execute(
            select(User, Role.label.label("role_label"), Role.slug.label("role_slug"))
            .join(Role, Role.id == User.role_id)
            .where(User.email == username)
        )
        user = query.mappings().first()
        if user is None:
            raiseUnauthenticated()
        return Auth.__formatUserData(user, token)

    @staticmethod
    async def refreshToken(
        db: AsyncSession,
        refresh_token: str,
        token: str,
    ) -> AccessTokenResponse:
        try:
            refresh_payload = Auth.__decodeToken(refresh_token)
            access_payload = Auth.__decodeToken(token, False)
            jti = refresh_payload["jti"]
            if (
                jti is None
                or refresh_payload["type"] != "refresh"
                or refresh_payload["sub"] is None
                or refresh_payload["jti"] != access_payload["refresh_jiti"]
            ):
                raiseUnauthenticated()
        except jwt.ExpiredSignatureError:
            raiseBadRequest("Refresh token has expired.")
        except JWTError:
            raiseUnauthenticated()
        access_exp = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)
        if datetime.now(timezone.utc).__gt__(access_exp):
            raiseBadRequest("Access token has not expired yet.")
        if not await exists(
            db,
            PersonalAccessToken,
            "token",
            jti,
            {"expires_at__gt": datetime.now(timezone.utc)},
        ):
            raiseUnauthenticated()

        access_token: GenerateAccessTokenResponse = Auth.__generateToken(
            {
                "refresh_jiti": jti,
                "sub": access_payload["sub"],
                "type": "access",
                "abilities": access_payload["abilities"],
                "minutes": access_payload["minutes"],
            },
            timedelta(minutes=access_payload["minutes"]),
        )
        return AccessTokenResponse(
            access_token=access_token.token,
            refresh_token=refresh_token,
            expires_at=access_token.expires_at,
        ).model_dump(exclude=["refresh_token"])

    @staticmethod
    async def deleteToken(db: AsyncSession, token: str) -> None:
        try:
            access_payload = Auth.__decodeToken(token)
        except jwt.ExpiredSignatureError:
            raiseBadRequest("Access token has expired.")
        except JWTError:
            raiseUnauthenticated()
        await db.execute(
            delete(PersonalAccessToken).where(
                PersonalAccessToken.token == access_payload["refresh_jiti"]
            )
        )
        await db.commit()

    @staticmethod
    async def sendPasswordResetLink(db: AsyncSession, email: str) -> None:
        if not await exists(db, User, "email", email):
            raiseBadRequest("User does not exist.")
        query = await db.execute(
            select(PasswordResetToken).where(PasswordResetToken.email == email)
        )
        current_reset_token = query.scalar_one_or_none()
        if current_reset_token is not None:
            try:
                Auth.__decodeToken(current_reset_token.token, False)
                raiseUnprocessableContent(
                    {"email": ["Password reset link already sent."]}
                )
            except jwt.ExpiredSignatureError or JWTError:
                await db.execute(
                    delete(PasswordResetToken).where(PasswordResetToken.email == email)
                )
                await db.commit()

        reset_token = Auth.__generateToken(
            {
                "sub": email,
                "type": "password_reset",
            },
            timedelta(hours=1),
        )
        prt = PasswordResetToken(
            email=email,
            token=reset_token.token,
            created_at=datetime.now(timezone.utc),
        )
        db.add(prt)
        await db.commit()
        await mailer.send(ForgetPasswordMail(prt.token).to(prt.email))

    @staticmethod
    async def resetPassword(db: AsyncSession, token: str, email: str, password: str):
        errors: dict = {}
        try:
            payload = Auth.__decodeToken(token)
        except jwt.ExpiredSignatureError or JWTError:
            errors["email"] = ["Invalid password reset link."]
        if payload["sub"] != email or payload["type"] != "password_reset":
            errors["email"] = ["Invalid email given."]
        if len(errors) > 0:
            raiseUnprocessableContent(errors)
        await db.execute(
            update(User).where(User.email == email).values(password=Hash.make(password))
        )
        await db.execute(
            delete(PasswordResetToken).where(PasswordResetToken.email == email)
        )
        await db.commit()

    @staticmethod
    async def hasPermission(
        db: AsyncSession, user: UserAuthResponse, permissions: list, match_any: bool
    ) -> bool:
        if user.role_slug == "super_admin":
            return True
        query = await db.execute(
            select(func.count())
            .select_from(Permission)
            .join(
                permission_role,
                permission_role.c.permission_id == Permission.id,
            )
            .where(
                permission_role.c.role_id == user.role_id,
                Permission.slug.in_(permissions),
            )
        )
        # query = await db.execute(
        #     select(
        #         (Role.slug == "super_admin").label("is_super"),
        #         func.count(Permission.id).label("perm_count"),
        #     )
        #     .select_from(Role)
        #     .outerjoin(permission_role, permission_role.c.role_id == Role.id)
        #     .outerjoin(
        #         Permission,
        #         and_(
        #             permission_role.c.permission_id == Permission.id,
        #             Permission.slug.in_(permissions),
        #         ),
        #     )
        #     .where(Role.id == user.role_id)
        #     .group_by(Role.id)
        # )
        # row = query.one_or_none()
        # if row is None:
        #     return False
        # is_super, perm_count = row
        perm_count = query.scalar()
        return len(permissions) == perm_count or (match_any and perm_count > 0)

    @staticmethod
    def __generateToken(
        data: dict,
        time_delta: timedelta,
    ) -> GenerateAccessTokenResponse:
        to_encode = data.copy()
        to_encode.update({"exp": datetime.now(timezone.utc) + time_delta})
        return GenerateAccessTokenResponse(
            token=jwt.encode(
                to_encode,
                config("secret_key"),
                algorithm=config("algorithm"),
            ),
            expires_at=to_encode["exp"],
        )

    @staticmethod
    def __decodeToken(token: str, check_expiration: bool = True) -> dict:
        payload = jwt.decode(
            token,
            config("secret_key"),
            algorithms=[config("algorithm")],
            options={"verify_exp": check_expiration},
        )
        return payload

    @staticmethod
    def __formatUserData(user: RowMapping, token: str) -> UserAuthResponse:
        return UserAuthResponse(
            id=user["User"].id,
            name=user["User"].name,
            email=user["User"].email,
            role_id=user["User"].role_id,
            role_slug=user["role_slug"],
            is_active=user["User"].is_active,
            created_at=user["User"].created_at,
            updated_at=user["User"].updated_at,
            current_token=token,
        )

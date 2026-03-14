from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import getAsyncDb
from libs.Auth import Auth
from bootstrap.exception.exceptions import raiseUnauthenticated, raiseUnauthorized
from app.Http.Middlewares.AuthMiddleware import handle as auth


def can(permissions: list | str, match_any: bool = False):
    _permissions = [permissions] if isinstance(permissions, str) else permissions

    async def handle(
        request: Request,
        db: AsyncSession = Depends(getAsyncDb),
        _: None = Depends(auth),  # enforces auth runs first
    ):
        """Dependency that requires authentication"""
        user = getattr(request.state, "user", None)
        if user is None:
            raiseUnauthenticated()
        if not await Auth.hasPermission(db, user, _permissions, match_any):
            raiseUnauthorized()

    return handle

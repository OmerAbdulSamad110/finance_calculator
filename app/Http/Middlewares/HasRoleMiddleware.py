from fastapi import Request, Depends
from bootstrap.exception.exceptions import raiseUnauthenticated, raiseUnauthorized
from app.Http.Middlewares.AuthMiddleware import handle as auth
from app.Http.Responses.UserResponse import UserAuthResponse


def has(roles: list | str):
    _roles = [roles] if isinstance(roles, str) else roles

    async def handle(
        request: Request,
        _: None = Depends(auth),  # enforces auth runs first
    ):
        """Dependency that requires authentication"""
        user: UserAuthResponse = getattr(request.state, "user", None)
        if user is None:
            raiseUnauthenticated()
        if user.role_slug not in _roles:
            raiseUnauthorized()

    return handle

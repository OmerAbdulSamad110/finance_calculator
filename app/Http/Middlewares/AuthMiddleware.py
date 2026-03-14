from fastapi import Request, Security, Depends
from bootstrap.exception.exceptions import raiseUnauthenticated
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.Core.Database import getAsyncDb
from libs.Auth import Auth

# Use HTTPBearer instead of OAuth2PasswordBearer
security = HTTPBearer()


# ✅ Use HTTPBearer
async def handle(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(getAsyncDb),
):
    """Dependency that requires authentication"""
    token = credentials.credentials
    if token is None:
        raiseUnauthenticated()
    user = await Auth.getUser(db, token)
    if user is None:
        raiseUnauthenticated()
    request.state.user = user  # Inject into request

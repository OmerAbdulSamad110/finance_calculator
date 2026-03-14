from pydantic import BaseModel
from datetime import datetime


class GenerateAccessTokenResponse(BaseModel):
    token: str
    expires_at: datetime


class AccessTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime

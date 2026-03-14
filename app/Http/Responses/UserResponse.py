from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from .RoleResponse import RoleSimpleResponse


class UserDetailResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role: Optional[RoleSimpleResponse] = None


class UserAuthResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    role_id: int
    role_slug: str
    created_at: datetime
    updated_at: datetime
    current_token: str


class UserDetailListResponse(BaseModel):
    List[UserDetailResponse]

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class RoleDetailResponse(BaseModel):
    id: int
    label: str
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoleDetailListResponse(BaseModel):
    List[RoleDetailResponse]


class RoleSimpleResponse(BaseModel):
    id: int
    label: Optional[str]
    slug: str


class RoleSimpleListResponse(BaseModel):
    List[RoleSimpleResponse]

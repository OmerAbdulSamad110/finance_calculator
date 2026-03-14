from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PermissionDetailResponse(BaseModel):
    id: int
    label: str
    slug: str
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class PermissionListResponse(BaseModel):
    List[PermissionDetailResponse]

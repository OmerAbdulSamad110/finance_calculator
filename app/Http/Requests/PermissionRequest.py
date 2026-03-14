from pydantic import BaseModel, Field
from typing import Optional, List


class PermissionRequest(BaseModel):
    label: str = Field(min_length=3, max_length=100)
    parent_id: Optional[int] = Field(default=None, ge=1)  # equivalent to min:1


class PermissionIdsRequest(BaseModel):
    permission_ids: List[int]

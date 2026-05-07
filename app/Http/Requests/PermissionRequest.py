from pydantic import BaseModel, Field
from typing import Optional, List, Literal

LIST_TYPE = Literal["parent", "groupedby_parent"]


class PermissionFormRequest(BaseModel):
    label: str = Field(min_length=3, max_length=100)
    parent_id: Optional[int] = Field(default=None, ge=1)  # equivalent to min:1


class PermissionIdsRequest(BaseModel):
    permission_ids: List[int]


class PermissionRequest(BaseModel):
    list_type: Optional[LIST_TYPE] = Field(
        default=None, description="Permission list type"
    )

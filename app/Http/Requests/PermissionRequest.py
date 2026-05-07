from pydantic import BaseModel, Field
from typing import Optional, List, Literal

LIST_TYPE = Literal["parent", "groupedby_parent"]


class PermissionFormRequest(BaseModel):
    label: str = Field(
        min_length=3,
        max_length=100,
        title="Permission label",
        description="Label of the permission",
    )
    parent_id: Optional[int] = Field(
        default=None,
        ge=1,
        title="Parent permission id",
        description="Parent permission id, if null then it is a parent permission",
    )  # equivalent to min:1


class PermissionIdsRequest(BaseModel):
    permission_ids: List[int]


class PermissionRequest(BaseModel):
    list_type: Optional[LIST_TYPE] = Field(
        default=None, description="Permission list type"
    )

from pydantic import BaseModel, Field


class RoleFormRequest(BaseModel):
    label: str = Field(min_length=3, max_length=100)
    is_active: bool = True

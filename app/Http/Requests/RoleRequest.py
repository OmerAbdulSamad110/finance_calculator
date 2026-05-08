from pydantic import BaseModel, Field


class RoleFormRequest(BaseModel):
    label: str = Field(
        required=True,
        min_length=3,
        max_length=100,
        title="Role label",
        description="The label of the role.",
    )
    permissions: dict[str, list[int]] = Field(
        required=True,
        title="Permissions grouped by parent slug",
        description="A dictionary where the keys are parent slug names and the values are lists of permission IDs.",
    )
    is_active: bool = Field(
        required=False,
        default=True,
        title="Is active",
        description="Indicates whether the role is active.",
    )

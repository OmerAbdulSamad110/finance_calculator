from pydantic import BaseModel, EmailStr, Field


class UserStoreRequest(BaseModel):
    name: str = Field(
        required=True,
        min_length=3,
        max_length=255,
        title="User name",
        description="The name of the user.",
    )
    email: EmailStr = Field(
        required=True,
        max_length=255,
        title="User email",
        description="The email address of the user.",
    )
    password: str = Field(
        required=True,
        min_length=8,
        max_length=255,
        title="User password",
        description="The password of the user.",
    )
    role_id: int = Field(
        required=True,
        gt=0,
        title="Role ID",
        description="The ID of the role assigned to the user.",
    )
    is_active: bool = True


class UserUpdateInfoRequest(BaseModel):
    name: str = Field(
        required=True,
        min_length=3,
        max_length=255,
        title="User name",
        description="The name of the user.",
    )
    email: EmailStr = Field(
        required=True,
        max_length=255,
        title="User email",
        description="The email address of the user.",
    )
    role_id: int = Field(
        required=True,
        gt=0,
        title="Role ID",
        description="The ID of the role assigned to the user.",
    )
    is_active: bool = True


class UserUpdatePasswordRequest(BaseModel):
    password: str = Field(
        required=True,
        min_length=8,
        max_length=255,
        title="User password",
        description="The password of the user.",
    )
    confirm_password: str = Field(
        required=True,
        min_length=8,
        max_length=255,
        title="Confirm password",
        description="The confirmation of the user's password.",
    )

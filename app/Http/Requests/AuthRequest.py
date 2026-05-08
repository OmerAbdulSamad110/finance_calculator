from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
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
        title="Password",
        description="The password of the user.",
    )
    remember: bool = Field(
        default=False,
        title="Remember me",
        description="Indicates whether to remember the user.",
    )


class RegisterRequest(BaseModel):
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
        title="Password",
        description="The password of the user.",
    )
    confirm_password: str = Field(
        required=True,
        min_length=8,
        max_length=255,
        title="Confirm password",
        description="The confirmation of the user's password.",
    )


class ForgetPasswordRequest(BaseModel):
    email: EmailStr = Field(
        required=True,
        max_length=255,
        title="User email",
        description="The email address of the user.",
    )


class ResetPasswordRequest(ForgetPasswordRequest):
    password: str = Field(
        required=True,
        min_length=8,
        max_length=255,
        title="Password",
        description="The password of the user.",
    )
    confirm_password: str = Field(
        required=True,
        min_length=8,
        max_length=255,
        title="Confirm password",
        description="The confirmation of the user's password.",
    )

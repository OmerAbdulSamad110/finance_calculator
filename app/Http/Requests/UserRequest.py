from typing import Annotated, Literal
from pydantic import BaseModel, EmailStr, Field


class UserStoreRequest(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)
    role_id: int = Field(gt=0)
    is_active: bool = True


class UserUpdateInfoRequest(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    email: EmailStr = Field(max_length=255)
    role_id: int = Field(gt=0)
    is_active: bool = True


class UserUpdatePasswordRequest(BaseModel):
    password: str = Field(min_length=8, max_length=255)
    confirm_password: str = Field(min_length=8, max_length=255)

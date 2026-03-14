from pydantic import BaseModel, Field
from typing import Optional, Literal

ORDER_DIR = Literal["asc", "desc"]


class PaginateRequest(BaseModel):
    page: int = Field(default=1, ge=1, description="Requested page number")
    list_size: int = Field(
        default=10,
        ge=10,
        le=100,
        description="Requested number of items per page",
    )


class CursorPaginateRequest(BaseModel):
    cursor: Optional[str] = Field(default=None, description="Cursor for pagination")
    list_size: int = Field(
        default=10,
        ge=10,
        le=100,
        description="Requested number of items per page",
    )
    order_by: Optional[str] = Field(default="id", description="Order by field")
    order_dir: ORDER_DIR = Field(default="asc", description="Order direction")


class DtRequest(PaginateRequest):
    search: Optional[str] = Field(default=None, description="Search term")
    order_by: Optional[str] = Field(default=None, description="Order by field")
    order_dir: ORDER_DIR = Field(default="asc", description="Order direction")

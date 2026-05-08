from pydantic import BaseModel, Field
from typing import Optional, Literal

ORDER_DIR = Literal["asc", "desc"]


class PaginateRequest(BaseModel):
    page: int = Field(
        default=1, ge=1, title="Page number", description="Requested page number"
    )
    list_size: int = Field(
        default=10,
        ge=10,
        le=100,
        title="List size",
        description="Requested number of items per page",
    )


class CursorPaginateRequest(BaseModel):
    cursor: Optional[str] = Field(
        default=None, title="Cursor", description="Cursor for pagination"
    )
    list_size: int = Field(
        default=10,
        ge=10,
        le=100,
        title="List size",
        description="Requested number of items per page",
    )
    order_by: Optional[str] = Field(
        default="id", title="Order by field", description="Order by field"
    )
    order_dir: ORDER_DIR = Field(
        default="asc", title="Order direction", description="Order direction"
    )


class DtRequest(PaginateRequest):
    search: Optional[str] = Field(
        default=None, title="Search term", description="Search term"
    )
    order_by: Optional[str] = Field(
        default=None, title="Order by field", description="Order by field"
    )
    order_dir: ORDER_DIR = Field(
        default="asc", title="Order direction", description="Order direction"
    )

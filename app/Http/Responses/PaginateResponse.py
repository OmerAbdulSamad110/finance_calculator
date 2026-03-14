from pydantic import BaseModel
from typing import List, Optional


class __PaginateResponse(BaseModel):
    list: List
    total_items: int


class PaginateResponse(__PaginateResponse):
    current_page: int
    next_page: Optional[int]
    prev_page: Optional[int]


class CursorPaginateResponse(__PaginateResponse):
    cursor: Optional[str]
    has_more: bool

from typing import Annotated, TypeVar
from fastapi import Depends
from sqlalchemy.sql import func
from sqlmodel import SQLModel, select, asc, desc
from sqlmodel.sql.expression import SelectOfScalar
from sqlalchemy.ext.asyncio import AsyncSession
from app.Http.Requests.DtRequest import PaginateRequest, CursorPaginateRequest
from app.Http.Responses.PaginateResponse import PaginateResponse, CursorPaginateResponse
from libs.Encryption import encode, decode

T = TypeVar("T", bound=SQLModel)


async def __getItemsCount(
    db: AsyncSession,
    query: SelectOfScalar[T],  # SQLModel select query
) -> int:
    # Get the total number of items
    total_items = await db.scalar(select(func.count()).select_from(query.subquery()))
    assert isinstance(
        total_items, int
    ), "A database error occurred when getting `total_items`"

    return total_items


async def paginate(
    db: AsyncSession,
    query: SelectOfScalar[T],  # SQLModel select query
    paginate_request: PaginateRequest,
) -> PaginateResponse:
    """Paginate the given query based on the pagination input."""
    # Get the total number of items
    total_items = await __getItemsCount(db, query)
    # Handle out-of-bounds page requests by going to the last page instead of displaying
    # empty data.
    total_pages = (
        total_items + paginate_request.list_size - 1
    ) // paginate_request.list_size
    # we don't want to have 0 page even if there is no item.
    total_pages = max(total_pages, 1)
    current_page = min(paginate_request.page, total_pages)

    # description = query.column_descriptions[0]
    # Calculate the offset for pagination
    offset = (current_page - 1) * paginate_request.list_size

    # Apply limit and offset to the query
    result = await db.execute(query.offset(offset).limit(paginate_request.list_size))

    # Fetch the paginated items
    temp = list(result.mappings().all())

    # Return the paginated response using the Page model
    return PaginateResponse(
        list=temp,
        current_page=paginate_request.page,
        next_page=None if current_page == total_pages else current_page + 1,
        prev_page=None if current_page == 1 else current_page - 1,
        total_pages=total_pages,
        total_items=total_items,
    )


async def cursorPaginate(
    db: AsyncSession, query: SelectOfScalar[T], paginate_request: CursorPaginateRequest
) -> CursorPaginateResponse:

    total_items = await __getItemsCount(db, query)
    if total_items == 0:
        return CursorPaginateResponse(
            list=[], total_items=0, cursor=None, has_more=False
        )
    order_by = paginate_request.order_by or "id"
    order_dir = paginate_request.order_dir or "asc"
    list_size = paginate_request.list_size
    cursor_value = None

    # Decode cursor — overrides order params from request
    if paginate_request.cursor is not None:
        try:
            cursor_value = decode(
                paginate_request.cursor, f"{order_by}|{order_dir}|{list_size}"
            )
        except ValueError:
            cursor_value = None

    # Validate sort column
    entity = query.column_descriptions[0]["entity"]
    if not hasattr(entity, order_by):
        raise ValueError(f"Invalid order_by: {order_by}")

    column = getattr(entity, order_by)
    direction = asc if order_dir == "asc" else desc

    # Apply cursor filter with tiebreaker on id
    if cursor_value is not None:
        condOp = column.__ge__ if order_dir == "asc" else column.__le__
        query = query.where(condOp(cursor_value))

    query = query.order_by(direction(column)).limit(list_size + 1)

    result = await db.execute(query)
    items = list(result.mappings().all())

    has_more = False
    next_cursor = None
    last_item = items.pop() if len(items) > list_size else None
    if last_item is not None:
        next_cursor_value = getattr(last_item[entity.__name__], order_by)
        if next_cursor_value is None:
            raise ValueError(f"Invalid order_by: {order_by}")
        has_more = True
        next_cursor = encode(next_cursor_value, f"{order_by}|{order_dir}|{list_size}")

    return CursorPaginateResponse(
        list=items,
        total_items=total_items,
        cursor=next_cursor,
        has_more=has_more,
    )


PaginationDep = Annotated[PaginateRequest, Depends()]

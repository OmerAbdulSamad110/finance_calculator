from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy import select, exists as sqlExists
from app.Models import Model


async def exists(
    db: AsyncSession, model: Model, key: str, value: str, filters: Optional[dict] = None
) -> bool:
    operators = {
        "eq": lambda c, v: c == v,
        "ne": lambda c, v: c != v,
        "lt": lambda c, v: c < v,
        "lte": lambda c, v: c <= v,
        "gt": lambda c, v: c > v,
        "gte": lambda c, v: c >= v,
    }
    column = getattr(model, key)
    stmt = select(sqlExists().where(column == value))
    if filters is not None:
        for key, value in filters.items():
            if "__" not in key:
                field = key
                op = "eq"
            else:
                field, op = key.split("__")
            if op not in operators:
                raise ValueError(f"Invalid operator: {op}")

            column = getattr(model, field)
            stmt = stmt.where(operators[op](column, value))
    return bool(await db.scalar(stmt))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists as sqlExists, or_
from app.Models import Model
from fastapi import UploadFile
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
from typing import Optional, List


async def exists(
    db: AsyncSession,
    model: Model,
    key: str,
    value: str | int,
    filters: Optional[dict] = None,
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
    query = select(sqlExists().where(column == value))
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
            query = query.where(operators[op](column, value))
    return bool(await db.scalar(query))


async def fieldsExists(
    db: AsyncSession, model: Model, data: dict, id: Optional[int] = None
) -> List[str]:
    fields = []
    conditions = [
        getattr(model, field) == value
        for field, value in data.items()
        if value is not None
    ]
    query = select(model).where(or_(*conditions))
    if id is not None:
        query = query.where(getattr(model, "id") != id)
    stmt = await db.execute(query)
    rows = stmt.scalars().all()

    for row in rows:
        for field, value in data.items():
            if getattr(row, field) == value:
                fields.append(field)
    return fields


async def fileMaxSize(file: UploadFile, max_size: int) -> bool:
    return len(await file.read()) > max_size


def isUrl(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def isNumber(value: str, integer: bool) -> bool:
    try:
        if integer:
            int(value)
        else:
            float(value)
        return True
    except ValueError:
        return False


async def isImage(file: UploadFile) -> bool:
    contents = await file.read()
    try:
        Image.open(BytesIO(contents)).verify()
        return True
    except Exception:
        return False


def validateMimes(file: UploadFile, mimes: list[str]) -> bool:
    extension = str(file.filename).split(".")[-1]
    return extension in mimes

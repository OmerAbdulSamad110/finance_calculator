from fastapi import Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import RowMapping, select, text, or_, asc, desc
from datetime import datetime
from app.Enums.FinancialFrequency import FinancialRecurringFrequency
from app.Models.RecurringFinancialEntry import RecurringFinancialEntry
from app.Models.FinancialCategory import FinancialCategory
from app.Core.Database import getAsyncDb
from app.Http.Requests.DtRequest import DtRequest
from app.Http.Responses.UserResponse import UserAuthResponse
from app.Http.Responses.JsonResponse import JsonResponse
from libs.Paginate import Paginate, PaginationDependency
from app.Http.Responses.RecurringFinancialEntryResponse import (
    RecurringFinancialEntryDetailResponse,
)
from app.Http.Requests.RecurringFinancialEntryRequest import (
    RecurringFinancialEntryStoreRequest,
)
from bootstrap.exception.validations import exists
from bootstrap.exception.exceptions import raiseUnprocessableContent, raiseNotFound


class RecurringFinancialEntryController:
    def __init__(self) -> None:
        pass

    async def index(
        self,
        request: Request,
        payload: PaginationDependency,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        user: UserAuthResponse = getattr(request.state, "user")
        query = select(RecurringFinancialEntry)
        if payload.search is not None:
            query = query.where(RecurringFinancialEntry.client_id == user.id).where(
                or_(
                    RecurringFinancialEntry.title.like(f"%{payload.search}%"),
                    RecurringFinancialEntry.amount.like(f"%{payload.search}%"),
                    RecurringFinancialEntry.description.like(f"%{payload.search}%"),
                    RecurringFinancialEntry.frequency.like(f"%{payload.search}%"),
                    text(
                        "DATE_FORMAT(generate_at, '%d-%m-%Y') LIKE :search"
                    ).bindparams(search=f"%{payload.search}%"),
                    text(
                        "DATE_FORMAT(created_at, '%d-%m-%Y %I:%i %p') LIKE :search"
                    ).bindparams(search=f"%{payload.search}%"),
                )
            )
        columns = {
            "title": RecurringFinancialEntry.title,
            "amount": RecurringFinancialEntry.amount,
            "description": RecurringFinancialEntry.description,
            "frequency": RecurringFinancialEntry.frequency,
            "is_active": RecurringFinancialEntry.is_active,
            "generate_at": RecurringFinancialEntry.generate_at,
            "created_at": RecurringFinancialEntry.created_at,
        }
        order_by = RecurringFinancialEntry.created_at
        if payload.order_by is not None:
            order_by = columns.get(payload.order_by)
        direction = asc if payload.order_dir == "asc" else desc
        query = query.order_by(direction(order_by))

        data = await Paginate.offset(db, query, payload)
        data.list = [self.__formatEntryData(entry) for entry in data.list]
        return JsonResponse(data={"recurring_entries": data})

    async def store(
        self,
        request: Request,
        payload: RecurringFinancialEntryStoreRequest,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        user: UserAuthResponse = getattr(request.state, "user")
        if not await exists(db, FinancialCategory, "id", payload.financial_category_id):
            return raiseUnprocessableContent(
                {"financial_category_id": ["Invalid financial category id given."]}
            )
        if await exists(
            db,
            RecurringFinancialEntry,
            "title",
            payload.title,
            {
                "client_id": user.id,
                "financial_category_id": payload.financial_category_id,
                "is_active": True,
            },
        ):
            return raiseUnprocessableContent({"title": ["Title already exists."]})
        entry = RecurringFinancialEntry(**payload.model_dump(), client_id=user.id)
        db.add(entry)
        await db.commit()
        return JsonResponse(message="Recurring financial entry created successfully.")

    async def update(
        self,
        id: int,
        request: Request,
        payload: RecurringFinancialEntryStoreRequest,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        user: UserAuthResponse = getattr(request.state, "user")
        query = await db.execute(
            select(RecurringFinancialEntry)
            .where(RecurringFinancialEntry.id == id)
            .where(RecurringFinancialEntry.client_id == user.id)
        )
        entry = query.scalar_one_or_none()
        if entry is None:
            return raiseNotFound("Recurring financial entry not found.")
        if not await exists(db, FinancialCategory, "id", payload.financial_category_id):
            return raiseUnprocessableContent(
                {"financial_category_id": ["Invalid financial category id given."]}
            )
        if exists(
            db,
            RecurringFinancialEntry,
            "title",
            payload.title,
            {
                "client_id": user.id,
                "financial_category_id": entry.financial_category_id,
                "is_active": True,
                "id__ne": id,
            },
        ):
            return raiseUnprocessableContent({"title": ["Title already exists."]})
        entry.title = payload.title
        entry.amount = payload.amount
        entry.description = payload.description
        entry.frequency = payload.frequency
        entry.generate_at = payload.generate_at
        entry.financial_category_id = payload.financial_category_id
        entry.is_active = payload.is_active
        await db.commit()
        return JsonResponse(message="Recurring financial entry updated successfully.")

    async def delete(
        self,
        request: Request,
        id: int,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        user: UserAuthResponse = getattr(request.state, "user")
        query = await db.execute(
            select(RecurringFinancialEntry)
            .where(RecurringFinancialEntry.id == id)
            .where(RecurringFinancialEntry.client_id == user.id)
        )
        entry = query.scalar_one_or_none()
        if entry is None:
            return raiseNotFound("Recurring financial entry not found.")
        await db.delete(entry)
        await db.commit()
        return JsonResponse(message="Recurring financial entry deleted successfully.")

    async def resources(self, db: AsyncSession = Depends(getAsyncDb)) -> JsonResponse:
        frequencies = [
            {"label": frequency.name, "value": frequency.value}
            for frequency in FinancialRecurringFrequency
        ]
        stmt = await db.execute(
            select(FinancialCategory).where(
                FinancialCategory.name.notin_(["loss", "loss_recovery"])
            )
        )
        financial_categories = [
            {"label": category.name, "value": category.id}
            for category in stmt.scalars().all()
        ]
        return JsonResponse(
            data={
                "frequencies": frequencies,
                "financial_categories": financial_categories,
            }
        )

    def __formatEntryData(
        self, entry: RowMapping
    ) -> RecurringFinancialEntryDetailResponse:
        generate_at_obj = datetime.strptime(
            entry["RecurringFinancialEntry"].generate_at, "%Y-%m-%d"
        )
        create_at_obj = datetime.strptime(
            entry["RecurringFinancialEntry"].created_at, "%Y-%m-%d %H:%M:%S"
        )
        return RecurringFinancialEntryDetailResponse(
            id=entry["RecurringFinancialEntry"].id,
            title=entry["RecurringFinancialEntry"].title,
            amount=entry["RecurringFinancialEntry"].amount,
            description=entry["RecurringFinancialEntry"].description,
            frequency=entry["RecurringFinancialEntry"].frequency,
            generate_at=generate_at_obj.strftime("%d-%m-%Y"),
            is_active=entry["RecurringFinancialEntry"].is_active,
            created_at=create_at_obj.strftime("%d-%m-%Y %I:%M %p"),
        )

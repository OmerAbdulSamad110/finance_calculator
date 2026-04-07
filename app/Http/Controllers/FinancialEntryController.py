from fastapi import Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import RowMapping
from sqlalchemy import select
from app.Core.Database import getAsyncDb
from datetime import datetime
from app.Http.Responses.UserResponse import UserAuthResponse
from app.Http.Requests.FinancialEntryRequest import (
    FinancialEntryListRequest,
    FinancialEntryStoreRequest,
)
from app.Models.FinancialEntry import FinancialEntry
from app.Models.FinancialCategory import FinancialCategory
from app.Http.Responses.JsonResponse import JsonResponse
from app.Http.Responses.FinancialEntryResponse import (
    FinancialEntryDetailResponse,
    FinancialCategoryDetailResponse,
)
from bootstrap.exception.exceptions import raiseNotFound, raiseUnprocessableContent
from bootstrap.exception.validations import exists


class FinancialEntryController:

    def __init__(self) -> None:
        pass

    async def index(
        self,
        request: Request,
        payload: FinancialEntryListRequest = Query(...),
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        user: UserAuthResponse = getattr(request.state, "user")
        start = datetime(payload.year, payload.month, 1)
        end = datetime(
            payload.year + (payload.month // 12), (payload.month % 12) + 1, 1
        )
        stmt = (
            (
                select(FinancialEntry)
                if not payload.with_category
                else select(
                    FinancialEntry,
                    FinancialCategory.name.label("category_name"),
                    FinancialCategory.color.label("category_color"),
                    FinancialCategory.transaction_type.label(
                        "category_transaction_type"
                    ),
                )
            )
            .join(
                FinancialCategory,
                FinancialCategory.id == FinancialEntry.financial_category_id,
            )
            .where(
                FinancialEntry.client_id == user.id,
                FinancialEntry.entered_at.between(start, end),
                FinancialCategory.name.notin_(["loss", "loss_recovery"]),
            )
        )
        query = await db.execute(stmt)
        data = query.mappings().all()

        enteries = [self.__formatFinancialEntryData(entery) for entery in data]
        return JsonResponse(data={"enteries": enteries})

    async def show(
        self, id: int, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        query = await db.execute(select(FinancialEntry).where(FinancialEntry.id == id))
        entery = query.mappings().first()
        if not entery:
            raiseNotFound("Financial Entry not found.")
        return JsonResponse(data=self.__formatFinancialEntryData(entery))

    async def store(
        self,
        payload: FinancialEntryStoreRequest,
        request: Request,
        db: AsyncSession = Depends(getAsyncDb),
    ) -> JsonResponse:
        if not await exists(db, FinancialCategory, "id", payload.financial_category_id):
            raiseUnprocessableContent({"financial_category_id": ["Inva."]})
        user: UserAuthResponse = getattr(request.state, "user", None)
        financial_entry = FinancialEntry(**payload.model_dump(), client_id=user.id)
        db.add(financial_entry)
        await db.commit()
        return JsonResponse(message="Financial Entry created successfully.")

    async def resources(
        self, request: Request, db: AsyncSession = Depends(getAsyncDb)
    ) -> JsonResponse:
        user: UserAuthResponse = getattr(request.state, "user")
        query = await db.execute(select(FinancialCategory))
        financial_categories = [
            FinancialCategoryDetailResponse(
                id=category["FinancialCategory"].id,
                name=category["FinancialCategory"].name,
                color=category["FinancialCategory"].color,
                transaction_type=category["FinancialCategory"].transaction_type,
            )
            for category in query.mappings().all()
        ]
        loss_ids = [
            category.id
            for category in financial_categories
            if category.name in ["loss", "loss_recovery"]
        ]
        query = await db.execute(
            select(FinancialEntry)
            .where(FinancialEntry.client_id == user.id)
            .where(FinancialEntry.financial_category_id.in_(loss_ids))
        )
        losses_enteries = [
            self.__formatFinancialEntryData(entry) for entry in query.mappings().all()
        ]
        return JsonResponse(
            data={
                "losses_enteries": {
                    "list": losses_enteries,
                    "total_loss": sum(
                        [
                            entry.amount
                            for entry in losses_enteries
                            if entry.category == loss_ids[0]
                        ]
                    ),
                    "total_recovery": sum(
                        [
                            entry.amount
                            for entry in losses_enteries
                            if entry.category == loss_ids[1]
                        ]
                    ),
                },
                "financial_categories": financial_categories,
            }
        )

    def __formatFinancialEntryData(
        self, entery: RowMapping
    ) -> FinancialEntryDetailResponse:
        financial_entry_dict = {
            "id": entery["FinancialEntry"].id,
            "title": entery["FinancialEntry"].title,
            "amount": entery["FinancialEntry"].amount,
            "description": entery["FinancialEntry"].description,
            "entered_at": entery["FinancialEntry"].entered_at,
            "frequency": entery["FinancialEntry"].frequency,
        }
        if "category_name" in entery:
            financial_entry_dict["category"] = {
                "id": entery["FinancialEntry"].financial_category_id,
                "name": entery["category_name"],
                "color": entery["category_color"],
                "transaction_type": entery["category_transaction_type"],
            }
        else:
            financial_entry_dict["category"] = entery[
                "FinancialEntry"
            ].financial_category_id
        return FinancialEntryDetailResponse(**financial_entry_dict)

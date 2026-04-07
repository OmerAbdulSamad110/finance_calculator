from sqlalchemy.ext.asyncio import AsyncSession
from app.Http.Responses.JsonResponse import JsonResponse
from app.Enums.FinancialCategoryType import FinancialCategoryType
from app.Models.FinancialCategory import FinancialCategory

financial_categories = [
    {
        "name": FinancialCategoryType.INCOME.value,
        "transaction_type": "credit",
        "color": "#00FF0090",
    },
    {
        "name": FinancialCategoryType.EXPENSE.value,
        "transaction_type": "debit",
        "color": "#FF0000",
    },
    {
        "name": FinancialCategoryType.REFUND.value,
        "transaction_type": "credit",
        "color": "#FF00FF",
    },
    {
        "name": FinancialCategoryType.INVESTMENT.value,
        "transaction_type": "debit",
        "color": "#0000FF",
    },
    {
        "name": FinancialCategoryType.RETURNS.value,
        "transaction_type": "credit",
        "color": "#FFFF00",
    },
    {
        "name": FinancialCategoryType.TAX.value,
        "transaction_type": "debit",
        "color": "#FFAA00E9",
    },
    {
        "name": FinancialCategoryType.LOSS.value,
        "transaction_type": "debit",
        "color": "#FF000000",
    },
    {
        "name": FinancialCategoryType.LOSS_RECOVERY.value,
        "transaction_type": "credit",
        "color": "#10EDEDD2",
    },
    {
        "name": FinancialCategoryType.LOAN_RECEIVED.value,
        "transaction_type": "credit",
        "color": "#B7FF00FF",
    },
    {
        "name": FinancialCategoryType.LOAN_REPAYMENT.value,
        "transaction_type": "debit",
        "color": "#8F3BC7AD",
    },
    {
        "name": FinancialCategoryType.LOAN_GIVEN.value,
        "transaction_type": "debit",
        "color": "#FF2181FF",
    },
    {
        "name": FinancialCategoryType.LOAN_RECOVERY.value,
        "transaction_type": "credit",
        "color": "#912929FF",
    },
    {
        "name": FinancialCategoryType.OTHER.value,
        "transaction_type": "debit",
        "color": "#908E8E",
    },
]


async def seedFinancialCategories(db: AsyncSession):
    for category in financial_categories:
        db.add(FinancialCategory(**category))
    await db.commit()
    return JsonResponse(message="Financial categories seeded successfully.")

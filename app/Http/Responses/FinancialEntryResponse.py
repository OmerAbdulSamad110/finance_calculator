from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class FinancialCategoryDetailResponse(BaseModel):
    id: int
    name: str
    color: str
    transaction_type: Literal["credit", "debit"]


class FinancialEntryDetailResponse(BaseModel):
    id: int
    title: str
    amount: float
    description: str
    entered_at: datetime
    frequency: str
    category: Optional[FinancialCategoryDetailResponse | int] = None

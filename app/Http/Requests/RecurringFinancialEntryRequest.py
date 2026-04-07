from pydantic import BaseModel, Field
from app.Enums.FinancialFrequency import FinancialRecurringFrequency
from datetime import date


class RecurringFinancialEntryStoreRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    amount: float = Field(gt=0)
    description: str = Field(max_length=255)
    frequency: FinancialRecurringFrequency
    generate_at: date = Field(format="%Y-%m-%d", gt=date.today())
    is_active: bool
    financial_category_id: int = Field(gt=0)

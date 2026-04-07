from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from app.Enums.FinancialFrequency import FinancialFrequency


class FinancialEntryListRequest(BaseModel):
    month: int = Field(gt=0, le=12)
    year: int = Field(gt=1900)
    with_category: bool = False

    @field_validator("year")
    def validate_year(cls, value):
        if value > datetime.now().year:
            raise ValueError("Year must be less than current year.")
        return value


class FinancialEntryStoreRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    amount: float = Field(gt=0)
    description: str = Field(max_length=300)
    financial_category_id: int = Field(gt=0)
    frequency: FinancialFrequency
    entered_at: date

from pydantic import BaseModel


class RecurringFinancialEntryDetailResponse(BaseModel):
    id: int
    title: str
    amount: float
    description: str
    frequency: str
    generate_at: str
    is_active: bool
    created_at: str

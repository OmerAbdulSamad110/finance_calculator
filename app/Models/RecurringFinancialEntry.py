from .Model import Model
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Boolean,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from datetime import timezone, datetime
from functools import partial
from app.Enums.FinancialFrequency import FinancialRecurringFrequency


class RecurringFinancialEntry(Model):
    __tablename__ = "recurring_financial_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(String(255), nullable=True)
    frequency = Column(
        Enum(
            FinancialRecurringFrequency,
            values_callable=lambda x: [item.value for item in x],
        ),
        nullable=False,
    )
    generate_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    client_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    financial_category_id = Column(
        Integer,
        ForeignKey("financial_categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(
        DateTime, nullable=False, default=partial(datetime.now, timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=partial(datetime.now, timezone.utc),
        onupdate=partial(datetime.now, timezone.utc),
    )

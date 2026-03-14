from .Model import Model
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import timezone, datetime
from functools import partial
from app.Enums.FinanceFrequency import FinanceRecurringFrequency


class RecurringEntry(Model):
    __tablename__ = "recurring_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Integer, nullable=False)
    short_description = Column(String(255), nullable=True)
    frequency = Column(Enum(FinanceRecurringFrequency), nullable=False)
    generate_at = Column(DateTime, nullable=False)
    client_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id = Column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime, nullable=False, default=partial(datetime.now, timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=partial(datetime.now, timezone.utc),
        onupdate=partial(datetime.now, timezone.utc),
    )
    client = relationship("User", back_populates="recurring_entries")
    category = relationship("Category", back_populates="recurring_entries")

from .Model import Model
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from datetime import timezone, datetime
from functools import partial


class FinancialEntry(Model):
    __tablename__ = "financial_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(DECIMAL(precision=10, scale=2), nullable=False)
    description = Column(String(300), nullable=False)
    client_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id = Column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    recurring_entry_id = Column(
        Integer, ForeignKey("recurring_entries.id", ondelete="CASCADE"), nullable=True
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
    client = relationship("User", back_populates="financial_entries")
    category = relationship("Category", back_populates="financial_entries")

from .Model import Model
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from datetime import datetime, timezone
from functools import partial
from app.Enums.FinanceCategoryType import FinanceCategoryType


class Category(Model):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(FinanceCategoryType))
    transaction_type = Column(Enum("credit", "debit"), nullable=False)
    color = Column(String(20), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=partial(datetime.now, timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=partial(datetime.now, timezone.utc),
        onupdate=partial(datetime.now, timezone.utc),
    )

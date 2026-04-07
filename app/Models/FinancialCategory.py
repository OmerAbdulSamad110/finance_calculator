from .Model import Model
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from functools import partial


class FinancialCategory(Model):
    __tablename__ = "financial_categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # name = Column(
    #     Enum(
    #         FinancialCategoryType,
    #         values_callable=lambda x: [item.value for item in x],
    #     )
    # )
    name = Column(String(255), nullable=False, unique=True)
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

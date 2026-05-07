from .Model import Model
from functools import partial
from sqlalchemy import Column, Integer, String, CHAR, DECIMAL, DateTime, ForeignKey
from datetime import timezone, datetime


class City:
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    state_code = Column(CHAR(3), nullable=False)
    country_code = Column(CHAR(2), nullable=False)
    country_id = Column(
        Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False
    )
    latitude = Column(DECIMAL(10, 2), nullable=False)
    longitude = Column(DECIMAL(10, 3), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=partial(datetime.now, timezone.utc)
    )  # No parentheses
    updated_at = Column(
        DateTime,
        nullable=False,
        default=partial(datetime.now, timezone.utc),
        onupdate=partial(datetime.now, timezone.utc),
    )

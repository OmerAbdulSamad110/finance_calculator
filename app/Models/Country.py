from .Model import Model
from functools import partial
from sqlalchemy import Column, Integer, String, CHAR, Text, DECIMAL, DateTime
from datetime import timezone, datetime


class Country(Model):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    iso2_code = Column(CHAR(2), nullable=False, unique=True)
    iso3_code = Column(CHAR(3), nullable=False, unique=True)
    phone_code = Column(String(5), nullable=False)
    currency_name = Column(String(200), nullable=False)
    currency_code = Column(CHAR(3), nullable=False)
    currency_symbol = Column(String(5), nullable=False)
    nationality = Column(String(200), nullable=False)
    capital = Column(String(100), nullable=False)
    region = Column(String(10), nullable=False)
    sub_region = Column(String(30), nullable=False)
    timezones = Column(Text, nullable=False)
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

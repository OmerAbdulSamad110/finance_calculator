from .Model import Model
from functools import partial
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import timezone, datetime


class Company(Model):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    logo = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    address = Column(String(300), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20), nullable=False)
    website_url = Column(String(300), nullable=True)
    certificate = Column(String(255), nullable=True)
    iata_no = Column(String(8), nullable=True)
    zip_code = Column(String(10), nullable=False)
    nature_of_business = Column(String(50), nullable=False)
    country_id = Column(
        Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False
    )
    city_id = Column(
        Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False
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

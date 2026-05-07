from .Model import Model
from functools import partial
from sqlalchemy import Column, Integer, String, CHAR, DateTime, ForeignKey
from datetime import timezone, datetime
from geoalchemy2 import Geometry


class location(Model):
    __tablename__ = "locations"
    __table_args__ = {"info": {"skip_autogenerate": True}}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    state_code = Column(CHAR(3), nullable=False)
    country_code = Column(CHAR(2), nullable=False)
    coordinates = Column(Geometry(geometry_type="POINT", srid=4326))
    country_id = Column(
        Integer, ForeignKey("countries.id", ondelete="CASCADE"), nullable=False
    )
    city_id = Column(
        Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False
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

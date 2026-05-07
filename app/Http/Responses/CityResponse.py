from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class CityItemResponse(BaseModel):
    id: int
    name: str
    state_code: str
    country_code: str
    country_id: int
    country_name: Optional[str] = None
    latitude: Decimal
    longitude: Decimal
    created_at: str

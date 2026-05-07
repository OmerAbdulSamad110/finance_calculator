from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, Literal


class CityFormRequest(BaseModel):
    name: str = Field(
        min_length=3, max_length=255, title="City Name", description="City Name"
    )
    state_code: str = Field(
        min_length=3,
        max_length=3,
        title="City State Code",
        description="City State Code",
    )
    country_code: str = Field(
        min_length=2,
        max_length=2,
        title="City Country Code",
        description="City Country Code",
    )
    country_id: int = Field(
        gt=0, title="City Country ID", description="City Country ID"
    )
    latitude: Decimal = Field(
        gt=-90, lt=90, title="City Latitude", description="City Latitude"
    )
    longitude: Decimal = Field(
        gt=-180, lt=180, title="City Longitude", description="City Longitude"
    )


class CityListRequest(BaseModel):
    list_type: Optional[Literal["with_country", "full"]] = Field(
        default=None, title="City list type", description="City list type"
    )

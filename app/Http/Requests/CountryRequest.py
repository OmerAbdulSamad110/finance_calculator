from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, Literal


class CountryFormRequest(BaseModel):
    name: str = Field(
        min_length=3, max_length=255, title="Country Name", description="Country Name"
    )
    iso2_code: str = Field(
        min_length=2,
        max_length=2,
        title="Country ISO2 Code",
        description="Country ISO2 Code",
    )
    iso3_code: str = Field(
        min_length=3,
        max_length=3,
        title="Country ISO3 Code",
        description="Country ISO3 Code",
    )
    phone_code: str = Field(
        min_length=1,
        max_length=5,
        title="Country Phone Code",
        description="Country Phone Code",
    )
    currency_name: str = Field(
        min_length=3,
        max_length=200,
        title="Country Currency Name",
        description="Country Currency Name",
    )
    currency_code: str = Field(
        min_length=3,
        max_length=3,
        title="Country Currency Code",
        description="Country Currency Code",
    )
    currency_symbol: str = Field(
        min_length=1,
        max_length=5,
        title="Country Currency Symbol",
        description="Country Currency Symbol",
    )
    nationality: str = Field(
        min_length=3,
        max_length=200,
        title="Country Nationality",
        description="Country Nationality",
    )
    capital: str = Field(
        min_length=3,
        max_length=100,
        title="Country Capital",
        description="Country Capital",
    )
    region: str = Field(
        min_length=3,
        max_length=10,
        title="Country Region",
        description="Country Region",
    )
    sub_region: str = Field(
        min_length=3,
        max_length=30,
        title="Country Sub Region",
        description="Country Sub Region",
    )
    timezones: str = Field(
        title="Country Timezones", description="Country Timezones JSON String"
    )
    latitude: Decimal = Field(
        gt=-90, lt=90, title="Country Latitude", description="Country Latitude"
    )
    longitude: Decimal = Field(
        gt=-180, lt=180, title="Country Longitude", description="Country Longitude"
    )


class CountryListRequest(BaseModel):
    list_type: Optional[Literal["nationality", "iso2", "currency"]] = Field(
        default=None, title="Country list type", description="Country list type"
    )

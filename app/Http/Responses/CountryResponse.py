from pydantic import BaseModel
from decimal import Decimal


class CountryItemResponse(BaseModel):
    name: str
    iso2_code: str
    iso3_code: str
    phone_code: str
    currency_name: str
    currency_code: str
    currency_symbol: str
    nationality: str
    capital: str
    region: str
    sub_region: str
    timezones: str
    latitude: Decimal
    longitude: Decimal

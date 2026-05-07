from pydantic import BaseModel
from typing import Optional


class CompanyDetailResponse(BaseModel):
    id: int
    name: str
    logo: Optional[str] = None
    certificate: Optional[str] = None
    address: str
    email: str
    phone: str
    website_url: Optional[str] = None
    iata_no: Optional[str] = None
    zip_code: str
    nature_of_business: str
    is_active: bool
    country_id: int
    country_name: Optional[str] = None
    city_id: int
    city_name: Optional[str] = None
    created_at: str

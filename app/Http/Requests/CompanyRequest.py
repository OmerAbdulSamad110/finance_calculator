from pydantic import BaseModel, Field
from fastapi import UploadFile, File
from typing import Optional
from typing_extensions import Annotated


class CompanyFormRequest(BaseModel):
    name: str = Field(min_length=3, max_length=255, title="Company Name")
    email: str = Field(max_length=255, title="Company Email")
    phone: str = Field(min_length=10, max_length=20, title="Company Phone")
    address: str = Field(max_length=300, title="Company Address")
    logo: Annotated[Optional[UploadFile], File()] = Field(
        default=None, title="Company Logo"
    )
    certificate: Annotated[Optional[UploadFile], File()] = Field(
        default=None, title="Company certificate"
    )
    website_url: Optional[str] = Field(
        max_length=300, default=None, title="Company Website URL"
    )
    iata_no: Optional[str] = Field(
        max_length=8, default=None, title="Company IATA Number"
    )
    zip_code: str = Field(max_length=10, title="Company Zip Code")
    nature_of_business: str = Field(max_length=50, title="Company Nature of Business")
    country_id: int = Field(gt=0, title="Company Country ID")
    city_id: int = Field(gt=0, title="Company City ID")
    is_active: bool = Field(default=True, title="Company Active Status")

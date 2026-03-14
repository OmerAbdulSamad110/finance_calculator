from pydantic import BaseModel


class SimpleListResponse(BaseModel):
    label: str
    value: str

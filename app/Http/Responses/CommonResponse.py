from pydantic import BaseModel


class SimpleListItemResponse(BaseModel):
    label: str
    value: str

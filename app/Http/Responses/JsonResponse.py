from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str
    status: bool = True


class DataResponse(BaseModel):
    data: dict
    status: bool = True

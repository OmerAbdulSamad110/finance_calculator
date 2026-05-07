from pydantic import BaseModel
from fastapi import UploadFile


class FileItem(BaseModel):
    name: str
    path: str
    file: UploadFile

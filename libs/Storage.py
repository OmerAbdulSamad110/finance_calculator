from fastapi import UploadFile
from typing import Optional
import shutil


class Storage:

    @staticmethod
    async def upload(file: UploadFile, path: str, name: Optional[str] = None) -> str:
        storage_path = f"storage/app/public/{path}"
        file_name = file.filename if name is None else name
        file_path = f"{storage_path}/{file_name}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_path

from fastapi import status, HTTPException
from typing import NoReturn


def raiseUnprocessableContent(errors: dict[str, list[str]]):
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=errors,
    )


def raiseBadRequest(message="Bad request"):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def raiseUnauthenticated(
    message="Unauthenticated", headers={"WWW-Authenticate": "Bearer"}
):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail=message, headers=headers
    )


def raiseUnauthorized(message="Unauthorized"):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def raiseNotFound(message="Not found") -> NoReturn:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

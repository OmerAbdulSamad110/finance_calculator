from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def returnValidationError(errors: dict[list]) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder(
            {
                "message": "Validation failed.",
                "errors": errors,
            }
        ),
    )


def raiseBadRequest(message="Bad request"):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def raiseUnauthorized(message="Unauthorized"):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


def raiseForbidden(message="Forbidden"):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def raiseNotFound(message="Not found"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from collections import defaultdict
import logging
from app.Core.Logger import logger
from starlette.exceptions import HTTPException as StarletteHTTPException


def setupExceptions(app: FastAPI):
    # -------------------------
    # HTTPException handler
    # -------------------------

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        status_code = exc.status_code
        content = {"message": "Internal server error."}

        if status_code in (400, 401, 403, 404, 405, 419, 422):
            content["message"] = exc.detail

            if status_code == 422:
                content = {"message": "Invalid data given.", "errors": exc.detail}
            elif status_code == 401:
                content = {"message": "Unauthenticated."}
            elif status_code == 403:
                content = {"message": "Unauthorized."}
            elif status_code == 405:
                content = {"message": "Method not allowed."}

        return JSONResponse(status_code=status_code, content=content)

    # -------------------------
    # Validation errors (Pydantic)
    # -------------------------
    @app.exception_handler(RequestValidationError)
    async def validationExceptionHandler(request: Request, exc: RequestValidationError):
        reformatted_errors = defaultdict(list)
        for error in exc.errors():
            loc = error["loc"]
            msg = error["msg"]
            filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
            field_string = ".".join(map(str, filtered_loc))
            reformatted_errors[field_string].append(msg)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=jsonable_encoder(
                {
                    "message": "Invalid data given.",
                    "errors": reformatted_errors,
                }
            ),
        )

    # -------------------------
    # Catch ALL unhandled errors
    # -------------------------
    @app.exception_handler(Exception)
    async def generalExceptionHandler(request: Request, exc: Exception):
        logger.error("Unhandled server error", exc_info=exc)
        logging.exception("Unhandled server error", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error."},
        )

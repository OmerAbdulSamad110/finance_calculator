from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from collections import defaultdict
import logging


def setup_exceptions(app: FastAPI) -> FastAPI:
    # -------------------------
    # HTTPException handler
    # -------------------------
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        status_code = exc.status_code
        # If not explicitly allowed → treat as 500
        if status_code not in (400, 401, 403, 404, 405, 419, 422):
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            message = "Internal server error."
        else:
            message = exc.detail
        logging.exception(message, {"status_code": status_code, "detail": exc.detail})
        return JSONResponse(
            status_code=status_code,
            content={"message": message},
        )

    # -------------------------
    # Validation errors (Pydantic)
    # -------------------------
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
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
                    "message": "Validation failed.",
                    "errors": reformatted_errors,
                }
            ),
        )

    # -------------------------
    # Catch ALL unhandled errors
    # -------------------------
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logging.exception("Unhandled server error", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error."},
        )

    return app

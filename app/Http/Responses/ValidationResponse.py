from pydantic import BaseModel, Field


class ValidationResponse(BaseModel):
    message: str = Field(
        "Invalid request given.", description="The general error message"
    )
    errors: dict[str, list[str]] = Field(
        description="Detailed field-specific errors",
        example={"field_name": ["Field related error 1", "Field related error 2"]},
    )

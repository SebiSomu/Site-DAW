from typing import TypeVar

from flask import request
from pydantic import BaseModel

from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse

SchemaT = TypeVar("SchemaT", bound=BaseModel)


def parse_body(schema: type[SchemaT]) -> SchemaT:
    return schema.model_validate(request.get_json(silent=True) or {})


__all__ = ["LoginRequest", "RegisterRequest", "UserResponse", "parse_body"]

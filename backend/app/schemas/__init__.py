from typing import TypeVar

from flask import request
from pydantic import BaseModel

from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from app.schemas.catalog import CategoryResponse, ProductDetail, ProductPageResponse, ProductQuery

SchemaT = TypeVar("SchemaT", bound=BaseModel)


def parse_body(schema: type[SchemaT]) -> SchemaT:
    return schema.model_validate(request.get_json(silent=True) or {})


def parse_query(schema: type[SchemaT]) -> SchemaT:
    return schema.model_validate(request.args.to_dict())


__all__ = [
    "CategoryResponse",
    "LoginRequest",
    "ProductDetail",
    "ProductPageResponse",
    "ProductQuery",
    "RegisterRequest",
    "UserResponse",
    "parse_body",
    "parse_query",
]

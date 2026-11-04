from typing import TypeVar

from flask import request
from pydantic import BaseModel

from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from app.schemas.catalog import CategoryResponse, ProductDetail, ProductPageResponse, ProductQuery, ReviewResponse
from app.schemas.shop import (
    AddressRequest,
    AddressResponse,
    CartItemRequest,
    CartRequest,
    CartResponse,
    OrderDetail,
    OrderRequest,
    OrderSummary,
    ReviewRequest,
)

SchemaT = TypeVar("SchemaT", bound=BaseModel)


def parse_body(schema: type[SchemaT]) -> SchemaT:
    return schema.model_validate(request.get_json(silent=True) or {})


def parse_query(schema: type[SchemaT]) -> SchemaT:
    return schema.model_validate(request.args.to_dict())


__all__ = [
    "AddressRequest",
    "AddressResponse",
    "CartItemRequest",
    "CartRequest",
    "CartResponse",
    "CategoryResponse",
    "LoginRequest",
    "OrderDetail",
    "OrderRequest",
    "OrderSummary",
    "ProductDetail",
    "ProductPageResponse",
    "ProductQuery",
    "RegisterRequest",
    "ReviewRequest",
    "ReviewResponse",
    "UserResponse",
    "parse_body",
    "parse_query",
]

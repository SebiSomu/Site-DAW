from flask import Flask, jsonify
from flask_wtf.csrf import CSRFError
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException, InternalServerError

from app.extensions import db
from app.services.activity_logger import activity_logger


class AppError(Exception):
    status_code = 500
    message = "Something went wrong. Please try again later."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or type(self).message
        super().__init__(self.message)


class ValidationError(AppError):
    status_code = 400
    message = "The submitted data is not valid."


class AuthenticationError(AppError):
    status_code = 401
    message = "Please log in to continue."


class ForbiddenError(AppError):
    status_code = 403
    message = "You do not have permission to do this."


class NotFoundError(AppError):
    status_code = 404
    message = "The requested resource was not found."


class ConflictError(AppError):
    status_code = 409
    message = "This conflicts with existing data."


class OutOfStockError(ConflictError):
    message = "This jar is out of stock."


def error_response(message: str, status_code: int):
    return jsonify(error=message), status_code


def describe_validation_error(error: PydanticValidationError) -> str:
    problems = []
    for detail in error.errors():
        field = ".".join(str(part) for part in detail["loc"])
        problems.append(f"{field}: {detail['msg']}" if field else detail["msg"])
    return "; ".join(problems)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return error_response(error.message, error.status_code)

    @app.errorhandler(PydanticValidationError)
    def handle_validation_error(error: PydanticValidationError):
        return error_response(describe_validation_error(error), ValidationError.status_code)

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error: IntegrityError):
        db.session.rollback()
        return error_response(ConflictError.message, ConflictError.status_code)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error: CSRFError):
        activity_logger.warning("csrf_rejected", error.description)
        return error_response("Your security token is missing or expired. Refresh the page and try again.", 400)

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return error_response(error.description, error.code)

    @app.errorhandler(InternalServerError)
    def handle_internal_error(error: InternalServerError):
        db.session.rollback()
        return error_response(AppError.message, 500)

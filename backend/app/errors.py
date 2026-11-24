from flask import Flask, jsonify, request
from flask_limiter.errors import RateLimitExceeded
from flask_wtf.csrf import CSRFError
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException, InternalServerError, RequestEntityTooLarge

from app.extensions import db
from app.rate_limits import describe_wait, seconds_until_reset
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


class CheckoutAlreadyPaidError(ConflictError):
    message = "This order has just been paid."


class PaymentError(AppError):
    status_code = 502
    message = "We could not reach the payment service. Please try again in a moment."


class UploadError(AppError):
    status_code = 400
    message = "This photo could not be uploaded."


class UploadTooLargeError(UploadError):
    status_code = 413
    message = "This file is larger than 12 MB. Please choose a smaller photo."


class WebhookError(AppError):
    status_code = 400
    message = "This payment notification could not be verified."


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

    @app.errorhandler(RequestEntityTooLarge)
    def handle_too_large(error: RequestEntityTooLarge):
        activity_logger.warning("upload_rejected", "reason=too_large")
        return error_response(UploadTooLargeError.message, UploadTooLargeError.status_code)

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limited(error: RateLimitExceeded):
        seconds = seconds_until_reset()
        activity_logger.warning("rate_limited", f"route={request.method} {request.path} limit={error.limit.limit}")
        response, status = error_response(f"Too many requests. Please try again in {describe_wait(seconds)}.", 429)
        response.headers["Retry-After"] = str(seconds)
        return response, status

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return error_response(error.description, error.code)

    @app.errorhandler(InternalServerError)
    def handle_internal_error(error: InternalServerError):
        db.session.rollback()
        return error_response(AppError.message, 500)

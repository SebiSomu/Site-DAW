from flask import Blueprint, jsonify
from flask_login import current_user, login_required
from flask_wtf.csrf import generate_csrf

from app.schemas import LoginRequest, RegisterRequest, UserResponse, parse_body
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


def user_json(user):
    return jsonify(user=UserResponse.from_user(user).model_dump())


@auth_bp.get("/csrf")
def csrf_token():
    return jsonify(csrf_token=generate_csrf())


@auth_bp.post("/auth/register")
def register():
    return user_json(AuthService().register(parse_body(RegisterRequest))), 201


@auth_bp.post("/auth/login")
def login():
    return user_json(AuthService().login(parse_body(LoginRequest)))


@auth_bp.post("/auth/logout")
@login_required
def logout():
    AuthService().logout()
    return "", 204


@auth_bp.get("/auth/session")
def session():
    user = UserResponse.from_user(current_user).model_dump() if current_user.is_authenticated else None
    return jsonify(user=user)


@auth_bp.get("/auth/me")
@login_required
def me():
    return user_json(current_user)

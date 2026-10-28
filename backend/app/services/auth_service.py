from flask_login import login_user, logout_user

from app.errors import AuthenticationError, ConflictError
from app.extensions import db
from app.models import RoleName, User
from app.repositories import RoleRepository, UserRepository
from app.schemas import LoginRequest, RegisterRequest
from app.services.activity_logger import activity_logger


class AuthService:
    def __init__(self, users: UserRepository | None = None, roles: RoleRepository | None = None) -> None:
        self.users = users or UserRepository()
        self.roles = roles or RoleRepository()

    def register(self, data: RegisterRequest) -> User:
        if self.users.email_exists(data.email):
            raise ConflictError("An account with this email already exists.")
        user = User(
            email=data.email.lower(),
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            role=self.roles.get_by_name(RoleName.CLIENT),
        )
        user.set_password(data.password)
        self.users.add(user)
        db.session.commit()
        login_user(user)
        activity_logger.info("register", f"email={user.email}")
        return user

    def login(self, data: LoginRequest) -> User:
        user = self.users.get_by_email(data.email)
        if user is None or not user.check_password(data.password):
            activity_logger.warning("login_failed", f"email={data.email}")
            raise AuthenticationError("Invalid email or password.")
        login_user(user)
        activity_logger.info("login", f"email={user.email}")
        return user

    def logout(self) -> None:
        activity_logger.info("logout")
        logout_user()

from functools import wraps

from flask_login import current_user, login_required

from app.errors import AuthenticationError, ForbiddenError
from app.models import RoleName, User
from app.repositories import UserRepository
from app.services.activity_logger import activity_logger


def load_user(user_id: str) -> User | None:
    return UserRepository().get(int(user_id))


def reject_anonymous() -> None:
    raise AuthenticationError()


def role_required(*roles: RoleName):
    allowed = {role.value for role in roles}

    def decorator(view):
        @wraps(view)
        @login_required
        def guarded(*args, **kwargs):
            if current_user.role.name not in allowed:
                activity_logger.warning("access_denied", f"role={current_user.role.name} view={view.__name__}")
                raise ForbiddenError()
            return view(*args, **kwargs)

        return guarded

    return decorator

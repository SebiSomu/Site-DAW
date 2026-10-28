from typing import Sequence

from sqlalchemy import func, select

from app.models import Address, User
from app.repositories.base import SqlAlchemyRepository


class UserRepository(SqlAlchemyRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        normalized = email.strip().lower()
        return self.session.scalars(select(User).where(func.lower(User.email) == normalized)).first()

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None


class AddressRepository(SqlAlchemyRepository[Address]):
    model = Address

    def list_active_for_user(self, user_id: int) -> Sequence[Address]:
        statement = (
            select(Address)
            .where(Address.user_id == user_id, Address.is_archived.is_(False))
            .order_by(Address.id.desc())
        )
        return self.session.scalars(statement).all()

    def get_for_user(self, address_id: int, user_id: int) -> Address | None:
        return self.find_one_by(id=address_id, user_id=user_id)

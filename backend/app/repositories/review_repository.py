from typing import Sequence

from sqlalchemy import select

from app.models import ContactMessage, Review
from app.repositories.base import SqlAlchemyRepository


class ReviewRepository(SqlAlchemyRepository[Review]):
    model = Review

    def list_for_product(self, product_id: int) -> Sequence[Review]:
        statement = select(Review).where(Review.product_id == product_id).order_by(Review.created_at.desc())
        return self.session.scalars(statement).all()

    def get_by_user_and_product(self, user_id: int, product_id: int) -> Review | None:
        return self.find_one_by(user_id=user_id, product_id=product_id)


class ContactMessageRepository(SqlAlchemyRepository[ContactMessage]):
    model = ContactMessage

    def list_newest_first(self) -> Sequence[ContactMessage]:
        return self.session.scalars(select(ContactMessage).order_by(ContactMessage.created_at.desc())).all()

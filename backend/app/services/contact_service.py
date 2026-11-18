from typing import Sequence

from app.errors import NotFoundError, ValidationError
from app.extensions import db
from app.models import ContactMessage
from app.repositories import ContactMessageRepository
from app.schemas.contact import ContactRequest
from app.security.sanitize import plain_text
from app.services.activity_logger import activity_logger


class ContactService:
    def __init__(self, messages: ContactMessageRepository | None = None) -> None:
        self.messages = messages or ContactMessageRepository()

    def send(self, data: ContactRequest) -> ContactMessage:
        message = ContactMessage(
            name=self._text(data.name, "Please tell us your name."),
            email=data.email.lower(),
            subject=self._text(data.subject, "Please add a subject."),
            message=self._text(data.message, "Please write your message."),
        )
        self.messages.add(message)
        db.session.commit()
        activity_logger.info("contact_message", f"message={message.id}")
        return message

    def page(self, page: int, per_page: int) -> tuple[Sequence[ContactMessage], int]:
        return self.messages.page_newest_first(page, per_page), self.messages.count()

    def delete(self, message_id: int) -> None:
        message = self.messages.get(message_id)
        if message is None:
            raise NotFoundError("We could not find this message.")
        self.messages.delete(message)
        db.session.commit()
        activity_logger.info("message_deleted", f"message={message_id}")

    @staticmethod
    def _text(value: str, message: str) -> str:
        cleaned = plain_text(value)
        if not cleaned:
            raise ValidationError(message)
        return cleaned

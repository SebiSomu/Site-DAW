from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field, StringConstraints, model_validator

from app.models import ContactMessage
from app.schemas.auth import RequestSchema

SenderName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Subject = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
MessageText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=5000)]
ActionName = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[a-z_]{1,60}$")]


def page_count(total: int, per_page: int) -> int:
    return max(1, -(-total // per_page))


class ContactRequest(RequestSchema):
    name: SenderName
    email: EmailStr = Field(max_length=255)
    subject: Subject
    message: MessageText


class PageQuery(RequestSchema):
    page: int = Field(default=1, ge=1, le=1000)
    per_page: int = Field(default=20, ge=1, le=50)


class ContactMessageResponse(BaseModel):
    id: int
    name: str
    email: str
    subject: str
    message: str
    created_at: datetime

    @classmethod
    def from_message(cls, message: ContactMessage) -> "ContactMessageResponse":
        return cls(
            id=message.id,
            name=message.name,
            email=message.email,
            subject=message.subject,
            message=message.message,
            created_at=message.created_at,
        )


class MessagesPageResponse(BaseModel):
    messages: list[ContactMessageResponse]
    total: int
    page: int
    per_page: int
    pages: int


class LogQuery(RequestSchema):
    user_id: int | None = Field(default=None, ge=1)
    action: ActionName | None = None
    level: Literal["INFO", "WARNING", "ERROR"] | None = None
    date_from: date | None = None
    date_to: date | None = None
    page: int = Field(default=1, ge=1, le=10000)
    per_page: int = Field(default=50, ge=1, le=200)

    @model_validator(mode="after")
    def dates_in_order(self) -> "LogQuery":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("The start date must be on or before the end date.")
        return self


class LogEntryResponse(BaseModel):
    timestamp: datetime
    level: str
    ip: str
    user_id: int | None
    action: str
    details: str


class LogPageResponse(BaseModel):
    entries: list[LogEntryResponse]
    total: int
    page: int
    per_page: int
    pages: int
    actions: list[str]

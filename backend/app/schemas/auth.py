from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from app.models import User

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, max_length=20, pattern=r"^\+?[0-9 ]{7,19}$")]


class RequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RegisterRequest(RequestSchema):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    first_name: Name
    last_name: Name
    phone: Phone | None = None


class LoginRequest(RequestSchema):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: str | None
    role: str

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role.name,
        )

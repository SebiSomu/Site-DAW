from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.extensions import db

ModelT = TypeVar("ModelT")


class IRepository(ABC, Generic[ModelT]):
    @abstractmethod
    def get(self, entity_id: int) -> ModelT | None: ...

    @abstractmethod
    def list_all(self) -> Sequence[ModelT]: ...

    @abstractmethod
    def add(self, entity: ModelT) -> ModelT: ...

    @abstractmethod
    def delete(self, entity: ModelT) -> None: ...

    @abstractmethod
    def count(self) -> int: ...


class SqlAlchemyRepository(IRepository[ModelT]):
    model: type[ModelT]

    def __init__(self, session: Session | None = None) -> None:
        self.session = session or db.session

    def get(self, entity_id: int) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def list_all(self) -> Sequence[ModelT]:
        return self.session.scalars(select(self.model)).all()

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)
        self.session.flush()

    def count(self) -> int:
        return self.session.scalar(select(func.count()).select_from(self.model)) or 0

    def find_one_by(self, **criteria) -> ModelT | None:
        return self.session.scalars(select(self.model).filter_by(**criteria)).first()

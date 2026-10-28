from app.models import Category, Ingredient, OrderStatus, OrderStatusCode, Role, RoleName
from app.repositories.base import SqlAlchemyRepository


class RoleRepository(SqlAlchemyRepository[Role]):
    model = Role

    def get_by_name(self, name: RoleName) -> Role | None:
        return self.find_one_by(name=name.value)


class OrderStatusRepository(SqlAlchemyRepository[OrderStatus]):
    model = OrderStatus

    def get_by_code(self, code: OrderStatusCode) -> OrderStatus | None:
        return self.find_one_by(code=code.value)


class CategoryRepository(SqlAlchemyRepository[Category]):
    model = Category

    def get_by_slug(self, slug: str) -> Category | None:
        return self.find_one_by(slug=slug)


class IngredientRepository(SqlAlchemyRepository[Ingredient]):
    model = Ingredient

    def get_by_name(self, name: str) -> Ingredient | None:
        return self.find_one_by(name=name)

    def get_or_create(self, name: str) -> Ingredient:
        return self.get_by_name(name) or self.add(Ingredient(name=name))

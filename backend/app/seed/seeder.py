from dataclasses import dataclass

from flask import current_app

from app.extensions import db
from app.models import (
    ORDER_STATUS_LABELS,
    Address,
    Category,
    OrderStatus,
    Product,
    Role,
    RoleName,
    User,
)
from app.repositories import (
    CategoryRepository,
    IngredientRepository,
    OrderStatusRepository,
    ProductRepository,
    RoleRepository,
    UserRepository,
)
from app.seed.data import CATEGORIES, PRODUCTS

DEMO_CLIENT_EMAIL = "client@exemplu.ro"
DEMO_CLIENT_PASSWORD = "Client-Demo-123"


@dataclass
class SeedReport:
    roles: int = 0
    statuses: int = 0
    categories: int = 0
    products: int = 0
    users: int = 0

    def summary(self) -> str:
        return (
            f"roles +{self.roles}, statuses +{self.statuses}, categories +{self.categories}, "
            f"products +{self.products}, users +{self.users}"
        )


class DatabaseSeeder:
    def __init__(self) -> None:
        self.roles = RoleRepository()
        self.statuses = OrderStatusRepository()
        self.categories = CategoryRepository()
        self.ingredients = IngredientRepository()
        self.products = ProductRepository()
        self.users = UserRepository()
        self.report = SeedReport()

    def run(self, include_demo_client: bool = False) -> SeedReport:
        self.seed_roles()
        self.seed_order_statuses()
        self.seed_categories()
        self.seed_products()
        self.seed_admin()
        if include_demo_client:
            self.seed_demo_client()
        db.session.commit()
        return self.report

    def seed_roles(self) -> None:
        for role_name in RoleName:
            if self.roles.get_by_name(role_name) is None:
                self.roles.add(Role(name=role_name.value))
                self.report.roles += 1

    def seed_order_statuses(self) -> None:
        for code, label in ORDER_STATUS_LABELS.items():
            if self.statuses.get_by_code(code) is None:
                self.statuses.add(OrderStatus(code=code.value, name=label))
                self.report.statuses += 1

    def seed_categories(self) -> None:
        for seed in CATEGORIES:
            if self.categories.get_by_slug(seed.slug) is None:
                self.categories.add(Category(name=seed.name, slug=seed.slug, description=seed.description))
                self.report.categories += 1

    def seed_products(self) -> None:
        for seed in PRODUCTS:
            if self.products.slug_exists(seed.slug):
                continue
            category = self.categories.get_by_slug(seed.category_slug)
            product = Product(
                name=seed.name,
                slug=seed.slug,
                description=seed.description,
                price_bani=seed.price_bani,
                weight_grams=seed.weight_grams,
                stock=seed.stock,
                category=category,
                ingredients=[self.ingredients.get_or_create(name) for name in seed.ingredients],
            )
            self.products.add(product)
            self.report.products += 1

    def seed_admin(self) -> None:
        email = current_app.config["ADMIN_EMAIL"]
        password = current_app.config["ADMIN_PASSWORD"]
        if not password or self.users.email_exists(email):
            return
        self._create_user(email, password, "Maria", "Popescu", RoleName.ADMIN)

    def seed_demo_client(self) -> None:
        if self.users.email_exists(DEMO_CLIENT_EMAIL):
            return
        client = self._create_user(DEMO_CLIENT_EMAIL, DEMO_CLIENT_PASSWORD, "Andrei", "Ionescu", RoleName.CLIENT)
        client.addresses.append(
            Address(street="Str. Republicii nr. 10", city="Brașov", county="Brașov", postal_code="500030")
        )

    def _create_user(self, email: str, password: str, first_name: str, last_name: str, role_name: RoleName) -> User:
        user = User(
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            role=self.roles.get_by_name(role_name),
        )
        user.set_password(password)
        self.users.add(user)
        self.report.users += 1
        return user

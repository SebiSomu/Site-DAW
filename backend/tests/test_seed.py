from app.models import Category, OrderStatus, Product, Role, User
from app.repositories import ProductRepository
from app.seed import DatabaseSeeder


def test_seed_creates_reference_data_catalog_and_accounts(app, session):
    report = DatabaseSeeder().run(include_demo_client=True)
    assert (report.roles, report.statuses, report.categories, report.products, report.users) == (2, 6, 4, 20, 2)
    assert session.query(Role).count() == 2
    assert session.query(OrderStatus).count() == 6
    assert session.query(Category).count() == 4
    assert session.query(Product).count() == 20
    assert session.query(User).count() == 2


def test_seed_is_idempotent(app, session):
    DatabaseSeeder().run(include_demo_client=True)
    second = DatabaseSeeder().run(include_demo_client=True)
    assert second.summary() == "roles +0, statuses +0, categories +0, products +0, users +0"


def test_ingredients_are_shared_not_duplicated(app, session):
    DatabaseSeeder().run()
    repository = ProductRepository()
    apricot = repository.get_by_slug("apricot-jam")
    strawberry = repository.get_by_slug("strawberry-jam")
    shared = {i.id for i in apricot.ingredients} & {i.id for i in strawberry.ingredients}
    assert len(shared) == 2


def test_admin_is_skipped_without_password(app, session):
    app.config["ADMIN_PASSWORD"] = None
    report = DatabaseSeeder().run()
    assert report.users == 0

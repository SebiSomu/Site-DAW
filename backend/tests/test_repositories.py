from app.repositories import IRepository, ProductRepository, ProductSort, SqlAlchemyRepository, UserRepository
from app.seed import DEMO_CLIENT_EMAIL


def test_repositories_implement_the_interface():
    repository = ProductRepository()
    assert isinstance(repository, IRepository)
    assert isinstance(repository, SqlAlchemyRepository)


def test_search_filters_by_category(seeded):
    page = ProductRepository().search(category_slug="fruit-butters")
    assert page.total == 3
    assert {product.category.slug for product in page.items} == {"fruit-butters"}


def test_search_is_case_insensitive(seeded):
    page = ProductRepository().search(query="STRAWBERRY")
    assert [product.slug for product in page.items] == ["strawberry-jam"]


def test_search_sorts_by_price(seeded):
    prices = [product.price_cents for product in ProductRepository().search(sort=ProductSort.PRICE_ASC, per_page=50).items]
    assert prices == sorted(prices)


def test_search_paginates(seeded):
    repository = ProductRepository()
    first = repository.search(per_page=5, page=1)
    third = repository.search(per_page=5, page=3)
    assert first.total == 20
    assert first.pages == 4
    assert len(first.items) == 5
    assert len(third.items) == 5


def test_search_is_safe_against_sql_injection(seeded):
    repository = ProductRepository()
    assert repository.search(query="' OR 1=1 --").total == 0
    assert repository.search(query="%").total == 0
    assert repository.count() == 20


def test_inactive_products_are_hidden_by_default(seeded, session):
    repository = ProductRepository()
    product = repository.get_by_slug("apricot-jam")
    product.is_active = False
    session.commit()
    assert repository.get_by_slug("apricot-jam") is None
    assert repository.get_by_slug("apricot-jam", include_inactive=True) is not None
    assert repository.search().total == 19


def test_low_stock_list_includes_sold_out(seeded):
    slugs = [product.slug for product in ProductRepository().list_low_stock(threshold=5)]
    assert slugs[0] == "rosehip-jam"
    assert "apricot-jam" not in slugs


def test_user_lookup_by_email_is_case_insensitive(seeded):
    assert UserRepository().get_by_email(DEMO_CLIENT_EMAIL.upper()) is not None

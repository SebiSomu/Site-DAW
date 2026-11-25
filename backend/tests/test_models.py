import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Address, Order, OrderItem, OrderStatusCode, Product, Review, RoleName, User
from app.repositories import (
    AddressRepository,
    CategoryRepository,
    OrderStatusRepository,
    ProductRepository,
    RoleRepository,
    UserRepository,
)
from app.seed import DEMO_CLIENT_EMAIL


def make_user(email: str, role_name: RoleName = RoleName.CLIENT) -> User:
    role = RoleRepository().get_by_name(role_name)
    user = User(email=email, first_name="Anna", last_name="Pop", role=role)
    user.set_password("Secure-Password-1")
    return user


def test_password_is_hashed_with_scrypt_and_verifies(seeded):
    user = make_user("ana@example.com")
    assert user.password_hash.startswith("scrypt:")
    assert "Secure-Password-1" not in user.password_hash
    assert user.check_password("Secure-Password-1")
    assert not user.check_password("wrong-password")


def test_duplicate_email_violates_unique_constraint(seeded, session):
    session.add(make_user("duplicate@example.com"))
    session.commit()
    session.add(make_user("duplicate@example.com"))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_foreign_keys_are_enforced(seeded, session):
    session.add(
        Product(
            category_id=9999,
            name="Ghost Jam",
            slug="ghost-jam",
            description="The category does not exist.",
            price_cents=1000,
            weight_grams=200,
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_category_with_products_cannot_be_deleted(seeded, session):
    category = CategoryRepository().get_by_slug("jams")
    session.delete(category)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


@pytest.mark.parametrize("field, value", [("stock", -1), ("price_cents", 0), ("weight_grams", 0)])
def test_product_check_constraints(seeded, session, field, value):
    product = ProductRepository().get_by_slug("apricot-jam")
    setattr(product, field, value)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


@pytest.mark.parametrize("rating", [0, 6])
def test_review_rating_must_be_between_one_and_five(seeded, session, rating):
    user = UserRepository().get_by_email(DEMO_CLIENT_EMAIL)
    product = ProductRepository().get_by_slug("apricot-jam")
    session.add(Review(user=user, product=product, rating=rating, comment="Test"))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_one_review_per_user_and_product(seeded, session):
    user = UserRepository().get_by_email(DEMO_CLIENT_EMAIL)
    product = ProductRepository().get_by_slug("apricot-jam")
    session.add(Review(user=user, product=product, rating=5, comment="Excellent"))
    session.commit()
    session.add(Review(user=user, product=product, rating=4, comment="Again"))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_order_total_is_computed_from_items(seeded, session):
    user = UserRepository().get_by_email(DEMO_CLIENT_EMAIL)
    address = AddressRepository().add(
        Address(user=user, street="5 Lungă Street", city="Brașov", county="Brașov", postal_code="500035")
    )
    products = ProductRepository()
    apricot = products.get_by_slug("apricot-jam")
    plum = products.get_by_slug("plum-butter")
    status = OrderStatusRepository().get_by_code(OrderStatusCode.PENDING_PAYMENT)
    order = Order(
        user=user,
        address=address,
        status=status,
        items=[
            OrderItem(product=apricot, quantity=2, unit_price_cents=2450),
            OrderItem(product=plum, quantity=1, unit_price_cents=2500),
        ],
    )
    session.add(order)
    session.commit()
    assert order.total_cents == 7400
    assert order.is_cancellable
    assert "total" not in Order.__table__.columns


def test_average_rating_is_computed(seeded, session):
    product = ProductRepository().get_by_slug("raspberry-jam")
    assert product.average_rating is None
    client = UserRepository().get_by_email(DEMO_CLIENT_EMAIL)
    other = make_user("neighbour@example.com")
    session.add_all(
        [
            Review(user=client, product=product, rating=5, comment="Just like Grandma's"),
            Review(user=other, product=product, rating=4, comment="Very good"),
        ]
    )
    session.commit()
    assert product.average_rating == 4.5


def test_admin_role_is_detected(seeded, session):
    admin = make_user("owner@example.com", RoleName.ADMIN)
    session.add(admin)
    client = make_user("client2@example.com", RoleName.CLIENT)
    session.add(client)
    assert admin.is_admin
    assert not client.is_admin


def test_user_and_product_helpers(seeded):
    client = UserRepository().get_by_email(DEMO_CLIENT_EMAIL)
    jar = ProductRepository().list_all()[0]

    assert client.full_name == f"{client.first_name} {client.last_name}"
    assert not client.is_admin
    assert repr(client) == f"<User {DEMO_CLIENT_EMAIL}>"
    assert repr(client.role) == "<Role client>"
    jar.stock = 0
    assert not jar.is_in_stock
    jar.stock = 3
    assert jar.is_in_stock

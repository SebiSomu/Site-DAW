from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.mixins import IdMixin, TimestampMixin

product_ingredients = Table(
    "product_ingredients",
    db.metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("ingredient_id", ForeignKey("ingredients.id", ondelete="RESTRICT"), primary_key=True),
)


class Category(IdMixin, db.Model):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Ingredient(IdMixin, db.Model):
    __tablename__ = "ingredients"

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)

    products: Mapped[list["Product"]] = relationship(secondary=product_ingredients, back_populates="ingredients")


class Product(IdMixin, TimestampMixin, db.Model):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price_bani > 0", name="price_positive"),
        CheckConstraint("weight_grams > 0", name="weight_positive"),
        CheckConstraint("stock >= 0", name="stock_not_negative"),
    )

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price_bani: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_grams: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category: Mapped[Category] = relationship(back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.position"
    )
    ingredients: Mapped[list[Ingredient]] = relationship(secondary=product_ingredients, back_populates="products")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")
    reviews: Mapped[list["Review"]] = relationship(back_populates="product", cascade="all, delete-orphan")

    @property
    def is_in_stock(self) -> bool:
        return self.stock > 0

    @property
    def average_rating(self) -> float | None:
        if not self.reviews:
            return None
        return round(sum(review.rating for review in self.reviews) / len(self.reviews), 1)


class ProductImage(IdMixin, db.Model):
    __tablename__ = "product_images"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    alt_text: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    product: Mapped[Product] = relationship(back_populates="images")

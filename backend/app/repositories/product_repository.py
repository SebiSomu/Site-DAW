from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import selectinload

from app.models import Category, Product
from app.repositories.base import SqlAlchemyRepository


class ProductSort(str, Enum):
    NEWEST = "newest"
    PRICE_ASC = "price-asc"
    PRICE_DESC = "price-desc"
    NAME = "name"


@dataclass(frozen=True)
class ProductPage:
    items: Sequence[Product]
    total: int
    page: int
    per_page: int

    @property
    def pages(self) -> int:
        return max(1, -(-self.total // self.per_page))


SORT_ORDER = {
    ProductSort.NEWEST: (Product.created_at.desc(), Product.id.desc()),
    ProductSort.PRICE_ASC: (Product.price_bani.asc(), Product.id.asc()),
    ProductSort.PRICE_DESC: (Product.price_bani.desc(), Product.id.asc()),
    ProductSort.NAME: (Product.name.asc(), Product.id.asc()),
}


class ProductRepository(SqlAlchemyRepository[Product]):
    model = Product

    def get_by_slug(self, slug: str, include_inactive: bool = False) -> Product | None:
        statement = (
            select(Product)
            .where(Product.slug == slug)
            .options(selectinload(Product.images), selectinload(Product.ingredients), selectinload(Product.reviews))
        )
        if not include_inactive:
            statement = statement.where(Product.is_active.is_(True))
        return self.session.scalars(statement).first()

    def search(
        self,
        query: str | None = None,
        category_slug: str | None = None,
        sort: ProductSort = ProductSort.NEWEST,
        page: int = 1,
        per_page: int = 12,
        include_inactive: bool = False,
    ) -> ProductPage:
        statement = self._filtered(query, category_slug, include_inactive)
        total = self.session.scalar(select(func.count()).select_from(statement.subquery())) or 0
        page = max(1, page)
        items = self.session.scalars(
            statement.options(selectinload(Product.images))
            .order_by(*SORT_ORDER[sort])
            .limit(per_page)
            .offset((page - 1) * per_page)
        ).all()
        return ProductPage(items=items, total=total, page=page, per_page=per_page)

    def list_low_stock(self, threshold: int = 5) -> Sequence[Product]:
        statement = select(Product).where(Product.stock <= threshold).order_by(Product.stock.asc())
        return self.session.scalars(statement).all()

    def slug_exists(self, slug: str) -> bool:
        return self.find_one_by(slug=slug) is not None

    def _filtered(self, query: str | None, category_slug: str | None, include_inactive: bool) -> Select:
        statement = select(Product)
        if not include_inactive:
            statement = statement.where(Product.is_active.is_(True))
        if category_slug:
            statement = statement.join(Product.category).where(Category.slug == category_slug)
        if query and query.strip():
            pattern = f"%{self._escape_like(query.strip())}%"
            statement = statement.where(
                or_(Product.name.ilike(pattern, escape="\\"), Product.description.ilike(pattern, escape="\\"))
            )
        return statement

    @staticmethod
    def _escape_like(value: str) -> str:
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

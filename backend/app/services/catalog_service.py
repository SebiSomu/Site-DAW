from typing import Sequence

from app.errors import NotFoundError
from app.models import Category, Product
from app.repositories import CategoryRepository, ProductPage, ProductRepository
from app.schemas import ProductQuery


class CatalogService:
    def __init__(self, products: ProductRepository | None = None, categories: CategoryRepository | None = None) -> None:
        self.products = products or ProductRepository()
        self.categories = categories or CategoryRepository()

    def list_categories(self) -> Sequence[Category]:
        return self.categories.list_all()

    def search_products(self, query: ProductQuery) -> ProductPage:
        return self.products.search(
            query=query.q,
            category_slug=query.category,
            sort=query.sort,
            page=query.page,
            per_page=query.per_page,
        )

    def get_product(self, slug: str) -> Product:
        product = self.products.get_by_slug(slug)
        if product is None:
            raise NotFoundError("We could not find this jar. It may be sold out for the season.")
        return product

    def public_paths(self) -> list[str]:
        category_paths = [f"/products?category={category.slug}" for category in self.list_categories()]
        product_paths = [f"/products/{product.slug}" for product in self.products.list_active()]
        return ["/", "/products", *category_paths, *product_paths]

from collections import Counter
from typing import Sequence

from app.models import CartLine, CartSummary
from app.repositories import ProductRepository
from app.schemas import CartItemRequest


class CartService:
    def __init__(self, products: ProductRepository | None = None) -> None:
        self.products = products or ProductRepository()

    def price(self, items: Sequence[CartItemRequest]) -> CartSummary:
        quantities: Counter[int] = Counter()
        for item in items:
            quantities[item.product_id] += item.quantity
        products = {product.id: product for product in self.products.list_active_by_ids(list(quantities))}
        return CartSummary(
            lines=[CartLine(products[product_id], quantity) for product_id, quantity in quantities.items() if product_id in products],
            missing_product_ids=[product_id for product_id in quantities if product_id not in products],
        )

from dataclasses import dataclass

from app.models.catalog import Product


@dataclass(frozen=True)
class CartLine:
    product: Product
    quantity: int

    @property
    def subtotal_cents(self) -> int:
        return self.quantity * self.product.price_cents

    @property
    def is_available(self) -> bool:
        return self.quantity <= self.product.stock


@dataclass(frozen=True)
class CartSummary:
    lines: list[CartLine]
    missing_product_ids: list[int]

    @property
    def total_cents(self) -> int:
        return sum(line.subtotal_cents for line in self.lines if line.is_available)

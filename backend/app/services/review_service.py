from app.errors import ConflictError, ForbiddenError, NotFoundError
from app.extensions import db
from app.models import Product, Review
from app.repositories import OrderRepository, ProductRepository, ReviewRepository
from app.schemas import ReviewRequest
from app.security.sanitize import plain_text
from app.services.activity_logger import activity_logger


class ReviewService:
    def __init__(
        self,
        reviews: ReviewRepository | None = None,
        orders: OrderRepository | None = None,
        products: ProductRepository | None = None,
    ) -> None:
        self.reviews = reviews or ReviewRepository()
        self.orders = orders or OrderRepository()
        self.products = products or ProductRepository()

    def can_review(self, user_id: int, product_id: int) -> bool:
        product = self._get_product(product_id)
        return (
            self.orders.user_has_purchased(user_id, product.id)
            and self.reviews.get_by_user_and_product(user_id, product.id) is None
        )

    def add(self, user_id: int, product_id: int, data: ReviewRequest) -> Review:
        product = self._get_product(product_id)
        if not self.orders.user_has_purchased(user_id, product.id):
            raise ForbiddenError("You can review a jar once you have bought it.")
        if self.reviews.get_by_user_and_product(user_id, product.id) is not None:
            raise ConflictError("You have already reviewed this jar.")
        review = self.reviews.add(
            Review(user_id=user_id, product_id=product.id, rating=data.rating, comment=plain_text(data.comment))
        )
        db.session.commit()
        activity_logger.info("review_posted", f"product={product.id} rating={review.rating}")
        return review

    def _get_product(self, product_id: int) -> Product:
        product = self.products.get(product_id)
        if product is None or not product.is_active:
            raise NotFoundError("We could not find this jar.")
        return product

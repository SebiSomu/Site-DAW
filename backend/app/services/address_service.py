from typing import Sequence

from app.errors import NotFoundError
from app.extensions import db
from app.models import Address
from app.repositories import AddressRepository
from app.schemas import AddressRequest
from app.services.activity_logger import activity_logger


class AddressService:
    def __init__(self, addresses: AddressRepository | None = None) -> None:
        self.addresses = addresses or AddressRepository()

    def list_for_user(self, user_id: int) -> Sequence[Address]:
        return self.addresses.list_active_for_user(user_id)

    def add(self, user_id: int, data: AddressRequest) -> Address:
        address = self.addresses.add(Address(user_id=user_id, **data.model_dump()))
        db.session.commit()
        activity_logger.info("address_added", f"address={address.id}")
        return address

    def get_active(self, address_id: int, user_id: int) -> Address:
        address = self.addresses.get_for_user(address_id, user_id)
        if address is None or address.is_archived:
            raise NotFoundError("We could not find this address.")
        return address

    def archive(self, address_id: int, user_id: int) -> None:
        address = self.get_active(address_id, user_id)
        address.is_archived = True
        db.session.commit()
        activity_logger.info("address_archived", f"address={address.id}")

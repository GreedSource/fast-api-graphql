from server.decorators.singleton_decorator import singleton
from server.models.dto.contact_dto import ContactItemModel, CreateContactModel, UpdateContactModel
from server.repositories.contact_repository import ContactRepository
from server.services.base_service import BaseService


@singleton
class ContactService(BaseService[CreateContactModel, UpdateContactModel, ContactItemModel]):
    repository = ContactRepository()
    item_model = ContactItemModel
    resource_not_found = "Contact not found"

from server.models.dto.contact_dto import CreateContactModel, UpdateContactModel
from server.schema.crm_resource_resolver import CRMResourceResolver
from server.services.contact_service import ContactService


class ContactResolver(CRMResourceResolver):
    module = "contacts"
    singular = "Contact"
    create_model = CreateContactModel
    update_model = UpdateContactModel
    service = ContactService()

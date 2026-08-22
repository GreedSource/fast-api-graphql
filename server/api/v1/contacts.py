from server.api.crud_router import build_scoped_crud_router
from server.models.dto.contact_dto import CreateContactModel, UpdateContactModel
from server.services.contact_service import ContactService

router = build_scoped_crud_router("contacts", ContactService(), CreateContactModel, UpdateContactModel)

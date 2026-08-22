from server.decorators.singleton_decorator import singleton
from server.models.orm.contact_orm import ContactORM
from server.repositories.scoped_resource_repository import ScopedResourceRepository


@singleton
class ContactRepository(ScopedResourceRepository[ContactORM]):
    model = ContactORM

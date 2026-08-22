from server.decorators.singleton_decorator import singleton
from server.models.orm.lead_orm import LeadORM
from server.repositories.scoped_resource_repository import ScopedResourceRepository


@singleton
class LeadRepository(ScopedResourceRepository[LeadORM]):
    model = LeadORM

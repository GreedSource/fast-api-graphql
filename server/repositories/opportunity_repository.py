from server.decorators.singleton_decorator import singleton
from server.models.orm.opportunity_orm import OpportunityORM
from server.repositories.scoped_resource_repository import ScopedResourceRepository


@singleton
class OpportunityRepository(ScopedResourceRepository[OpportunityORM]):
    model = OpportunityORM

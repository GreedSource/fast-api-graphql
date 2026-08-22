from server.decorators.singleton_decorator import singleton
from server.models.orm.company_orm import CompanyORM
from server.repositories.scoped_resource_repository import ScopedResourceRepository


@singleton
class CompanyRepository(ScopedResourceRepository[CompanyORM]):
    model = CompanyORM

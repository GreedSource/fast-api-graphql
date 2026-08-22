from server.decorators.singleton_decorator import singleton
from server.models.orm.crm_organization_orm import CRMOrganizationORM
from server.repositories.base_repository import BaseRepository


@singleton
class CRMOrganizationRepository(BaseRepository[CRMOrganizationORM]):
    model = CRMOrganizationORM

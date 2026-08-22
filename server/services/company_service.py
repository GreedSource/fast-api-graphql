from server.decorators.singleton_decorator import singleton
from server.models.dto.company_dto import CompanyItemModel, CreateCompanyModel, UpdateCompanyModel
from server.repositories.company_repository import CompanyRepository
from server.services.base_service import BaseService


@singleton
class CompanyService(BaseService[CreateCompanyModel, UpdateCompanyModel, CompanyItemModel]):
    repository = CompanyRepository()
    item_model = CompanyItemModel
    resource_not_found = "Company not found"

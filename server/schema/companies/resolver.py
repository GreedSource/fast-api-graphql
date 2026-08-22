from server.models.dto.company_dto import CreateCompanyModel, UpdateCompanyModel
from server.schema.crm_resource_resolver import CRMResourceResolver
from server.services.company_service import CompanyService


class CompanyResolver(CRMResourceResolver):
    module = "companies"
    singular = "Company"
    create_model = CreateCompanyModel
    update_model = UpdateCompanyModel
    service = CompanyService()

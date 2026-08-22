from server.api.crud_router import build_scoped_crud_router
from server.models.dto.company_dto import CreateCompanyModel, UpdateCompanyModel
from server.services.company_service import CompanyService

router = build_scoped_crud_router("companies", CompanyService(), CreateCompanyModel, UpdateCompanyModel)

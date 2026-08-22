from datetime import datetime

from pydantic import Field

from server.models.dto.crm_base_dto import CRMResourceCreateModel, CRMResourceItemModel, CRMResourceUpdateModel


class CreateCompanyModel(CRMResourceCreateModel):
    name: str = Field(min_length=1, max_length=160)
    industry: str | None = None
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None


class UpdateCompanyModel(CRMResourceUpdateModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    industry: str | None = None
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    status: str | None = None


class CompanyItemModel(CRMResourceItemModel):
    name: str
    industry: str | None = None
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    status: str
    archived_at: datetime | None = Field(default=None, alias="archivedAt")

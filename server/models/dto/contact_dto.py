import uuid

from pydantic import Field

from server.models.dto.crm_base_dto import CRMResourceCreateModel, CRMResourceItemModel, CRMResourceUpdateModel


class CreateContactModel(CRMResourceCreateModel):
    company_id: uuid.UUID | None = Field(default=None, alias="companyId")
    name: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)
    email: str | None = None
    phone: str | None = None
    position: str | None = None


class UpdateContactModel(CRMResourceUpdateModel):
    company_id: uuid.UUID | None = Field(default=None, alias="companyId")
    name: str | None = None
    lastname: str | None = None
    email: str | None = None
    phone: str | None = None
    position: str | None = None
    status: str | None = None


class ContactItemModel(CRMResourceItemModel):
    company_id: uuid.UUID | None = Field(default=None, alias="companyId")
    name: str
    lastname: str
    email: str | None = None
    phone: str | None = None
    position: str | None = None
    status: str

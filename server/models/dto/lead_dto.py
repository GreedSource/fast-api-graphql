import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.crm_base_dto import CRMResourceCreateModel, CRMResourceItemModel, CRMResourceUpdateModel

LEAD_STATUSES = {"new", "contacted", "qualified", "lost", "opportunity", "archived"}


class LeadFields:
    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value is not None and value not in LEAD_STATUSES:
            raise CustomGraphQLExceptionHelper("Invalid lead status.")
        return value


class CreateLeadModel(LeadFields, CRMResourceCreateModel):
    company_id: uuid.UUID | None = Field(default=None, alias="companyId")
    contact_id: uuid.UUID | None = Field(default=None, alias="contactId")
    name: str = Field(min_length=1, max_length=160)
    source: str | None = None
    status: str = "new"
    score: int = Field(default=0, ge=0, le=100)


class UpdateLeadModel(LeadFields, CRMResourceUpdateModel):
    company_id: uuid.UUID | None = Field(default=None, alias="companyId")
    contact_id: uuid.UUID | None = Field(default=None, alias="contactId")
    name: str | None = None
    source: str | None = None
    status: str | None = None
    score: int | None = Field(default=None, ge=0, le=100)


class LeadItemModel(CRMResourceItemModel):
    company_id: uuid.UUID | None = Field(default=None, alias="companyId")
    contact_id: uuid.UUID | None = Field(default=None, alias="contactId")
    name: str
    source: str | None = None
    status: str
    score: int
    archived_at: datetime | None = Field(default=None, alias="archivedAt")
    converted_at: datetime | None = Field(default=None, alias="convertedAt")


class ConvertLeadModel(BaseModel):
    id: uuid.UUID
    opportunity_name: str = Field(alias="opportunityName", min_length=1, max_length=160)
    value: Decimal = Field(default=0, ge=0)
    probability: int = Field(default=0, ge=0, le=100)
    expected_close_date: datetime | None = Field(default=None, alias="expectedCloseDate")
    model_config = {"populate_by_name": True}

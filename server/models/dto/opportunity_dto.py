import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.crm_base_dto import CRMResourceCreateModel, CRMResourceItemModel, CRMResourceUpdateModel


class CreateOpportunityModel(CRMResourceCreateModel):
    company_id: uuid.UUID | None = Field(default=None, alias="companyId")
    contact_id: uuid.UUID | None = Field(default=None, alias="contactId")
    lead_id: uuid.UUID | None = Field(default=None, alias="leadId")
    name: str = Field(min_length=1, max_length=160)
    value: Decimal = Field(default=0, ge=0)
    probability: int = Field(default=0, ge=0, le=100)
    stage: str = "qualified"
    expected_close_date: datetime | None = Field(default=None, alias="expectedCloseDate")


class UpdateOpportunityModel(CRMResourceUpdateModel):
    name: str | None = None
    value: Decimal | None = Field(default=None, ge=0)
    probability: int | None = Field(default=None, ge=0, le=100)
    stage: str | None = None
    expected_close_date: datetime | None = Field(default=None, alias="expectedCloseDate")


class OpportunityItemModel(CRMResourceItemModel):
    company_id: uuid.UUID | None = Field(default=None, alias="companyId")
    contact_id: uuid.UUID | None = Field(default=None, alias="contactId")
    lead_id: uuid.UUID | None = Field(default=None, alias="leadId")
    name: str
    value: Decimal
    probability: int
    stage: str
    expected_close_date: datetime | None = Field(default=None, alias="expectedCloseDate")
    closed_at: datetime | None = Field(default=None, alias="closedAt")


class CloseOpportunityModel(BaseModel):
    id: uuid.UUID
    stage: str

    @model_validator(mode="after")
    def validate_closed_stage(self):
        if self.stage not in {"won", "lost"}:
            raise CustomGraphQLExceptionHelper("Opportunity can only be closed as won or lost.")
        return self

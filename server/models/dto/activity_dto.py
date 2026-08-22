import uuid
from datetime import datetime

from pydantic import Field

from server.models.dto.crm_base_dto import CRMResourceCreateModel, CRMResourceItemModel, CRMResourceUpdateModel


class CreateActivityModel(CRMResourceCreateModel):
    company_id: uuid.UUID | None = Field(default=None, alias="companyId")
    contact_id: uuid.UUID | None = Field(default=None, alias="contactId")
    lead_id: uuid.UUID | None = Field(default=None, alias="leadId")
    opportunity_id: uuid.UUID | None = Field(default=None, alias="opportunityId")
    activity_type: str = Field(alias="activityType")
    subject: str = Field(min_length=1, max_length=180)
    description: str | None = None
    scheduled_at: datetime | None = Field(default=None, alias="scheduledAt")


class UpdateActivityModel(CRMResourceUpdateModel):
    activity_type: str | None = Field(default=None, alias="activityType")
    subject: str | None = None
    description: str | None = None
    status: str | None = None
    scheduled_at: datetime | None = Field(default=None, alias="scheduledAt")


class ActivityItemModel(CRMResourceItemModel):
    company_id: uuid.UUID | None = Field(default=None, alias="companyId")
    contact_id: uuid.UUID | None = Field(default=None, alias="contactId")
    lead_id: uuid.UUID | None = Field(default=None, alias="leadId")
    opportunity_id: uuid.UUID | None = Field(default=None, alias="opportunityId")
    activity_type: str = Field(alias="activityType")
    subject: str
    description: str | None = None
    status: str
    scheduled_at: datetime | None = Field(default=None, alias="scheduledAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")

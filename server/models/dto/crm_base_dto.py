import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CRMResourceCreateModel(BaseModel):
    organization_id: uuid.UUID = Field(alias="organizationId")
    team_id: uuid.UUID | None = Field(default=None, alias="teamId")
    owner_id: uuid.UUID | None = Field(default=None, alias="ownerId")
    model_config = {"populate_by_name": True}

    @field_validator("*", mode="before")
    @classmethod
    def strip_strings(cls, value):
        return value.strip() if isinstance(value, str) else value


class CRMResourceUpdateModel(BaseModel):
    id: uuid.UUID
    team_id: uuid.UUID | None = Field(default=None, alias="teamId")
    owner_id: uuid.UUID | None = Field(default=None, alias="ownerId")
    model_config = {"populate_by_name": True}


class CRMResourceItemModel(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID = Field(alias="organizationId")
    team_id: uuid.UUID | None = Field(default=None, alias="teamId")
    owner_id: uuid.UUID | None = Field(default=None, alias="ownerId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    model_config = {"populate_by_name": True, "from_attributes": True}

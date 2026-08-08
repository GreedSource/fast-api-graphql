import uuid
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, RootModel, field_validator

from server.models.dto.project_dto import validate_uuid_value


class CreateAuditLogModel(BaseModel):
    user_id: Optional[uuid.UUID] = Field(default=None, alias="userId")
    module: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)
    resource_type: Optional[str] = Field(default=None, alias="resourceType", max_length=50)
    resource_id: Optional[str] = Field(default=None, alias="resourceId", max_length=100)
    status: str = Field(..., min_length=1, max_length=30)
    metadata_json: dict[str, Any] | None = Field(default=None, alias="metadata")

    model_config = {"populate_by_name": True}

    @field_validator("user_id", mode="before")
    @classmethod
    def validate_user_id(cls, value):
        return validate_uuid_value(value, "Audit log userId is not a valid UUID.")

    @field_validator("module", "action", "resource_type", "resource_id", "status", mode="before")
    @classmethod
    def strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class AuditLogItemModel(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = Field(default=None, alias="userId")
    module: str
    action: str
    resource_type: Optional[str] = Field(default=None, alias="resourceType")
    resource_id: Optional[str] = Field(default=None, alias="resourceId")
    status: str
    metadata_json: dict[str, Any] | None = Field(default=None, alias="metadata")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class AuditLogListModel(RootModel):
    root: List[AuditLogItemModel]

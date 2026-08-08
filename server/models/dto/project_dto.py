import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel, field_validator

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper

PROJECT_STATUSES = {"active", "archived"}


def validate_uuid_value(value, message: str):
    if value is None or isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        raise CustomGraphQLExceptionHelper(message)


class CreateProjectModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(default=None)
    owner_id: Optional[uuid.UUID] = Field(default=None, alias="ownerId")

    model_config = {"populate_by_name": True}

    @field_validator("name", "description", mode="before")
    @classmethod
    def strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("owner_id", mode="before")
    @classmethod
    def validate_owner_id(cls, value):
        return validate_uuid_value(value, "ownerId is not a valid UUID.")


class UpdateProjectModel(BaseModel):
    id: uuid.UUID
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    owner_id: Optional[uuid.UUID] = Field(default=None, alias="ownerId")

    model_config = {"populate_by_name": True}

    @field_validator("id", "owner_id", mode="before")
    @classmethod
    def validate_uuid(cls, value):
        return validate_uuid_value(value, "Project UUID field is not valid.")

    @field_validator("name", "description", "status", mode="before")
    @classmethod
    def strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value is None:
            return value
        if value not in PROJECT_STATUSES:
            raise CustomGraphQLExceptionHelper("Invalid project status.")
        return value


class ProjectItemModel(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    status: str
    owner_id: Optional[uuid.UUID] = Field(default=None, alias="ownerId")
    archived_at: Optional[datetime] = Field(default=None, alias="archivedAt")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class ProjectListModel(RootModel):
    root: List[ProjectItemModel]

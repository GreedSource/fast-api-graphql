import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, RootModel, field_validator

from server.models.dto.project_dto import validate_uuid_value


class AddProjectMemberModel(BaseModel):
    project_id: uuid.UUID = Field(..., alias="projectId")
    user_id: uuid.UUID = Field(..., alias="userId")
    project_role_id: uuid.UUID = Field(..., alias="projectRoleId")

    model_config = {"populate_by_name": True}

    @field_validator("project_id", "user_id", "project_role_id", mode="before")
    @classmethod
    def validate_uuid(cls, value):
        return validate_uuid_value(value, "Project member UUID field is not valid.")


class UpdateProjectMemberRoleModel(BaseModel):
    id: uuid.UUID
    project_role_id: uuid.UUID = Field(..., alias="projectRoleId")

    model_config = {"populate_by_name": True}

    @field_validator("id", "project_role_id", mode="before")
    @classmethod
    def validate_uuid(cls, value):
        return validate_uuid_value(value, "Project member UUID field is not valid.")


class ProjectRoleItemModel(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    active: bool

    model_config = {"from_attributes": True}


class ProjectMemberItemModel(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID = Field(..., alias="projectId")
    user_id: uuid.UUID = Field(..., alias="userId")
    project_role_id: uuid.UUID = Field(..., alias="projectRoleId")
    project_role: ProjectRoleItemModel | None = Field(default=None, alias="projectRole")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class ProjectMemberListModel(RootModel):
    root: List[ProjectMemberItemModel]

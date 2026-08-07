import uuid
from typing import List

from pydantic import BaseModel, Field, RootModel, field_validator

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


class PermissionItemModel(BaseModel):
    id: uuid.UUID = Field(..., description="Permission ID")
    module_id: uuid.UUID = Field(..., alias="moduleId", description="Module ID")
    action_id: uuid.UUID = Field(..., alias="actionId", description="Action ID")
    module_key: str = Field(..., alias="moduleKey", description="Module key/name")
    action_key: str = Field(..., alias="actionKey", description="Action key/name")
    description: str | None = Field(None, description="Permission description")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }

    @field_validator("id", "module_id", "action_id", mode="before")
    @classmethod
    def validate_uuid(cls, value):
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(str(value))
        except (ValueError, TypeError):
            raise CustomGraphQLExceptionHelper("Invalid UUID format for Permission field.")


class CreatePermissionModel(BaseModel):
    module_id: str = Field(..., alias="moduleId", description="Module UUID or key")
    action_id: str = Field(..., alias="actionId", description="Action UUID or key")
    description: str | None = Field(None, max_length=255, description="Permission description")

    model_config = {"populate_by_name": True}


class PermissionListModel(RootModel):
    root: List[PermissionItemModel]

import uuid
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel, field_validator

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


class PermissionKeyModel(BaseModel):
    action: str = Field(..., description="Action key")
    type: str = Field(..., description="Module key")


class AssignPermissionsModel(BaseModel):
    role_id: uuid.UUID = Field(..., alias="roleId")
    permission_ids: list[uuid.UUID] = Field(..., alias="permissionIds")

    model_config = {"populate_by_name": True}

    @field_validator("role_id", mode="before")
    @classmethod
    def validate_role_id(cls, v):
        if isinstance(v, uuid.UUID):
            return v
        try:
            return uuid.UUID(str(v))
        except (ValueError, TypeError):
            raise CustomGraphQLExceptionHelper("Invalid roleId UUID.")

    @field_validator("permission_ids", mode="before")
    @classmethod
    def validate_permission_ids(cls, v):
        if not isinstance(v, list):
            raise CustomGraphQLExceptionHelper("permissionIds must be a list.")
        res = []
        for item in v:
            if isinstance(item, uuid.UUID):
                res.append(item)
            else:
                try:
                    res.append(uuid.UUID(str(item)))
                except (ValueError, TypeError):
                    raise CustomGraphQLExceptionHelper("Invalid UUID in permissionIds.")
        return res


class RoleItemModel(BaseModel):
    id: uuid.UUID = Field(..., description="Role ID")
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    active: bool = Field(True, description="Indicates if the role is active")
    permissions: List[PermissionKeyModel] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }

    @field_validator("id", mode="before")
    @classmethod
    def validate_uuid(cls, v):
        if isinstance(v, uuid.UUID):
            return v
        try:
            return uuid.UUID(str(v))
        except (ValueError, TypeError):
            raise CustomGraphQLExceptionHelper("Invalid Role UUID.")

    @field_validator("permissions", mode="before")
    @classmethod
    def map_permissions(cls, value):
        if value is None:
            return []

        mapped = []
        for permission in value:
            if isinstance(permission, dict):
                mapped.append(permission)
                continue

            module = getattr(permission, "module", None)
            action = getattr(permission, "action", None)
            if module and action:
                mapped.append(
                    {
                        "type": getattr(module, "key", None) or getattr(module, "name", None),
                        "action": getattr(action, "key", None) or getattr(action, "name", None),
                    }
                )

        return mapped


class RoleListModel(RootModel):
    root: List[RoleItemModel]


class CreateRoleModel(BaseModel):
    name: str = Field(..., description="Role name", min_length=2)
    description: Optional[str] = Field(None, description="Role description")
    active: bool = Field(True, description="Indicates if the role is active")


class UpdateRoleModel(BaseModel):
    id: uuid.UUID = Field(..., description="Role ID")
    name: Optional[str] = Field(None, description="Role name", min_length=2)
    description: Optional[str] = Field(None, description="Role description")
    active: Optional[bool] = Field(None, description="Indicates if the role is active")

    @field_validator("id", mode="before")
    @classmethod
    def validate_uuid(cls, v):
        if isinstance(v, uuid.UUID):
            return v
        try:
            return uuid.UUID(str(v))
        except (ValueError, TypeError):
            raise CustomGraphQLExceptionHelper("Invalid Role UUID.")

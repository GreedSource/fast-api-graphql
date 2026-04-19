from pydantic import BaseModel, Field, RootModel, ValidationInfo, field_validator

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


class AssignPermissionsModel(BaseModel):
    role_id: str = Field(..., alias="roleId")
    permission_ids: list[str] = Field(..., alias="permissionIds")


class PermissionKeyModel(BaseModel):
    action: str = Field(..., description="Action key")
    type: str = Field(..., description="Module key")


class RoleItemModel(BaseModel):
    id: str | None = Field(None, alias="_id")
    name: str
    description: str | None = None
    active: bool | None = True
    permissions: list[PermissionKeyModel] = Field(default_factory=list)

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: object, info: ValidationInfo) -> str:
        if not v:
            raise CustomGraphQLExceptionHelper(f"{info.field_name} not valid.")
        return str(v)

    model_config = {"populate_by_name": True}


# Crear un modelo que sea una lista de RoleItemModel
class RoleListModel(RootModel[list[RoleItemModel]]):
    root: list[RoleItemModel]


class CreateRoleModel(BaseModel):
    name: str = Field(..., description="Role name")
    description: str | None = Field(None, description="Role description")
    active: bool | None = Field(True, description="Indicates if the role is active")


class UpdateRoleModel(BaseModel):
    id: str = Field(..., description="Role ID")
    name: str | None = Field(None, description="Role name")
    description: str | None = Field(None, description="Role description")
    active: bool | None = Field(None, description="Indicates if the role is active")

# server/models/role_model.py
from pydantic import BaseModel, Field, RootModel, ValidationInfo, field_validator
from typing import List, Optional

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


class RoleItemModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    active: Optional[bool] = Field(True, description="Indicates if the role is active")

    @field_validator("id", mode="before")
    def validate_id(cls, v, info: ValidationInfo):
        if not v:
            raise CustomGraphQLExceptionHelper(f"{info.field_name} not valid.")
        return str(v)

    model_config = {
        "populate_by_name": True  # permite pasar 'id' o '_id' al instanciar
    }


# Crear un modelo que sea una lista de RoleItemModel
class RoleListModel(RootModel):
    root: List[RoleItemModel]  # <--- lista de roles


class CreateRoleModel(BaseModel):
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    active: Optional[bool] = Field(True, description="Indicates if the role is active")


class UpdateRoleModel(BaseModel):
    id: str = Field(..., description="Role ID")
    name: Optional[str] = Field(None, description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    active: Optional[bool] = Field(None, description="Indicates if the role is active")

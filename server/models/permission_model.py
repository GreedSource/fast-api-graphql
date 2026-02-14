from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, RootModel, ValidationInfo, field_validator

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


class PermissionItemModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id", description="Permission ID")
    description: Optional[str] = Field(default=None, description="Permission description")
    moduleId: str = Field(..., description="Permission type", alias="moduleId")
    actionId: str = Field(..., description="Permission action", alias="actionId")

    model_config = {"populate_by_name": True}

    @field_validator("id", "moduleId", "actionId", mode="before")
    @classmethod
    def validate_and_cast_object_id(cls, value):
        if value is None:
            return value

        # If it's already an ObjectId → convert to str
        if isinstance(value, ObjectId):
            return str(value)

        # If it's a string → validate
        if isinstance(value, str):
            if not ObjectId.is_valid(value):
                raise ValueError("Must be a valid MongoDB ObjectId (24 hex characters)")
            return value

        raise TypeError("Invalid type for ObjectId field")


class CreatePermissionModel(BaseModel):
    module_id: str = Field(..., alias="moduleId", description="Module ID")
    action_id: str = Field(..., alias="actionId", description="Action ID")
    description: Optional[str] = Field(default=None, description="Permission description")

    @field_validator("module_id", "action_id")
    @classmethod
    def validate_object_id(cls, value: str, info: ValidationInfo) -> str:
        if not ObjectId.is_valid(value):
            raise CustomGraphQLExceptionHelper(
                f"{info.field_name}: Must be a valid MongoDB ObjectId (24 hex characters)"
            )
        return value


# Crear un modelo que sea una lista de PermissionItemModel
class PermissionListModel(RootModel):
    root: List[PermissionItemModel]  # <--- lista de permisos

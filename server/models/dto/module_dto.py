import uuid
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel, field_validator

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


class ModuleItemModel(BaseModel):
    id: uuid.UUID = Field(..., description="Module ID")
    name: str = Field(..., description="Module name")
    key: str = Field(..., description="Module key")
    description: Optional[str] = Field(None, description="Module description")
    active: bool = Field(True, description="Indicates if the module is active")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }

    @field_validator("id", mode="before")
    @classmethod
    def validate_uuid(cls, value):
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(str(value))
        except (ValueError, TypeError):
            raise CustomGraphQLExceptionHelper("Invalid Module UUID.")


class ModuleListModel(RootModel):
    root: List[ModuleItemModel]


class CreateModuleModel(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        strip_whitespace=True,
        description="Nombre visible del módulo",
    )
    key: str = Field(
        ...,
        min_length=1,
        max_length=50,
        strip_whitespace=True,
        description="Identificador único del módulo (ej: users, roles)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=255,
        strip_whitespace=True,
        description="Descripción del módulo",
    )
    active: bool = Field(default=True, description="Indica si el módulo está activo")

    @field_validator("key")
    @classmethod
    def normalize_key(cls, v: str) -> str:
        return v.lower().strip()


class UpdateModuleModel(BaseModel):
    id: uuid.UUID = Field(..., description="ID del módulo")
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, strip_whitespace=True)
    key: Optional[str] = Field(default=None, min_length=1, max_length=50, strip_whitespace=True)
    description: Optional[str] = Field(default=None, max_length=255, strip_whitespace=True)
    active: Optional[bool] = Field(default=None)

    @field_validator("key")
    @classmethod
    def normalize_key(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.lower().strip()

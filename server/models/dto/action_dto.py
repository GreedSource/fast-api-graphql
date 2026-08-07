import uuid
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel, field_validator

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


class ActionItemModel(BaseModel):
    id: uuid.UUID = Field(..., description="Action ID")
    name: str = Field(..., description="Action name")
    key: str = Field(..., description="Action key")
    description: Optional[str] = Field(None, description="Action description")
    active: bool = Field(True, description="Indicates if the action is active")

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
            raise CustomGraphQLExceptionHelper("Invalid Action UUID.")


class ActionListModel(RootModel):
    root: List[ActionItemModel]


class CreateActionModel(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        strip_whitespace=True,
        description="Nombre visible de la acción",
    )
    key: str = Field(
        ...,
        min_length=1,
        max_length=50,
        strip_whitespace=True,
        description="Identificador de la acción (ej: create, read, update, delete)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=255,
        strip_whitespace=True,
        description="Descripción de la acción",
    )
    active: bool = Field(default=True, description="Indica si la acción está activa")

    @field_validator("key")
    @classmethod
    def normalize_key(cls, v: str) -> str:
        return v.lower().strip()

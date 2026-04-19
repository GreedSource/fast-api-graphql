from typing import cast

from bson import ObjectId
from pydantic import BaseModel, Field, RootModel, field_validator


class ModuleItemModel(BaseModel):
    id: str | None = Field(None, alias="_id")
    name: str
    key: str
    description: str | None
    active: bool = True

    model_config = {"populate_by_name": True}

    @field_validator("id", mode="before")
    @classmethod
    def cast_object_id(cls, value: object) -> str | None:
        if value is None:
            return value
        if isinstance(value, ObjectId):
            return str(value)
        return cast(str, value)


class ModuleListModel(RootModel[list[ModuleItemModel]]):
    root: list[ModuleItemModel]


class CreateModuleModel(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre visible del módulo",
    )

    key: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Identificador único del módulo",
    )

    description: str | None = Field(
        default=None,
        max_length=255,
        description="Descripción del módulo",
    )

    active: bool = Field(default=True, description="Indica si el módulo está activo")

    @field_validator("key")
    @classmethod
    def normalize_key(cls, v: str) -> str:
        return v.lower()


class UpdateModuleModel(BaseModel):
    id: str = Field(..., description="ID del módulo")

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    key: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    description: str | None = Field(
        default=None,
        max_length=255,
    )

    active: bool | None = Field(default=None)

    @field_validator("key")
    @classmethod
    def normalize_key(cls, v: str) -> str:
        return v.lower()

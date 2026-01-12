from pydantic import BaseModel, Field, RootModel, field_validator
from typing import Optional, List


class ActionItemModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    key: str
    description: Optional[str]
    active: bool = True

    model_config = {"populate_by_name": True}


class ActionListModel(RootModel):
    root: List[ActionItemModel]


class CreateActionModel(BaseModel):
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
        description="Identificador único del módulo",
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
        return v.lower()

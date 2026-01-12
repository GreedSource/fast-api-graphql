import re
from typing import List, Optional
from pydantic import (
    BaseModel,
    Field,
    RootModel,
    ValidationInfo,
    field_validator,
    model_validator,
    EmailStr,
)

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.utils.auth_utils import hash_password


class RegisterModel(BaseModel):
    name: str = Field(..., description="User name", min_length=3)
    lastname: str = Field(..., description="User lastname", min_length=3)
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")
    confirm_password: str = Field(
        ..., description="Password confirmation", alias="confirmPassword"
    )

    @model_validator(mode="before")
    @classmethod
    def trim_all_str_fields(cls, values: dict) -> dict:
        return {k: v.strip() if isinstance(v, str) else v for k, v in values.items()}

    @model_validator(mode="after")
    def check_password_match(self):
        if self.password != self.confirm_password:
            raise CustomGraphQLExceptionHelper("Password mismatch.")
        self.password = hash_password(self.password)
        del self.__dict__["confirm_password"]
        return self

    @field_validator("password", "confirm_password")
    def strong_password(cls, v):
        # Al menos 8 caracteres, una mayúscula, una minúscula, un número y un símbolo
        pattern = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        )
        if not re.match(pattern, v):
            raise CustomGraphQLExceptionHelper(
                "La contraseña debe tener al menos 8 caracteres, incluyendo una mayúscula, "
                "una minúscula, un número y un carácter especial (@$!%*?&)."
            )
        return v

    model_config = {
        "populate_by_name": True  # permite pasar 'id' o '_id' al instanciar
    }


class UpdateUserModel(BaseModel):
    name: Optional[str] = Field(None, description="User name", min_length=3)
    lastname: Optional[str] = Field(None, description="User lastname", min_length=3)
    email: EmailStr | None = Field(None, description="User email")


class UserItemModel(BaseModel):
    id: str = Field(..., alias="_id", description="User ID")
    name: str = Field(..., description="User name")
    lastname: str = Field(..., description="User lastname")
    email: EmailStr = Field(..., description="User email")

    @field_validator("id", mode="before")
    def validate_id(cls, v, info: ValidationInfo):
        if not v:
            raise CustomGraphQLExceptionHelper(f"{info.field_name} not valid.")
        return str(v)

    model_config = {
        "populate_by_name": True  # permite pasar 'id' o '_id' al instanciar
    }


# Crear un modelo que sea una lista de UserItemModel
class UserListModel(RootModel):
    root: List[UserItemModel]  # <--- lista de usuarios

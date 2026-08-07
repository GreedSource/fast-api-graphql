import re
import uuid
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, RootModel, field_validator, model_validator

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.role_dto import RoleItemModel
from server.utils.auth_utils import hash_password


class RegisterModel(BaseModel):
    name: str = Field(..., description="User name", min_length=3)
    lastname: str = Field(..., description="User lastname", min_length=3)
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")
    confirm_password: str = Field(..., description="Password confirmation", alias="confirmPassword")

    @model_validator(mode="before")
    @classmethod
    def trim_all_str_fields(cls, values: dict) -> dict:
        if isinstance(values, dict):
            return {k: v.strip() if isinstance(v, str) else v for k, v in values.items()}
        return values

    @model_validator(mode="after")
    def check_password_match(self):
        if self.password != self.confirm_password:
            raise CustomGraphQLExceptionHelper("Password mismatch.")
        self.password = hash_password(self.password)
        del self.__dict__["confirm_password"]
        return self

    @field_validator("password", "confirm_password")
    def strong_password(cls, v):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(pattern, v):
            raise CustomGraphQLExceptionHelper(
                "La contraseña debe tener al menos 8 caracteres, incluyendo una mayúscula, "
                "una minúscula, un número y un carácter especial (@$!%*?&)."
            )
        return v

    model_config = {"populate_by_name": True}


class ResetPasswordModel(BaseModel):
    token: str = Field(..., description="Reset token from email")
    password: str = Field(..., description="New password")
    confirm_password: str = Field(..., description="Password confirmation", alias="confirmPassword")

    @model_validator(mode="before")
    @classmethod
    def trim_all_str_fields(cls, values: dict) -> dict:
        if isinstance(values, dict):
            return {k: v.strip() if isinstance(v, str) else v for k, v in values.items()}
        return values

    @model_validator(mode="after")
    def check_password_match(self):
        if self.password != self.confirm_password:
            raise CustomGraphQLExceptionHelper("Password mismatch.")
        self.password = hash_password(self.password)
        del self.__dict__["confirm_password"]
        return self

    @field_validator("password", "confirm_password")
    def strong_password(cls, v):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(pattern, v):
            raise CustomGraphQLExceptionHelper(
                "La contraseña debe tener al menos 8 caracteres, incluyendo una mayúscula, "
                "una minúscula, un número y un carácter especial (@$!%*?&)."
            )
        return v

    model_config = {"populate_by_name": True}


class UpdateUserModel(BaseModel):
    name: Optional[str] = Field(None, description="User name", min_length=3)
    lastname: Optional[str] = Field(None, description="User lastname", min_length=3)
    email: Optional[EmailStr] = Field(None, description="User email")
    role_id: Optional[uuid.UUID] = Field(None, alias="roleId", description="User role ID")

    @field_validator("role_id", mode="before")
    @classmethod
    def validate_role_id(cls, value):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(str(value))
        except (ValueError, TypeError):
            raise CustomGraphQLExceptionHelper("roleId is not a valid UUID.")

    model_config = {"populate_by_name": True}


class UserItemModel(BaseModel):
    id: uuid.UUID = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    lastname: str = Field(..., description="User lastname")
    email: EmailStr = Field(..., description="User email")
    role: Optional[RoleItemModel] = Field(None, description="User role")

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v):
        if isinstance(v, uuid.UUID):
            return v
        try:
            return uuid.UUID(str(v))
        except (ValueError, TypeError):
            raise CustomGraphQLExceptionHelper("User ID is not a valid UUID.")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }


class UserListModel(RootModel):
    root: List[UserItemModel]

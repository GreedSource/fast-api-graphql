from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    status: int = Field(..., description="HTTP status code or custom status")
    message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Payload of the response")

    model_config = {
        "populate_by_name": True,  # útil si usas alias en los modelos
    }

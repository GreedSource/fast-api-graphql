import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel, field_validator

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.project_dto import validate_uuid_value

TASK_STATUSES = {"todo", "in_progress", "blocked", "done"}
TASK_PRIORITIES = {"low", "medium", "high", "urgent"}


class CreateTaskModel(BaseModel):
    project_id: uuid.UUID = Field(..., alias="projectId")
    title: str = Field(..., min_length=1, max_length=160)
    description: Optional[str] = None
    priority: str = "medium"
    assignee_id: Optional[uuid.UUID] = Field(default=None, alias="assigneeId")
    created_by_id: Optional[uuid.UUID] = Field(default=None, alias="createdById")
    due_date: Optional[datetime] = Field(default=None, alias="dueDate")

    model_config = {"populate_by_name": True}

    @field_validator("project_id", "assignee_id", "created_by_id", mode="before")
    @classmethod
    def validate_uuid(cls, value):
        return validate_uuid_value(value, "Task UUID field is not valid.")

    @field_validator("title", "description", "priority", mode="before")
    @classmethod
    def strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value):
        if value not in TASK_PRIORITIES:
            raise CustomGraphQLExceptionHelper("Invalid task priority.")
        return value


class UpdateTaskModel(BaseModel):
    id: uuid.UUID
    title: Optional[str] = Field(default=None, min_length=1, max_length=160)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[uuid.UUID] = Field(default=None, alias="assigneeId")
    due_date: Optional[datetime] = Field(default=None, alias="dueDate")

    model_config = {"populate_by_name": True}

    @field_validator("id", "assignee_id", mode="before")
    @classmethod
    def validate_uuid(cls, value):
        return validate_uuid_value(value, "Task UUID field is not valid.")

    @field_validator("title", "description", "status", "priority", mode="before")
    @classmethod
    def strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value is None:
            return value
        if value not in TASK_STATUSES:
            raise CustomGraphQLExceptionHelper("Invalid task status.")
        return value

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value):
        if value is None:
            return value
        if value not in TASK_PRIORITIES:
            raise CustomGraphQLExceptionHelper("Invalid task priority.")
        return value


class TaskItemModel(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID = Field(..., alias="projectId")
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assignee_id: Optional[uuid.UUID] = Field(default=None, alias="assigneeId")
    created_by_id: Optional[uuid.UUID] = Field(default=None, alias="createdById")
    due_date: Optional[datetime] = Field(default=None, alias="dueDate")
    completed_at: Optional[datetime] = Field(default=None, alias="completedAt")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class TaskListModel(RootModel):
    root: List[TaskItemModel]

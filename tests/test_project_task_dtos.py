import pytest

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.project_dto import CreateProjectModel, UpdateProjectModel
from server.models.dto.task_dto import CreateTaskModel, UpdateTaskModel
from tests.factories import PROJECT_ID, TASK_ID, USER_ID, make_project, make_task


def test_create_project_strips_strings_and_validates_owner_id():
    payload = CreateProjectModel(name=" Apollo ", description=" Project Apollo ", ownerId=str(USER_ID))

    assert payload.name == "Apollo"
    assert payload.description == "Project Apollo"
    assert payload.owner_id == USER_ID


def test_update_project_rejects_invalid_status():
    with pytest.raises(CustomGraphQLExceptionHelper):
        UpdateProjectModel(id=PROJECT_ID, status="invalid")


def test_project_item_serializes_aliases_as_json():
    payload = make_project()

    result = CreateProjectModel(name="Apollo").model_dump()
    item = __import__("server.models.dto.project_dto", fromlist=["ProjectItemModel"]).ProjectItemModel

    assert result["name"] == "Apollo"
    assert item.model_validate(payload).model_dump(by_alias=True, mode="json")["ownerId"] == str(USER_ID)


def test_create_task_strips_title_and_validates_priority():
    payload = CreateTaskModel(projectId=str(PROJECT_ID), title=" Build API ", priority="high")

    assert payload.project_id == PROJECT_ID
    assert payload.title == "Build API"
    assert payload.priority == "high"


def test_update_task_rejects_invalid_status():
    with pytest.raises(CustomGraphQLExceptionHelper):
        UpdateTaskModel(id=TASK_ID, status="invalid")


def test_create_task_accepts_status_for_kanban_creation():
    payload = CreateTaskModel(projectId=str(PROJECT_ID), title="Build API", status="in_progress")

    assert payload.status == "in_progress"


def test_create_task_rejects_invalid_status():
    with pytest.raises(CustomGraphQLExceptionHelper):
        CreateTaskModel(projectId=str(PROJECT_ID), title="Build API", status="invalid")


def test_task_item_serializes_aliases_as_json():
    item = __import__("server.models.dto.task_dto", fromlist=["TaskItemModel"]).TaskItemModel

    result = item.model_validate(make_task()).model_dump(by_alias=True, mode="json")

    assert result["projectId"] == str(PROJECT_ID)
    assert result["assigneeId"] == str(USER_ID)

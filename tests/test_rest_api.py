from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server import create_app
from server.api.dependencies import get_current_user, require_rest_permission
from server.api.v1 import projects
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


def user_with(*permissions):
    return {
        "id": "40000000-0000-0000-0000-000000000001",
        "role": {
            "name": "test",
            "permissions": [
                {"type": permission.split(".", 1)[0], "action": permission.split(".", 1)[1]}
                for permission in permissions
            ],
        },
    }


def test_rest_api_and_graphql_are_exposed_together():
    app = create_app()
    paths = app.openapi()["paths"]

    assert "/graphql" in paths
    assert "/api/v1/projects" in paths
    assert "/api/v1/leads/{lead_id}/convert" in paths
    assert "/api/v1/opportunities/{opportunity_id}/close" in paths


@pytest.mark.asyncio
async def test_rest_api_rejects_missing_token_with_401():
    request = SimpleNamespace(headers={}, cookies={})

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await get_current_user(request)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_rest_api_rejects_missing_permission_with_403():
    dependency = require_rest_permission("projects", "create")

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await dependency(user_with("projects.read"))

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_rest_project_list_delegates_to_existing_service(monkeypatch):
    service = SimpleNamespace(get_all=AsyncMock(return_value=[{"id": "project-1"}]))
    monkeypatch.setattr(projects, "service", service)

    response = await projects.list_projects(False, user_with("projects.read"))

    assert response["data"] == [{"id": "project-1"}]
    service.get_all.assert_awaited_once_with(False)

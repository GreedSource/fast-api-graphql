from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.project_member_dto import AddProjectMemberModel, UpdateProjectMemberRoleModel
from server.services.project_member_service import ProjectMemberService
from tests.factories import PROJECT_ID, PROJECT_MEMBER_ID, PROJECT_ROLE_ID, USER_ID, make_project, make_project_member


@pytest.mark.asyncio
async def test_project_member_service_add_member_validates_dependencies_and_serializes():
    repository = SimpleNamespace(
        find_project_role_by_id=AsyncMock(return_value=SimpleNamespace(id=PROJECT_ROLE_ID)),
        find_by_project_and_user=AsyncMock(return_value=None),
        create=AsyncMock(return_value=make_project_member()),
    )
    service = ProjectMemberService()
    service._ProjectMemberService__repository = repository
    service._ProjectMemberService__project_repository = SimpleNamespace(
        find_by_id=AsyncMock(return_value=make_project())
    )
    service._ProjectMemberService__user_repository = SimpleNamespace(
        find_by_id=AsyncMock(return_value=SimpleNamespace(id=USER_ID))
    )

    result = await service.add_member(
        AddProjectMemberModel(projectId=PROJECT_ID, userId=USER_ID, projectRoleId=PROJECT_ROLE_ID)
    )

    assert result["id"] == str(PROJECT_MEMBER_ID)
    assert result["projectRole"]["name"] == "developer"


@pytest.mark.asyncio
async def test_project_member_service_rejects_duplicate_member():
    service = ProjectMemberService()
    service._ProjectMemberService__repository = SimpleNamespace(
        find_project_role_by_id=AsyncMock(return_value=SimpleNamespace(id=PROJECT_ROLE_ID)),
        find_by_project_and_user=AsyncMock(return_value=make_project_member()),
    )
    service._ProjectMemberService__project_repository = SimpleNamespace(
        find_by_id=AsyncMock(return_value=make_project())
    )
    service._ProjectMemberService__user_repository = SimpleNamespace(
        find_by_id=AsyncMock(return_value=SimpleNamespace(id=USER_ID))
    )

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.add_member(
            AddProjectMemberModel(projectId=PROJECT_ID, userId=USER_ID, projectRoleId=PROJECT_ROLE_ID)
        )

    assert exc_info.value.message == "El usuario ya es miembro del proyecto"


@pytest.mark.asyncio
async def test_project_member_service_update_role_rejects_missing_role():
    service = ProjectMemberService()
    service._ProjectMemberService__repository = SimpleNamespace(find_project_role_by_id=AsyncMock(return_value=None))

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await service.update_member_role(
            UpdateProjectMemberRoleModel(id=PROJECT_MEMBER_ID, projectRoleId=PROJECT_ROLE_ID)
        )

    assert exc_info.value.message == "Project role not found"

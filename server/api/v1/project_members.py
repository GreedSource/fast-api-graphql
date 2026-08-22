import uuid

from fastapi import APIRouter, Depends, status

from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.models.dto.project_member_dto import AddProjectMemberModel, UpdateProjectMemberRoleModel
from server.services.authorization_service import AuthorizationService
from server.services.project_member_service import ProjectMemberService

router = APIRouter(prefix="/projects/{project_id}/members", tags=["Project Members"])
service = ProjectMemberService()
authorization = AuthorizationService()


class UpdateMemberRoleBody(UpdateProjectMemberRoleModel):
    id: uuid.UUID | None = None


class AddProjectMemberBody(AddProjectMemberModel):
    project_id: uuid.UUID | None = None


@router.get("")
async def list_members(project_id: str, user: dict = Depends(require_rest_permission("members", "read"))):
    await authorization.authorize_or_raise(user, "members", "read", context={"project_id": project_id})
    return api_response(await service.get_project_members(project_id), "Project members fetched")


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_member(
    project_id: str,
    payload: AddProjectMemberBody,
    user: dict = Depends(require_rest_permission("members", "manage")),
):
    payload.project_id = uuid.UUID(project_id)
    await authorization.authorize_or_raise(user, "members", "manage", context={"project_id": project_id})
    return api_response(await service.add_member(payload), "Project member added", 201)


@router.patch("/{member_id}")
async def update_member_role(
    project_id: str,
    member_id: str,
    payload: UpdateMemberRoleBody,
    user: dict = Depends(require_rest_permission("members", "manage")),
):
    payload.id = uuid.UUID(member_id)
    await authorization.authorize_or_raise(user, "members", "manage", context={"project_id": project_id})
    return api_response(await service.update_member_role(payload), "Project member role updated")


@router.delete("/{member_id}")
async def remove_member(
    project_id: str,
    member_id: str,
    user: dict = Depends(require_rest_permission("members", "manage")),
):
    await authorization.authorize_or_raise(user, "members", "manage", context={"project_id": project_id})
    return api_response(await service.remove_member(member_id), "Project member removed")

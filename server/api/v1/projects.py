import uuid

from fastapi import APIRouter, Depends, status

from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.models.dto.project_dto import CreateProjectModel, UpdateProjectModel
from server.services.authorization_service import AuthorizationService
from server.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])
service = ProjectService()
authorization = AuthorizationService()


class UpdateProjectBody(UpdateProjectModel):
    id: uuid.UUID | None = None


@router.get("")
async def list_projects(
    include_archived: bool = False,
    user: dict = Depends(require_rest_permission("projects", "read")),
):
    return api_response(await service.get_all(include_archived), "Projects fetched")


@router.get("/{project_id}")
async def get_project(project_id: str, user: dict = Depends(require_rest_permission("projects", "read"))):
    resource = await service.get_one(project_id)
    if resource:
        await authorization.authorize_or_raise(user, "projects", "read", resource)
    return api_response(resource, "Project fetched")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: CreateProjectModel, user: dict = Depends(require_rest_permission("projects", "create"))
):
    return api_response(await service.create(payload), "Project created", 201)


@router.patch("/{project_id}")
async def update_project(
    project_id: str,
    payload: UpdateProjectBody,
    user: dict = Depends(require_rest_permission("projects", "update")),
):
    payload.id = uuid.UUID(project_id)
    resource = await service.get_one(project_id)
    if resource:
        await authorization.authorize_or_raise(user, "projects", "update", resource)
    return api_response(await service.update(payload), "Project updated")


@router.post("/{project_id}/archive")
async def archive_project(project_id: str, user: dict = Depends(require_rest_permission("projects", "archive"))):
    resource = await service.get_one(project_id)
    if resource:
        await authorization.authorize_or_raise(user, "projects", "archive", resource)
    return api_response(await service.archive(project_id), "Project archived")


@router.delete("/{project_id}")
async def delete_project(project_id: str, user: dict = Depends(require_rest_permission("projects", "delete"))):
    resource = await service.get_one(project_id)
    if resource:
        await authorization.authorize_or_raise(user, "projects", "delete", resource)
    return api_response(await service.delete(project_id), "Project deleted")

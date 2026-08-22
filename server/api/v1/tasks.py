import uuid

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.models.dto.task_dto import CreateTaskModel, UpdateTaskModel
from server.services.authorization_service import AuthorizationService
from server.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])
service = TaskService()
authorization = AuthorizationService()


class AssignTaskBody(BaseModel):
    assignee_id: str


class UpdateTaskBody(UpdateTaskModel):
    id: uuid.UUID | None = None


@router.get("")
async def list_tasks(project_id: str | None = None, user: dict = Depends(require_rest_permission("tasks", "read"))):
    if project_id:
        await authorization.authorize_or_raise(user, "tasks", "read", context={"project_id": project_id})
    return api_response(await service.get_all(project_id), "Tasks fetched")


@router.get("/{task_id}")
async def get_task(task_id: str, user: dict = Depends(require_rest_permission("tasks", "read"))):
    resource = await service.get_one(task_id)
    if resource:
        await authorization.authorize_or_raise(user, "tasks", "read", resource)
    return api_response(resource, "Task fetched")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(payload: CreateTaskModel, user: dict = Depends(require_rest_permission("tasks", "create"))):
    await authorization.authorize_or_raise(user, "tasks", "create", context={"project_id": str(payload.project_id)})
    return api_response(await service.create(payload), "Task created", 201)


@router.patch("/{task_id}")
async def update_task(
    task_id: str, payload: UpdateTaskBody, user: dict = Depends(require_rest_permission("tasks", "update"))
):
    payload.id = uuid.UUID(task_id)
    resource = await service.get_one(task_id)
    if resource:
        await authorization.authorize_or_raise(user, "tasks", "update", resource)
    return api_response(await service.update(payload), "Task updated")


@router.post("/{task_id}/assign")
async def assign_task(
    task_id: str, payload: AssignTaskBody, user: dict = Depends(require_rest_permission("tasks", "assign"))
):
    resource = await service.get_one(task_id)
    if resource:
        await authorization.authorize_or_raise(user, "tasks", "assign", resource)
    return api_response(await service.assign(task_id, payload.assignee_id), "Task assigned")


@router.post("/{task_id}/complete")
async def complete_task(task_id: str, user: dict = Depends(require_rest_permission("tasks", "complete"))):
    resource = await service.get_one(task_id)
    if resource:
        await authorization.authorize_or_raise(user, "tasks", "complete", resource)
    return api_response(await service.complete(task_id), "Task completed")


@router.delete("/{task_id}")
async def delete_task(task_id: str, user: dict = Depends(require_rest_permission("tasks", "delete"))):
    resource = await service.get_one(task_id)
    if resource:
        await authorization.authorize_or_raise(user, "tasks", "delete", resource)
    return api_response(await service.delete(task_id), "Task deleted")

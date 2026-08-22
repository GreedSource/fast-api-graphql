import uuid

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.models.dto.role_dto import CreateRoleModel, UpdateRoleModel
from server.services.role_service import RoleService

router = APIRouter(prefix="/roles", tags=["Roles"])
service = RoleService()


class PermissionIdsBody(BaseModel):
    permission_ids: list[str]


class UpdateRoleBody(UpdateRoleModel):
    id: uuid.UUID | None = None


@router.get("")
async def list_roles(user: dict = Depends(require_rest_permission("roles", "read"))):
    return api_response(await service.get_roles(), "Roles fetched")


@router.get("/{role_id}")
async def get_role(role_id: str, user: dict = Depends(require_rest_permission("roles", "read"))):
    return api_response(await service.get_role(role_id), "Role fetched")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_role(payload: CreateRoleModel, user: dict = Depends(require_rest_permission("roles", "create"))):
    return api_response(await service.create(payload), "Role created", 201)


@router.patch("/{role_id}")
async def update_role(
    role_id: str,
    payload: UpdateRoleBody,
    user: dict = Depends(require_rest_permission("roles", "update")),
):
    payload.id = uuid.UUID(role_id)
    return api_response(await service.update(payload), "Role updated")


@router.delete("/{role_id}")
async def delete_role(role_id: str, user: dict = Depends(require_rest_permission("roles", "delete"))):
    return api_response(await service.delete_role(role_id), "Role deleted")


@router.post("/{role_id}/permissions")
async def add_permissions(
    role_id: str,
    payload: PermissionIdsBody,
    user: dict = Depends(require_rest_permission("roles", "update")),
):
    return api_response(await service.add_permissions(role_id, payload.permission_ids), "Permissions added")


@router.delete("/{role_id}/permissions")
async def remove_permissions(
    role_id: str,
    payload: PermissionIdsBody,
    user: dict = Depends(require_rest_permission("roles", "update")),
):
    return api_response(await service.remove_permissions(role_id, payload.permission_ids), "Permissions removed")

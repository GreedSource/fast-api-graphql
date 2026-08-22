from fastapi import APIRouter, Depends, status

from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.models.dto.permission_dto import CreatePermissionModel
from server.services.permission_service import PermissionService

router = APIRouter(prefix="/permissions", tags=["Permissions"])
service = PermissionService()


@router.get("")
async def list_permissions(user: dict = Depends(require_rest_permission("permissions", "read"))):
    return api_response(await service.get_all(), "Permissions fetched")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_permission(
    payload: CreatePermissionModel,
    user: dict = Depends(require_rest_permission("permissions", "create")),
):
    return api_response(await service.create(payload), "Permission created", 201)


@router.delete("/{permission_id}")
async def delete_permission(
    permission_id: str,
    user: dict = Depends(require_rest_permission("permissions", "delete")),
):
    return api_response(await service.delete(permission_id), "Permission deleted")

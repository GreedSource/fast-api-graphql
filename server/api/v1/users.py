from fastapi import APIRouter, Depends

from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.models.dto.user_dto import UpdateUserModel
from server.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])
service = UserService()


@router.get("")
async def list_users(user: dict = Depends(require_rest_permission("users", "read"))):
    return api_response(await service.get_users(), "Users fetched")


@router.get("/{user_id}")
async def get_user(user_id: str, user: dict = Depends(require_rest_permission("users", "read"))):
    return api_response(await service.get_user(user_id), "User fetched")


@router.patch("/{user_id}")
async def update_user(
    user_id: str,
    payload: UpdateUserModel,
    user: dict = Depends(require_rest_permission("users", "update")),
):
    return api_response(await service.update_user(user_id, payload.model_dump(exclude_unset=True)), "User updated")


@router.delete("/{user_id}")
async def delete_user(user_id: str, user: dict = Depends(require_rest_permission("users", "delete"))):
    return api_response(await service.delete_user(user_id), "User deleted")

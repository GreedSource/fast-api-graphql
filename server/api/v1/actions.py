from fastapi import APIRouter, Depends, status

from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.models.dto.action_dto import CreateActionModel
from server.services.action_service import ActionService

router = APIRouter(prefix="/actions", tags=["Actions"])
service = ActionService()


@router.get("")
async def list_actions(user: dict = Depends(require_rest_permission("actions", "read"))):
    return api_response(await service.get_all(), "Actions fetched")


@router.get("/{action_id}")
async def get_action(action_id: str, user: dict = Depends(require_rest_permission("actions", "read"))):
    return api_response(await service.get_one(action_id), "Action fetched")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_action(payload: CreateActionModel, user: dict = Depends(require_rest_permission("actions", "create"))):
    return api_response(await service.create(payload), "Action created", 201)

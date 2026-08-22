import uuid

from fastapi import APIRouter, Depends, status

from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.models.dto.module_dto import CreateModuleModel, UpdateModuleModel
from server.services.module_service import ModuleService

router = APIRouter(prefix="/modules", tags=["Modules"])
service = ModuleService()


class UpdateModuleBody(UpdateModuleModel):
    id: uuid.UUID | None = None


@router.get("")
async def list_modules(user: dict = Depends(require_rest_permission("modules", "read"))):
    return api_response(await service.get_all(), "Modules fetched")


@router.get("/{module_id}")
async def get_module(module_id: str, user: dict = Depends(require_rest_permission("modules", "read"))):
    return api_response(await service.get_one(module_id), "Module fetched")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_module(payload: CreateModuleModel, user: dict = Depends(require_rest_permission("modules", "create"))):
    return api_response(await service.create(payload), "Module created", 201)


@router.patch("/{module_id}")
async def update_module(
    module_id: str,
    payload: UpdateModuleBody,
    user: dict = Depends(require_rest_permission("modules", "update")),
):
    payload.id = uuid.UUID(module_id)
    return api_response(await service.update(payload), "Module updated")

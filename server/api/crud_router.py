import uuid

from fastapi import APIRouter, Depends, status
from pydantic import create_model as create_pydantic_model

from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.services.authorization_service import AuthorizationService


def build_scoped_crud_router(module, service, create_dto, update_dto) -> APIRouter:
    router = APIRouter(prefix=f"/{module}", tags=[module.title()])
    authorization = AuthorizationService()
    update_body_model = create_pydantic_model(
        f"Update{module.title()}Body",
        __base__=update_dto,
        id=(uuid.UUID | None, None),
    )

    @router.get("")
    async def list_resources(
        organization_id: str,
        user: dict = Depends(require_rest_permission(module, "read")),
    ):
        access = await authorization.resolve_access(user, organization_id)
        return api_response(await service.get_all(organization_id, access), f"{module} fetched")

    @router.get("/{resource_id}")
    async def get_resource(resource_id: str, user: dict = Depends(require_rest_permission(module, "read"))):
        resource = await service.get_one(resource_id)
        if resource:
            await authorization.authorize_or_raise(user, module, "read", resource)
        return api_response(resource, f"{module} resource fetched")

    @router.post("", status_code=status.HTTP_201_CREATED)
    async def create_resource(payload: create_dto, user: dict = Depends(require_rest_permission(module, "create"))):
        access = await authorization.resolve_access(user, payload.organization_id)
        if payload.owner_id is None:
            payload.owner_id = uuid.UUID(str(user["id"]))
        if payload.team_id is None and access.get("team_id"):
            payload.team_id = uuid.UUID(str(access["team_id"]))
        resource_context = payload.model_dump(by_alias=True, mode="json", exclude_none=True)
        await authorization.authorize_or_raise(user, module, "create", resource_context)
        return api_response(await service.create(payload), f"{module} resource created", 201)

    @router.patch("/{resource_id}")
    async def update_resource(
        resource_id: str,
        payload: update_body_model,
        user: dict = Depends(require_rest_permission(module, "update")),
    ):
        payload.id = uuid.UUID(resource_id)
        resource = await service.get_one(resource_id)
        if resource:
            await authorization.authorize_or_raise(user, module, "update", resource)
        return api_response(await service.update(payload), f"{module} resource updated")

    @router.delete("/{resource_id}")
    async def delete_resource(resource_id: str, user: dict = Depends(require_rest_permission(module, "delete"))):
        resource = await service.get_one(resource_id)
        if resource:
            await authorization.authorize_or_raise(user, module, "delete", resource)
        return api_response(await service.delete(resource_id), f"{module} resource deleted")

    return router

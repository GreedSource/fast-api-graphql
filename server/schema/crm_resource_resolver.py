import uuid

from ariadne import MutationType, QueryType

from server.decorators.require_permission_decorator import require_permission
from server.decorators.require_token_decorator import require_token
from server.models.dto.response_dto import ResponseModel
from server.services.authorization_service import AuthorizationService


def protect_bound(owner, handler, module, action):
    async def adapter(_resolver_self, parent, info, *args, **kwargs):
        return await handler(parent, info, *args, **kwargs)

    wrapped = require_token(require_permission(type=module, action=action)(adapter))
    return wrapped.__get__(owner, type(owner))


class CRMResourceResolver:
    module: str
    singular: str
    create_model = None
    update_model = None
    service = None

    def __init__(self):
        self.query = QueryType()
        self.mutation = MutationType()
        self.authorization = AuthorizationService()
        self.query.set_field(self.module, self._protected("read", self.resolve_all))
        self.query.set_field(self.singular.lower(), self._protected("read", self.resolve_one))
        self.mutation.set_field(f"create{self.singular}", self._protected("create", self.resolve_create))
        self.mutation.set_field(f"update{self.singular}", self._protected("update", self.resolve_update))
        self.mutation.set_field(f"delete{self.singular}", self._protected("delete", self.resolve_delete))

    def _protected(self, action, handler):
        return protect_bound(self, handler, self.module, action)

    async def resolve_all(self, _, info, organizationId):
        access = await self.authorization.resolve_access(info.context["current_user"], organizationId)
        return ResponseModel(
            status=200, message=f"{self.singular} list fetched", data=await self.service.get_all(organizationId, access)
        )

    async def resolve_one(self, _, info, id):
        data = await self.service.get_one(id)
        if data:
            await self.authorization.authorize_or_raise(info.context["current_user"], self.module, "read", data)
        return ResponseModel(status=200, message=f"{self.singular} fetched", data=data)

    async def resolve_create(self, _, info, input):
        payload = self.create_model(**input)
        access = await self.authorization.resolve_access(info.context["current_user"], payload.organization_id)
        if payload.owner_id is None:
            payload.owner_id = uuid.UUID(str(info.context["current_user"]["id"]))
        if payload.team_id is None and access.get("team_id"):
            payload.team_id = uuid.UUID(str(access["team_id"]))
        resource = payload.model_dump(by_alias=True, mode="json", exclude_none=True)
        await self.authorization.authorize_or_raise(info.context["current_user"], self.module, "create", resource)
        return ResponseModel(status=200, message=f"{self.singular} created", data=await self.service.create(payload))

    async def resolve_update(self, _, info, input):
        payload = self.update_model(**input)
        resource = await self.service.get_one(payload.id)
        if resource:
            await self.authorization.authorize_or_raise(info.context["current_user"], self.module, "update", resource)
        return ResponseModel(status=200, message=f"{self.singular} updated", data=await self.service.update(payload))

    async def resolve_delete(self, _, info, id):
        resource = await self.service.get_one(id)
        if resource:
            await self.authorization.authorize_or_raise(info.context["current_user"], self.module, "delete", resource)
        return ResponseModel(status=200, message=f"{self.singular} deleted", data=await self.service.delete(id))

    def get_resolvers(self):
        return [self.query, self.mutation]

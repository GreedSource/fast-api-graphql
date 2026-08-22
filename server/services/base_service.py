from typing import Generic, TypeVar

from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper

CreateT = TypeVar("CreateT")
UpdateT = TypeVar("UpdateT")
ItemT = TypeVar("ItemT")


class BaseService(Generic[CreateT, UpdateT, ItemT]):
    """Casos CRUD compartidos; cada dominio conserva sus reglas y operaciones propias."""

    repository = None
    item_model: type[ItemT]
    resource_not_found = "Resource not found"
    serialize_by_alias = True
    serialize_mode = "json"
    serialize_exclude_none = True

    def serialize(self, resource):
        return self.item_model.model_validate(resource).model_dump(
            by_alias=self.serialize_by_alias,
            mode=self.serialize_mode,
            exclude_none=self.serialize_exclude_none,
        )

    async def create(self, payload: CreateT):
        return self.serialize(await self.repository.create(payload.model_dump(exclude_none=True)))

    async def get_one(self, resource_id):
        resource = await self.repository.find_by_id(resource_id)
        return self.serialize(resource) if resource else None

    async def get_all(self, *args, **filters):
        return [self.serialize(item) for item in await self.repository.find_all(*args, **filters)]

    async def update(self, payload: UpdateT):
        resource = await self.repository.update(payload.id, payload.model_dump(exclude={"id"}, exclude_none=True))
        if not resource:
            self.raise_not_found()
        return self.serialize(resource)

    async def delete(self, resource_id):
        if not await self.repository.delete(resource_id):
            self.raise_not_found()
        return True

    def raise_not_found(self):
        raise CustomGraphQLExceptionHelper(self.resource_not_found, HTTPErrorCode.NOT_FOUND)

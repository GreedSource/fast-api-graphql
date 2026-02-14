from ariadne import MutationType, QueryType

from server.models.action_model import CreateActionModel
from server.models.response_model import ResponseModel
from server.services.action_service import ActionService


class ActionResolver:
    def __init__(self):
        self.query = QueryType()
        self.mutation = MutationType()
        self.__service = ActionService()

        self.query.set_field("actions", self.resolve_actions)
        self.mutation.set_field("createAction", self.resolve_create)

    async def resolve_actions(self, *_):
        data = await self.__service.get_all()
        return ResponseModel(status=200, message="Actions fetched", data=data)

    async def resolve_create(self, _, __, input):
        model = CreateActionModel(**input)
        data = await self.__service.create(model)
        return ResponseModel(status=200, message="Action created", data=data)

    def get_resolvers(self):
        return [self.query, self.mutation]

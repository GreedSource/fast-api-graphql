from ariadne import MutationType, QueryType

from server.models.module_model import CreateModuleModel, UpdateModuleModel
from server.models.response_model import ResponseModel
from server.services.module_service import ModuleService


class ModuleResolver:
    def __init__(self):
        self.query = QueryType()
        self.mutation = MutationType()
        self.__service = ModuleService()

        self.query.set_field("modules", self.resolve_modules)
        self.query.set_field("module", self.resolve_module)
        self.mutation.set_field("createModule", self.resolve_create)
        self.mutation.set_field("updateModule", self.resolve_update)

    async def resolve_modules(self, *_):
        data = await self.__service.get_all()
        return ResponseModel(status=200, message="Modules fetched", data=data)

    async def resolve_module(self, _, __, id):
        data = await self.__service.get_one(id)
        return ResponseModel(status=200, message="Module fetched", data=data)

    async def resolve_create(self, _, __, input):
        model = CreateModuleModel(**input)
        data = await self.__service.create(model)
        return ResponseModel(status=200, message="Module created", data=data)

    async def resolve_update(self, _, __, input):
        model = UpdateModuleModel(**input)
        data = await self.__service.update(model)
        return ResponseModel(status=200, message="Module updated", data=data)

    def get_resolvers(self):
        return [self.query, self.mutation]

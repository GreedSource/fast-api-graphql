from ariadne import MutationType, QueryType

from server.decorators.require_permission_decorator import require_permission
from server.decorators.require_token_decorator import require_token
from server.models.dto.response_dto import ResponseModel
from server.models.dto.task_dto import CreateTaskModel, UpdateTaskModel
from server.services.task_service import TaskService


class TaskResolver:
    def __init__(self):
        self.query = QueryType()
        self.mutation = MutationType()
        self.__service = TaskService()

        self.query.set_field("tasks", self.resolve_tasks)
        self.query.set_field("task", self.resolve_task)
        self.mutation.set_field("createTask", self.resolve_create_task)
        self.mutation.set_field("updateTask", self.resolve_update_task)
        self.mutation.set_field("assignTask", self.resolve_assign_task)
        self.mutation.set_field("completeTask", self.resolve_complete_task)
        self.mutation.set_field("deleteTask", self.resolve_delete_task)

    @require_token
    @require_permission(type="tasks", action="read")
    async def resolve_tasks(self, _, info, projectId=None):
        data = await self.__service.get_all(project_id=projectId)
        return ResponseModel(status=200, message="Tasks fetched", data=data)

    @require_token
    @require_permission(type="tasks", action="read")
    async def resolve_task(self, _, info, id):
        data = await self.__service.get_one(id)
        return ResponseModel(status=200, message="Task fetched", data=data)

    @require_token
    @require_permission(type="tasks", action="create")
    async def resolve_create_task(self, _, info, input):
        model = CreateTaskModel(**input)
        data = await self.__service.create(model)
        return ResponseModel(status=200, message="Task created", data=data)

    @require_token
    @require_permission(type="tasks", action="update")
    async def resolve_update_task(self, _, info, input):
        model = UpdateTaskModel(**input)
        data = await self.__service.update(model)
        return ResponseModel(status=200, message="Task updated", data=data)

    @require_token
    @require_permission(type="tasks", action="assign")
    async def resolve_assign_task(self, _, info, id, assigneeId):
        data = await self.__service.assign(id, assigneeId)
        return ResponseModel(status=200, message="Task assigned", data=data)

    @require_token
    @require_permission(type="tasks", action="complete")
    async def resolve_complete_task(self, _, info, id):
        data = await self.__service.complete(id)
        return ResponseModel(status=200, message="Task completed", data=data)

    @require_token
    @require_permission(type="tasks", action="delete")
    async def resolve_delete_task(self, _, info, id):
        data = await self.__service.delete(id)
        return ResponseModel(status=200, message="Task deleted", data=data)

    def get_resolvers(self):
        return [self.query, self.mutation]

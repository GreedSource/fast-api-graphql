from server.decorators.singleton_decorator import singleton
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.task_dto import CreateTaskModel, TaskItemModel, UpdateTaskModel
from server.repositories.project_repository import ProjectRepository
from server.repositories.task_repository import TaskRepository
from server.services.base_service import BaseService


@singleton
class TaskService(BaseService[CreateTaskModel, UpdateTaskModel, TaskItemModel]):
    repository = TaskRepository()
    project_repository = ProjectRepository()
    item_model = TaskItemModel
    resource_not_found = "Tarea no encontrada"

    async def create(self, payload: CreateTaskModel):
        if not await self.project_repository.find_by_id(payload.project_id):
            raise CustomGraphQLExceptionHelper("Proyecto no encontrado", HTTPErrorCode.NOT_FOUND)
        return await super().create(payload)

    async def get_all(self, project_id: str | None = None):
        return await super().get_all(project_id=project_id)

    async def assign(self, task_id: str, assignee_id: str):
        task = await self.repository.update(task_id, {"assignee_id": assignee_id})
        if not task:
            self.raise_not_found()
        return self.serialize(task)

    async def complete(self, task_id: str):
        task = await self.repository.complete(task_id)
        if not task:
            self.raise_not_found()
        return self.serialize(task)

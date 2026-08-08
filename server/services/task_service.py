from server.decorators.singleton_decorator import singleton
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.task_dto import CreateTaskModel, TaskItemModel, TaskListModel, UpdateTaskModel
from server.repositories.project_repository import ProjectRepository
from server.repositories.task_repository import TaskRepository


@singleton
class TaskService:
    def __init__(self):
        self.__repository = TaskRepository()
        self.__project_repository = ProjectRepository()

    async def create(self, payload: CreateTaskModel):
        project = await self.__project_repository.find_by_id(payload.project_id)
        if not project:
            raise CustomGraphQLExceptionHelper("Proyecto no encontrado")

        task_orm = await self.__repository.create(payload.model_dump(exclude_none=True))
        return TaskItemModel.model_validate(task_orm).model_dump(by_alias=True, mode="json")

    async def get_all(self, project_id: str | None = None):
        task_orms = await self.__repository.find_all(project_id=project_id)
        return TaskListModel.model_validate(task_orms).model_dump(by_alias=True, mode="json")

    async def get_one(self, task_id: str):
        task_orm = await self.__repository.find_by_id(task_id)
        if not task_orm:
            return None
        return TaskItemModel.model_validate(task_orm).model_dump(by_alias=True, mode="json")

    async def update(self, payload: UpdateTaskModel):
        task_orm = await self.__repository.update(
            payload.id,
            payload.model_dump(exclude={"id"}, exclude_none=True),
        )
        if not task_orm:
            raise CustomGraphQLExceptionHelper("Tarea no encontrada")
        return TaskItemModel.model_validate(task_orm).model_dump(by_alias=True, mode="json")

    async def assign(self, task_id: str, assignee_id: str):
        task_orm = await self.__repository.update(task_id, {"assignee_id": assignee_id})
        if not task_orm:
            raise CustomGraphQLExceptionHelper("Tarea no encontrada")
        return TaskItemModel.model_validate(task_orm).model_dump(by_alias=True, mode="json")

    async def complete(self, task_id: str):
        task_orm = await self.__repository.complete(task_id)
        if not task_orm:
            raise CustomGraphQLExceptionHelper("Tarea no encontrada")
        return TaskItemModel.model_validate(task_orm).model_dump(by_alias=True, mode="json")

    async def delete(self, task_id: str):
        return await self.__repository.delete(task_id)

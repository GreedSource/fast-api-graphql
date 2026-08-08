from server.decorators.singleton_decorator import singleton
from server.enums.http_error_code_enum import HTTPErrorCode
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.project_dto import CreateProjectModel, ProjectItemModel, ProjectListModel, UpdateProjectModel
from server.repositories.project_repository import ProjectRepository


@singleton
class ProjectService:
    def __init__(self):
        self.__repository = ProjectRepository()

    async def create(self, payload: CreateProjectModel):
        project_orm = await self.__repository.create(payload.model_dump(exclude_none=True))
        return ProjectItemModel.model_validate(project_orm).model_dump(by_alias=True, mode="json")

    async def get_all(self, include_archived: bool = False):
        project_orms = await self.__repository.find_all(include_archived=include_archived)
        return ProjectListModel.model_validate(project_orms).model_dump(by_alias=True, mode="json")

    async def get_one(self, project_id: str):
        project_orm = await self.__repository.find_by_id(project_id)
        if not project_orm:
            return None
        return ProjectItemModel.model_validate(project_orm).model_dump(by_alias=True, mode="json")

    async def update(self, payload: UpdateProjectModel):
        project_orm = await self.__repository.update(
            payload.id,
            payload.model_dump(exclude={"id"}, exclude_none=True),
        )
        if not project_orm:
            raise CustomGraphQLExceptionHelper("Proyecto no encontrado", HTTPErrorCode.NOT_FOUND)
        return ProjectItemModel.model_validate(project_orm).model_dump(by_alias=True, mode="json")

    async def archive(self, project_id: str):
        project_orm = await self.__repository.archive(project_id)
        if not project_orm:
            raise CustomGraphQLExceptionHelper("Proyecto no encontrado", HTTPErrorCode.NOT_FOUND)
        return ProjectItemModel.model_validate(project_orm).model_dump(by_alias=True, mode="json")

    async def delete(self, project_id: str):
        deleted = await self.__repository.delete(project_id)
        if not deleted:
            raise CustomGraphQLExceptionHelper("Proyecto no encontrado", HTTPErrorCode.NOT_FOUND)
        return deleted

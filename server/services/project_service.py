from server.decorators.singleton_decorator import singleton
from server.models.dto.project_dto import CreateProjectModel, ProjectItemModel, UpdateProjectModel
from server.repositories.project_repository import ProjectRepository
from server.services.base_service import BaseService


@singleton
class ProjectService(BaseService[CreateProjectModel, UpdateProjectModel, ProjectItemModel]):
    repository = ProjectRepository()
    item_model = ProjectItemModel
    resource_not_found = "Proyecto no encontrado"

    async def get_all(self, include_archived: bool = False):
        return await super().get_all(include_archived=include_archived)

    async def archive(self, project_id):
        project = await self.repository.archive(project_id)
        if not project:
            self.raise_not_found()
        return self.serialize(project)

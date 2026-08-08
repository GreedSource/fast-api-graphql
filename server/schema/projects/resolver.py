from ariadne import MutationType, QueryType

from server.decorators.require_permission_decorator import require_permission
from server.decorators.require_token_decorator import require_token
from server.models.dto.project_dto import CreateProjectModel, UpdateProjectModel
from server.models.dto.response_dto import ResponseModel
from server.services.authorization_service import AuthorizationService
from server.services.project_service import ProjectService


class ProjectResolver:
    def __init__(self):
        self.query = QueryType()
        self.mutation = MutationType()
        self.__service = ProjectService()
        self.__authorization = AuthorizationService()

        self.query.set_field("projects", self.resolve_projects)
        self.query.set_field("project", self.resolve_project)
        self.mutation.set_field("createProject", self.resolve_create_project)
        self.mutation.set_field("updateProject", self.resolve_update_project)
        self.mutation.set_field("archiveProject", self.resolve_archive_project)
        self.mutation.set_field("deleteProject", self.resolve_delete_project)

    @require_token
    @require_permission(type="projects", action="read")
    async def resolve_projects(self, _, info, includeArchived=False):
        data = await self.__service.get_all(include_archived=includeArchived)
        return ResponseModel(status=200, message="Projects fetched", data=data)

    @require_token
    @require_permission(type="projects", action="read")
    async def resolve_project(self, _, info, id):
        data = await self.__service.get_one(id)
        if data:
            await self.__authorization.authorize_or_raise(info.context.get("current_user"), "projects", "read", data)
        return ResponseModel(status=200, message="Project fetched", data=data)

    @require_token
    @require_permission(type="projects", action="create")
    async def resolve_create_project(self, _, info, input):
        model = CreateProjectModel(**input)
        data = await self.__service.create(model)
        return ResponseModel(status=200, message="Project created", data=data)

    @require_token
    @require_permission(type="projects", action="update")
    async def resolve_update_project(self, _, info, input):
        model = UpdateProjectModel(**input)
        resource = await self.__service.get_one(str(model.id))
        if resource:
            await self.__authorization.authorize_or_raise(
                info.context.get("current_user"), "projects", "update", resource
            )
        data = await self.__service.update(model)
        return ResponseModel(status=200, message="Project updated", data=data)

    @require_token
    @require_permission(type="projects", action="archive")
    async def resolve_archive_project(self, _, info, id):
        resource = await self.__service.get_one(id)
        if resource:
            await self.__authorization.authorize_or_raise(
                info.context.get("current_user"), "projects", "archive", resource
            )
        data = await self.__service.archive(id)
        return ResponseModel(status=200, message="Project archived", data=data)

    @require_token
    @require_permission(type="projects", action="delete")
    async def resolve_delete_project(self, _, info, id):
        resource = await self.__service.get_one(id)
        if resource:
            await self.__authorization.authorize_or_raise(
                info.context.get("current_user"), "projects", "delete", resource
            )
        data = await self.__service.delete(id)
        return ResponseModel(status=200, message="Project deleted", data=data)

    def get_resolvers(self):
        return [self.query, self.mutation]

from server.decorators.singleton_decorator import singleton
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.models.dto.project_member_dto import (
    AddProjectMemberModel,
    ProjectMemberItemModel,
    ProjectMemberListModel,
    UpdateProjectMemberRoleModel,
)
from server.repositories.project_member_repository import ProjectMemberRepository
from server.repositories.project_repository import ProjectRepository
from server.repositories.user_repository import UserRepository


@singleton
class ProjectMemberService:
    def __init__(self):
        self.__repository = ProjectMemberRepository()
        self.__project_repository = ProjectRepository()
        self.__user_repository = UserRepository()

    async def add_member(self, payload: AddProjectMemberModel):
        project = await self.__project_repository.find_by_id(payload.project_id)
        if not project:
            raise CustomGraphQLExceptionHelper("Proyecto no encontrado")

        user = await self.__user_repository.find_by_id(payload.user_id)
        if not user:
            raise CustomGraphQLExceptionHelper("Usuario no encontrado")

        project_role = await self.__repository.find_project_role_by_id(payload.project_role_id)
        if not project_role:
            raise CustomGraphQLExceptionHelper("Project role not found")

        existing = await self.__repository.find_by_project_and_user(payload.project_id, payload.user_id)
        if existing:
            raise CustomGraphQLExceptionHelper("El usuario ya es miembro del proyecto")

        member = await self.__repository.create(payload.model_dump())
        return ProjectMemberItemModel.model_validate(member).model_dump(by_alias=True, mode="json")

    async def get_project_members(self, project_id: str):
        members = await self.__repository.find_by_project(project_id)
        return ProjectMemberListModel.model_validate(members).model_dump(by_alias=True, mode="json")

    async def update_member_role(self, payload: UpdateProjectMemberRoleModel):
        project_role = await self.__repository.find_project_role_by_id(payload.project_role_id)
        if not project_role:
            raise CustomGraphQLExceptionHelper("Project role not found")

        member = await self.__repository.update_role(payload.id, payload.project_role_id)
        if not member:
            raise CustomGraphQLExceptionHelper("Project member not found")
        return ProjectMemberItemModel.model_validate(member).model_dump(by_alias=True, mode="json")

    async def remove_member(self, member_id: str):
        return await self.__repository.delete(member_id)

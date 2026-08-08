from ariadne import MutationType, QueryType

from server.decorators.require_permission_decorator import require_permission
from server.decorators.require_token_decorator import require_token
from server.models.dto.project_member_dto import AddProjectMemberModel, UpdateProjectMemberRoleModel
from server.models.dto.response_dto import ResponseModel
from server.services.project_member_service import ProjectMemberService


class ProjectMemberResolver:
    def __init__(self):
        self.query = QueryType()
        self.mutation = MutationType()
        self.__service = ProjectMemberService()

        self.query.set_field("projectMembers", self.resolve_project_members)
        self.mutation.set_field("addProjectMember", self.resolve_add_project_member)
        self.mutation.set_field("updateProjectMemberRole", self.resolve_update_project_member_role)
        self.mutation.set_field("removeProjectMember", self.resolve_remove_project_member)

    @require_token
    @require_permission(type="members", action="read")
    async def resolve_project_members(self, _, info, projectId):
        data = await self.__service.get_project_members(projectId)
        return ResponseModel(status=200, message="Project members fetched", data=data)

    @require_token
    @require_permission(type="members", action="manage")
    async def resolve_add_project_member(self, _, info, input):
        model = AddProjectMemberModel(**input)
        data = await self.__service.add_member(model)
        return ResponseModel(status=200, message="Project member added", data=data)

    @require_token
    @require_permission(type="members", action="manage")
    async def resolve_update_project_member_role(self, _, info, input):
        model = UpdateProjectMemberRoleModel(**input)
        data = await self.__service.update_member_role(model)
        return ResponseModel(status=200, message="Project member role updated", data=data)

    @require_token
    @require_permission(type="members", action="manage")
    async def resolve_remove_project_member(self, _, info, id):
        data = await self.__service.remove_member(id)
        return ResponseModel(status=200, message="Project member removed", data=data)

    def get_resolvers(self):
        return [self.query, self.mutation]

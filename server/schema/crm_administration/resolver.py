from ariadne import MutationType, QueryType

from server.models.dto.response_dto import ResponseModel
from server.schema.crm_resource_resolver import protect_bound
from server.services.authorization_service import AuthorizationService
from server.services.crm_organization_service import CRMOrganizationService
from server.services.crm_team_service import CRMTeamService


class CRMAdministrationResolver:
    def __init__(self):
        self.query = QueryType()
        self.mutation = MutationType()
        self.authorization = AuthorizationService()
        self.organizations = CRMOrganizationService()
        self.teams = CRMTeamService()
        self.query.set_field("crmTeams", protect_bound(self, self.resolve_teams, "teams", "read"))
        self.mutation.set_field(
            "createCRMOrganization",
            protect_bound(self, self.resolve_create_organization, "modules", "create"),
        )
        self.mutation.set_field("createCRMTeam", protect_bound(self, self.resolve_create_team, "teams", "create"))
        self.mutation.set_field(
            "addCRMTeamMember",
            protect_bound(self, self.resolve_add_member, "teams", "manage"),
        )

    async def resolve_teams(self, _, info, organizationId):
        await self.authorization.resolve_access(info.context["current_user"], organizationId)
        return ResponseModel(status=200, message="CRM teams fetched", data=await self.teams.get_all(organizationId))

    async def resolve_create_organization(self, _, info, name, slug):
        return ResponseModel(
            status=200, message="CRM organization created", data=await self.organizations.create(name, slug)
        )

    async def resolve_create_team(self, _, info, organizationId, name, description=None):
        return ResponseModel(
            status=200, message="CRM team created", data=await self.teams.create(organizationId, name, description)
        )

    async def resolve_add_member(self, _, info, teamId, userId, role, scope):
        team = await self.teams.get_one(teamId)
        if team:
            await self.authorization.authorize_or_raise(info.context["current_user"], "teams", "manage", team)
        return ResponseModel(
            status=200, message="CRM team member added", data=await self.teams.add_member(teamId, userId, role, scope)
        )

    def get_resolvers(self):
        return [self.query, self.mutation]

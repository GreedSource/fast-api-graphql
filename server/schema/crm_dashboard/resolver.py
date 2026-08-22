from ariadne import QueryType

from server.models.dto.response_dto import ResponseModel
from server.schema.crm_resource_resolver import protect_bound
from server.services.authorization_service import AuthorizationService
from server.services.crm_dashboard_service import CRMDashboardService


class CRMDashboardResolver:
    def __init__(self):
        self.query = QueryType()
        self.authorization = AuthorizationService()
        self.service = CRMDashboardService()
        self.query.set_field("crmDashboard", protect_bound(self, self.resolve_dashboard, "dashboard", "read"))

    async def resolve_dashboard(self, _, info, organizationId):
        access = await self.authorization.resolve_access(info.context["current_user"], organizationId)
        return ResponseModel(
            status=200, message="CRM dashboard fetched", data=await self.service.get(organizationId, access)
        )

    def get_resolvers(self):
        return [self.query]

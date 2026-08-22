from server.decorators.singleton_decorator import singleton
from server.repositories.crm_dashboard_repository import CRMDashboardRepository


@singleton
class CRMDashboardService:
    def __init__(self):
        self.repository = CRMDashboardRepository()

    async def get(self, organization_id, access):
        return await self.repository.summarize(organization_id, access)

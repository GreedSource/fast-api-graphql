from server.decorators.singleton_decorator import singleton
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.repositories.crm_team_repository import CRMTeamRepository


@singleton
class CRMTeamService:
    def __init__(self):
        self.repository = CRMTeamRepository()

    async def create(self, organization_id, name, description=None):
        item = await self.repository.create(
            {"organization_id": organization_id, "name": name.strip(), "description": description}
        )
        return {
            "id": str(item.id),
            "organizationId": str(item.organization_id),
            "name": item.name,
            "description": item.description,
        }

    async def add_member(self, team_id, user_id, role, scope):
        if scope not in {"OWN", "TEAM", "ORGANIZATION", "GLOBAL"}:
            raise CustomGraphQLExceptionHelper("Invalid authorization scope.")
        item = await self.repository.add_member(
            {"team_id": team_id, "user_id": user_id, "role": role.lower(), "scope": scope}
        )
        return {
            "id": str(item.id),
            "teamId": str(item.team_id),
            "userId": str(item.user_id),
            "role": item.role,
            "scope": item.scope,
        }

    async def get_all(self, organization_id):
        return [
            {
                "id": str(item.id),
                "organizationId": str(item.organization_id),
                "name": item.name,
                "description": item.description,
            }
            for item in await self.repository.find_all(organization_id)
        ]

    async def get_one(self, team_id):
        item = await self.repository.find_by_id(team_id)
        if not item:
            return None
        return {"id": str(item.id), "organizationId": str(item.organization_id), "teamId": str(item.id)}

import re

from server.decorators.singleton_decorator import singleton
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper
from server.repositories.crm_organization_repository import CRMOrganizationRepository


@singleton
class CRMOrganizationService:
    def __init__(self):
        self.repository = CRMOrganizationRepository()

    async def create(self, name, slug):
        normalized_slug = slug.strip().lower()
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", normalized_slug):
            raise CustomGraphQLExceptionHelper("Organization slug is invalid.")
        item = await self.repository.create({"name": name.strip(), "slug": normalized_slug})
        return {"id": str(item.id), "name": item.name, "slug": item.slug}

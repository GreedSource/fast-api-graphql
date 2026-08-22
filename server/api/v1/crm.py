from fastapi import APIRouter, Depends
from pydantic import BaseModel

from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.services.authorization_service import AuthorizationService
from server.services.crm_dashboard_service import CRMDashboardService
from server.services.crm_organization_service import CRMOrganizationService
from server.services.crm_team_service import CRMTeamService

router = APIRouter(prefix="/crm", tags=["CRM Administration"])
authorization = AuthorizationService()
dashboard_service = CRMDashboardService()
organization_service = CRMOrganizationService()
team_service = CRMTeamService()


class CreateOrganizationBody(BaseModel):
    name: str
    slug: str


class CreateTeamBody(BaseModel):
    name: str
    description: str | None = None


class AddTeamMemberBody(BaseModel):
    user_id: str
    role: str
    scope: str


@router.get("/dashboard")
async def dashboard(
    organization_id: str,
    user: dict = Depends(require_rest_permission("dashboard", "read")),
):
    access = await authorization.resolve_access(user, organization_id)
    return api_response(await dashboard_service.get(organization_id, access), "CRM dashboard fetched")


@router.post("/organizations", status_code=201)
async def create_organization(
    payload: CreateOrganizationBody,
    user: dict = Depends(require_rest_permission("modules", "create")),
):
    return api_response(await organization_service.create(payload.name, payload.slug), "CRM organization created", 201)


@router.get("/organizations/{organization_id}/teams")
async def list_teams(
    organization_id: str,
    user: dict = Depends(require_rest_permission("teams", "read")),
):
    await authorization.resolve_access(user, organization_id)
    return api_response(await team_service.get_all(organization_id), "CRM teams fetched")


@router.post("/organizations/{organization_id}/teams", status_code=201)
async def create_team(
    organization_id: str,
    payload: CreateTeamBody,
    user: dict = Depends(require_rest_permission("teams", "create")),
):
    return api_response(
        await team_service.create(organization_id, payload.name, payload.description), "CRM team created", 201
    )


@router.post("/teams/{team_id}/members", status_code=201)
async def add_team_member(
    team_id: str,
    payload: AddTeamMemberBody,
    user: dict = Depends(require_rest_permission("teams", "manage")),
):
    team = await team_service.get_one(team_id)
    if team:
        await authorization.authorize_or_raise(user, "teams", "manage", team)
    return api_response(
        await team_service.add_member(team_id, payload.user_id, payload.role, payload.scope),
        "CRM team member added",
        201,
    )

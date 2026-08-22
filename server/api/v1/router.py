from fastapi import APIRouter

from server.api.v1 import (
    actions,
    activities,
    audit_logs,
    auth,
    companies,
    contacts,
    crm,
    leads,
    modules,
    opportunities,
    permissions,
    project_members,
    projects,
    roles,
    tasks,
    users,
)

api_v1_router = APIRouter(prefix="/api/v1")
for router in (
    auth.router,
    users.router,
    roles.router,
    modules.router,
    actions.router,
    permissions.router,
    projects.router,
    project_members.router,
    tasks.router,
    companies.router,
    contacts.router,
    leads.router,
    opportunities.router,
    activities.router,
    crm.router,
    audit_logs.router,
):
    api_v1_router.include_router(router)

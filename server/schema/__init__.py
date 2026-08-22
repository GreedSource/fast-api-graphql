from pathlib import Path

from ariadne import load_schema_from_path, make_executable_schema

from server.schema.actions.action_resolver import ActionResolver
from server.schema.activities.resolver import ActivityResolver
from server.schema.audit_logs.resolver import AuditLogResolver
from server.schema.companies.resolver import CompanyResolver
from server.schema.contacts.resolver import ContactResolver
from server.schema.crm_administration.resolver import CRMAdministrationResolver
from server.schema.crm_dashboard.resolver import CRMDashboardResolver
from server.schema.leads.resolver import LeadResolver
from server.schema.modules.resolver import ModuleResolver
from server.schema.opportunities.resolver import OpportunityResolver
from server.schema.permission.resolver import PermissionResolver
from server.schema.project_members.resolver import ProjectMemberResolver
from server.schema.projects.resolver import ProjectResolver
from server.schema.tasks.resolver import TaskResolver

from .auth.resolver import AuthResolver
from .hello.resolver import HelloResolver
from .roles.resolver import RoleResolver
from .users.resolver import UserResolver

__user_resolver = UserResolver()
__hello_resolver = HelloResolver()
__auth_resolver = AuthResolver()
__role_resolver = RoleResolver()
__module_resolver = ModuleResolver()
__action_resolver = ActionResolver()
__audit_log_resolver = AuditLogResolver()
__permission_resolver = PermissionResolver()
__project_member_resolver = ProjectMemberResolver()
__project_resolver = ProjectResolver()
__task_resolver = TaskResolver()
__crm_resolvers = [
    CompanyResolver(),
    ContactResolver(),
    LeadResolver(),
    OpportunityResolver(),
    ActivityResolver(),
    CRMAdministrationResolver(),
    CRMDashboardResolver(),
]
schemas_path = Path(__file__).parent

# Cargar todos los archivos .graphql
# Carga TODOS los .graphql del folder schema/
type_defs = load_schema_from_path(schemas_path)  # o la carpeta que tengas

# Unir todos los resolvers
all_resolvers = []
all_resolvers.extend(__hello_resolver.get_resolvers())
all_resolvers.extend(__user_resolver.get_resolvers())
all_resolvers.extend(__auth_resolver.get_resolvers())
all_resolvers.extend(__role_resolver.get_resolvers())
all_resolvers.extend(__module_resolver.get_resolvers())
all_resolvers.extend(__action_resolver.get_resolvers())
all_resolvers.extend(__audit_log_resolver.get_resolvers())
all_resolvers.extend(__permission_resolver.get_resolvers())
all_resolvers.extend(__project_member_resolver.get_resolvers())
all_resolvers.extend(__project_resolver.get_resolvers())
all_resolvers.extend(__task_resolver.get_resolvers())
for crm_resolver in __crm_resolvers:
    all_resolvers.extend(crm_resolver.get_resolvers())

schema = make_executable_schema(type_defs, *all_resolvers)

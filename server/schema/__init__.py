from pathlib import Path

from ariadne import load_schema_from_path, make_executable_schema

from server.schema.actions.action_resolver import ActionResolver
from server.schema.modules.resolver import ModuleResolver
from server.schema.permission.resolver import PermissionResolver

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
__permission_resolver = PermissionResolver()
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
all_resolvers.extend(__permission_resolver.get_resolvers())

schema = make_executable_schema(type_defs, *all_resolvers)

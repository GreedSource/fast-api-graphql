from itertools import product

DEFAULT_MODULES = [
    {"name": "Usuarios", "key": "users", "description": "Gestión de usuarios", "active": True},
    {"name": "Roles", "key": "roles", "description": "Gestión de roles", "active": True},
    {"name": "Permisos", "key": "permissions", "description": "Gestión de permisos", "active": True},
    {"name": "Módulos", "key": "modules", "description": "Activar módulos", "active": True},
    {"name": "Acciones", "key": "actions", "description": "Gestión de acciones", "active": True},
    {"name": "Dashboard", "key": "dashboard", "description": "Resumen operativo del sistema", "active": True},
    {"name": "Proyectos", "key": "projects", "description": "Gestión de proyectos", "active": True},
    {"name": "Tareas", "key": "tasks", "description": "Gestión de tareas", "active": True},
    {"name": "Equipos", "key": "teams", "description": "Gestión de equipos", "active": True},
    {"name": "Miembros", "key": "members", "description": "Gestión de miembros", "active": True},
    {"name": "Hitos", "key": "milestones", "description": "Gestión de hitos", "active": True},
    {"name": "Reportes", "key": "reports", "description": "Consulta y exportación de reportes", "active": True},
    {"name": "Documentos", "key": "documents", "description": "Gestión de documentos", "active": True},
    {"name": "Actividad", "key": "activity", "description": "Consulta de actividad y auditoría", "active": True},
    {"name": "Empresas CRM", "key": "companies", "description": "Gestión de empresas del CRM", "active": True},
    {"name": "Contactos CRM", "key": "contacts", "description": "Gestión de contactos del CRM", "active": True},
    {"name": "Leads CRM", "key": "leads", "description": "Gestión de leads del CRM", "active": True},
    {"name": "Oportunidades CRM", "key": "opportunities", "description": "Pipeline comercial", "active": True},
    {"name": "Actividades CRM", "key": "activities", "description": "Interacciones comerciales", "active": True},
]

DEFAULT_ACTIONS = [
    {"name": "Crear", "key": "create", "description": "Permite crear entidades", "active": True},
    {"name": "Leer", "key": "read", "description": "Permite leer entidades", "active": True},
    {"name": "Actualizar", "key": "update", "description": "Permite actualizar entidades", "active": True},
    {"name": "Eliminar", "key": "delete", "description": "Permite eliminar entidades", "active": True},
    {"name": "Archivar", "key": "archive", "description": "Permite archivar entidades", "active": True},
    {"name": "Asignar", "key": "assign", "description": "Permite asignar recursos", "active": True},
    {"name": "Completar", "key": "complete", "description": "Permite completar elementos de trabajo", "active": True},
    {"name": "Exportar", "key": "export", "description": "Permite exportar información", "active": True},
    {
        "name": "Administrar",
        "key": "manage",
        "description": "Permite administrar relaciones o recursos",
        "active": True,
    },
    {"name": "Restaurar", "key": "restore", "description": "Permite restaurar entidades archivadas", "active": True},
    {"name": "Convertir", "key": "convert", "description": "Permite convertir leads", "active": True},
    {"name": "Cerrar", "key": "close", "description": "Permite cerrar oportunidades", "active": True},
]

DEFAULT_ROLES = [
    {"name": "admin", "description": "Administrador del sistema", "active": True},
    {"name": "user", "description": "Usuario estándar", "active": True},
    {"name": "super_admin", "description": "Acceso completo al sistema y al MVP de proyectos", "active": True},
    {"name": "project_manager", "description": "Administra proyectos, tareas, equipos y reportes", "active": True},
    {"name": "developer", "description": "Colabora en proyectos y tareas asignadas", "active": True},
    {"name": "client", "description": "Consulta proyectos, tareas y reportes autorizados", "active": True},
    {"name": "viewer", "description": "Consulta información sin modificarla", "active": True},
    {"name": "sales_director", "description": "Administra la operación comercial de la organización", "active": True},
    {"name": "sales_manager", "description": "Administra los recursos comerciales de su equipo", "active": True},
    {"name": "sales_representative", "description": "Administra sus recursos comerciales", "active": True},
    {"name": "sales_assistant", "description": "Apoya la captura de información comercial", "active": True},
]

CRM_READ_KEYS = {
    f"{module}.read" for module in ("companies", "contacts", "leads", "opportunities", "activities", "teams", "reports")
}
CRM_WRITE_KEYS = {
    f"{module}.{action}"
    for module in ("companies", "contacts", "leads", "opportunities", "activities")
    for action in ("read", "create", "update")
}
CRM_DIRECTOR_KEYS = CRM_WRITE_KEYS | {
    "dashboard.read",
    "companies.assign",
    "companies.archive",
    "contacts.assign",
    "leads.assign",
    "leads.convert",
    "opportunities.assign",
    "opportunities.close",
    "activities.assign",
    "teams.read",
    "teams.update",
    "teams.manage",
    "reports.read",
    "reports.export",
}
CRM_MANAGER_KEYS = CRM_WRITE_KEYS | {
    "dashboard.read",
    "leads.assign",
    "opportunities.assign",
    "opportunities.close",
    "activities.assign",
    "teams.read",
    "teams.manage",
    "reports.read",
    "reports.export",
}

PROJECT_MANAGER_PERMISSION_KEYS = {
    "projects.read",
    "projects.create",
    "projects.update",
    "projects.archive",
    "tasks.read",
    "tasks.create",
    "tasks.update",
    "tasks.delete",
    "tasks.assign",
    "tasks.complete",
    "teams.read",
    "teams.update",
    "teams.manage",
    "members.manage",
    "reports.read",
    "reports.export",
}

DEVELOPER_PERMISSION_KEYS = {
    "projects.read",
    "tasks.read",
    "tasks.create",
    "tasks.update",
    "tasks.complete",
    "teams.read",
}

CLIENT_PERMISSION_KEYS = {
    "projects.read",
    "tasks.read",
    "reports.read",
}

VIEWER_PERMISSION_KEYS = CLIENT_PERMISSION_KEYS


def module_keys() -> list[str]:
    return [module["key"] for module in DEFAULT_MODULES]


def action_keys() -> list[str]:
    return [action["key"] for action in DEFAULT_ACTIONS]


def permission_keys() -> list[str]:
    return [f"{module_key}.{action_key}" for module_key, action_key in product(module_keys(), action_keys())]


def role_permission_keys(role_name: str) -> set[str]:
    if role_name in {"admin", "super_admin"}:
        return set(permission_keys())
    if role_name == "project_manager":
        return PROJECT_MANAGER_PERMISSION_KEYS
    if role_name == "developer":
        return DEVELOPER_PERMISSION_KEYS
    if role_name == "client":
        return CLIENT_PERMISSION_KEYS
    if role_name == "viewer":
        return VIEWER_PERMISSION_KEYS | CRM_READ_KEYS
    if role_name == "sales_director":
        return CRM_DIRECTOR_KEYS
    if role_name == "sales_manager":
        return CRM_MANAGER_KEYS
    if role_name == "sales_representative":
        return CRM_WRITE_KEYS | {"dashboard.read", "leads.convert"}
    if role_name == "sales_assistant":
        return CRM_READ_KEYS | {
            "dashboard.read",
            "contacts.create",
            "contacts.update",
            "activities.create",
            "activities.update",
        }
    if role_name == "user":
        return {"dashboard.read"}
    return set()

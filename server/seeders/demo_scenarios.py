DEMO_USERS = [
    {
        "name": "Joel",
        "lastname": "Manager",
        "email": "joel.manager@example.com",
        "password": "Manager123!",
        "role_name": "project_manager",
    },
    {
        "name": "Maria",
        "lastname": "Developer",
        "email": "maria.developer@example.com",
        "password": "Developer123!",
        "role_name": "developer",
    },
    {
        "name": "Carlos",
        "lastname": "Client",
        "email": "carlos.client@example.com",
        "password": "Client123!",
        "role_name": "client",
    },
    {
        "name": "Valeria",
        "lastname": "Viewer",
        "email": "valeria.viewer@example.com",
        "password": "Viewer123!",
        "role_name": "viewer",
    },
]

DEMO_PROJECTS = [
    {
        "name": "Project A",
        "description": "Joel acts as project manager and Maria as developer.",
        "owner_email": "joel.manager@example.com",
    },
    {
        "name": "Project B",
        "description": "Joel acts as developer to demonstrate contextual roles.",
        "owner_email": "joel.manager@example.com",
    },
    {
        "name": "Project C",
        "description": "Joel acts as viewer to demonstrate restricted capabilities.",
        "owner_email": "joel.manager@example.com",
    },
]

DEMO_MEMBERSHIPS = [
    {"project_name": "Project A", "user_email": "joel.manager@example.com", "project_role_name": "project_manager"},
    {"project_name": "Project A", "user_email": "maria.developer@example.com", "project_role_name": "developer"},
    {"project_name": "Project A", "user_email": "carlos.client@example.com", "project_role_name": "client"},
    {"project_name": "Project B", "user_email": "joel.manager@example.com", "project_role_name": "developer"},
    {"project_name": "Project C", "user_email": "joel.manager@example.com", "project_role_name": "viewer"},
]

DEMO_TASKS = [
    {
        "project_name": "Project A",
        "title": "Build authorization dashboard",
        "description": "Project manager can assign and update this task.",
        "assignee_email": "maria.developer@example.com",
        "created_by_email": "joel.manager@example.com",
        "priority": "high",
    },
    {
        "project_name": "Project B",
        "title": "Implement task filters",
        "description": "Joel can edit this task as assigned developer in Project B.",
        "assignee_email": "joel.manager@example.com",
        "created_by_email": "joel.manager@example.com",
        "priority": "medium",
    },
    {
        "project_name": "Project C",
        "title": "Review readonly project",
        "description": "Joel can view but not modify this task in Project C.",
        "assignee_email": None,
        "created_by_email": "joel.manager@example.com",
        "priority": "low",
    },
]

from types import SimpleNamespace
from uuid import UUID

ACTION_ID = UUID("55555555-5555-5555-5555-555555555555")
MODULE_ID = UUID("66666666-6666-6666-6666-666666666666")
PERMISSION_ID = UUID("77777777-7777-7777-7777-777777777777")
ROLE_ID = UUID("88888888-8888-8888-8888-888888888888")


def make_action(**overrides):
    data = {
        "id": ACTION_ID,
        "name": "Read",
        "key": "read",
        "description": "Read records",
        "active": True,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_module(**overrides):
    data = {
        "id": MODULE_ID,
        "name": "Users",
        "key": "users",
        "description": "User management",
        "active": True,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_permission(**overrides):
    data = {
        "id": PERMISSION_ID,
        "module_id": MODULE_ID,
        "action_id": ACTION_ID,
        "module": make_module(),
        "action": make_action(),
        "description": "Users read permission",
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_role(**overrides):
    data = {
        "id": ROLE_ID,
        "name": "Admin",
        "description": "System administrator",
        "active": True,
        "permissions": [make_permission()],
    }
    data.update(overrides)
    return SimpleNamespace(**data)

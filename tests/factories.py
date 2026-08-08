from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

ACTION_ID = UUID("55555555-5555-5555-5555-555555555555")
MODULE_ID = UUID("66666666-6666-6666-6666-666666666666")
PERMISSION_ID = UUID("77777777-7777-7777-7777-777777777777")
ROLE_ID = UUID("88888888-8888-8888-8888-888888888888")
PROJECT_ID = UUID("99999999-9999-9999-9999-999999999999")
TASK_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
PROJECT_ROLE_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
PROJECT_MEMBER_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")


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


def make_current_user(permissions=None, **overrides):
    data = {
        "id": "user-1",
        "name": "Test",
        "lastname": "User",
        "email": "test@example.com",
        "role": {
            "name": "admin",
            "permissions": permissions or [{"type": "users", "action": "read"}],
        },
    }
    data.update(overrides)
    return data


def make_project(**overrides):
    now = datetime.now(timezone.utc)
    data = {
        "id": PROJECT_ID,
        "name": "Apollo",
        "description": "Project Apollo",
        "status": "active",
        "owner_id": USER_ID,
        "archived_at": None,
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_task(**overrides):
    now = datetime.now(timezone.utc)
    data = {
        "id": TASK_ID,
        "project_id": PROJECT_ID,
        "title": "Build API",
        "description": "Implement GraphQL API",
        "status": "todo",
        "priority": "medium",
        "assignee_id": USER_ID,
        "created_by_id": USER_ID,
        "due_date": None,
        "completed_at": None,
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_project_role(**overrides):
    data = {
        "id": PROJECT_ROLE_ID,
        "name": "developer",
        "description": "Project developer",
        "active": True,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_project_member(**overrides):
    now = datetime.now(timezone.utc)
    data = {
        "id": PROJECT_MEMBER_ID,
        "project_id": PROJECT_ID,
        "user_id": USER_ID,
        "project_role_id": PROJECT_ROLE_ID,
        "project_role": make_project_role(),
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return SimpleNamespace(**data)

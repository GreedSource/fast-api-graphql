from server.seeders.rbac_catalog import (
    CLIENT_PERMISSION_KEYS,
    CRM_READ_KEYS,
    DEFAULT_ACTIONS,
    DEFAULT_MODULES,
    DEFAULT_ROLES,
    DEVELOPER_PERMISSION_KEYS,
    PROJECT_MANAGER_PERMISSION_KEYS,
    action_keys,
    module_keys,
    permission_keys,
    role_permission_keys,
)


def test_default_modules_include_project_management_catalog_without_duplicates():
    keys = module_keys()

    assert {
        "dashboard",
        "projects",
        "tasks",
        "teams",
        "members",
        "milestones",
        "reports",
        "documents",
        "activity",
    }.issubset(keys)
    assert len(keys) == len(set(keys))
    assert len(DEFAULT_MODULES) == len(keys)


def test_default_actions_include_mvp_actions_without_duplicates():
    keys = action_keys()

    assert {
        "create",
        "read",
        "update",
        "delete",
        "archive",
        "assign",
        "complete",
        "export",
        "manage",
        "restore",
    }.issubset(keys)
    assert len(keys) == len(set(keys))
    assert len(DEFAULT_ACTIONS) == len(keys)


def test_permission_keys_build_full_module_action_matrix():
    keys = permission_keys()

    assert len(keys) == len(module_keys()) * len(action_keys())
    assert len(keys) == len(set(keys))
    assert "projects.archive" in keys
    assert "tasks.assign" in keys
    assert "reports.export" in keys


def test_default_roles_include_mvp_roles_without_duplicates():
    role_names = [role["name"] for role in DEFAULT_ROLES]

    assert {"super_admin", "project_manager", "developer", "client", "viewer"}.issubset(role_names)
    assert {"sales_director", "sales_manager", "sales_representative", "sales_assistant"}.issubset(role_names)
    assert len(role_names) == len(set(role_names))


def test_role_permission_keys_are_defined_subsets_of_catalog_permissions():
    catalog_permissions = set(permission_keys())

    for role in DEFAULT_ROLES:
        assert role_permission_keys(role["name"]).issubset(catalog_permissions)


def test_project_manager_permissions_match_stage_2_contract():
    assert role_permission_keys("project_manager") == PROJECT_MANAGER_PERMISSION_KEYS
    assert {
        "projects.create",
        "projects.archive",
        "tasks.assign",
        "tasks.complete",
        "teams.manage",
        "members.manage",
        "reports.export",
    }.issubset(PROJECT_MANAGER_PERMISSION_KEYS)


def test_developer_permissions_match_stage_2_contract():
    assert role_permission_keys("developer") == DEVELOPER_PERMISSION_KEYS
    assert "tasks.complete" in DEVELOPER_PERMISSION_KEYS
    assert "projects.delete" not in DEVELOPER_PERMISSION_KEYS
    assert "reports.export" not in DEVELOPER_PERMISSION_KEYS


def test_client_and_viewer_permissions_are_read_only():
    assert role_permission_keys("client") == CLIENT_PERMISSION_KEYS
    assert role_permission_keys("viewer") == CLIENT_PERMISSION_KEYS | CRM_READ_KEYS
    assert role_permission_keys("client") == {"projects.read", "tasks.read", "reports.read"}


def test_super_admin_and_legacy_admin_receive_full_catalog():
    assert role_permission_keys("super_admin") == set(permission_keys())
    assert role_permission_keys("admin") == set(permission_keys())

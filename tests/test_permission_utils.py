from server.utils.permission_utils import (
    has_permission,
    normalize_permission,
    permission_set,
    permission_to_key,
    permissions_to_keys,
)


def test_normalize_permission_accepts_current_dict_contract():
    assert normalize_permission({"type": " Users ", "action": " Read "}) == {
        "type": "users",
        "action": "read",
    }


def test_normalize_permission_accepts_module_action_key():
    assert normalize_permission("Projects.Archive") == {
        "type": "projects",
        "action": "archive",
    }


def test_permission_to_key_keeps_frontend_friendly_shape():
    assert permission_to_key({"type": "tasks", "action": "assign"}) == "tasks.assign"


def test_permissions_to_keys_ignores_invalid_permissions():
    assert permissions_to_keys(
        [
            {"type": "users", "action": "read"},
            "tasks.update",
            {"type": "missing-action"},
            "invalid",
        ]
    ) == ["users.read", "tasks.update"]


def test_permission_set_normalizes_mixed_permission_inputs():
    assert permission_set([{"type": "Users", "action": "READ"}, "tasks.Update"]) == {
        ("users", "read"),
        ("tasks", "update"),
    }


def test_has_permission_matches_case_and_whitespace_insensitively():
    assert has_permission([{"type": " Users ", "action": " Read "}], "users", "read") is True
    assert has_permission(["tasks.update"], "tasks", "delete") is False

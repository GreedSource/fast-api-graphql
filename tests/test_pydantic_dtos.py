from uuid import UUID

from server.models.dto.action_dto import CreateActionModel
from server.models.dto.module_dto import CreateModuleModel, UpdateModuleModel

MODULE_ID = UUID("44444444-4444-4444-4444-444444444444")


def test_create_module_strips_strings_and_normalizes_key():
    payload = CreateModuleModel(name=" Users ", key=" USERS ", description=" User management ")

    assert payload.name == "Users"
    assert payload.key == "users"
    assert payload.description == "User management"


def test_update_module_strips_strings_and_normalizes_key():
    payload = UpdateModuleModel(id=MODULE_ID, name=" Roles ", key=" ROLES ", description=" Role management ")

    assert payload.name == "Roles"
    assert payload.key == "roles"
    assert payload.description == "Role management"


def test_create_action_strips_strings_and_normalizes_key():
    payload = CreateActionModel(name=" Read ", key=" READ ", description=" Read records ")

    assert payload.name == "Read"
    assert payload.key == "read"
    assert payload.description == "Read records"

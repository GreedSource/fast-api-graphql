from types import SimpleNamespace

import pytest

from server.decorators.require_permission_decorator import PermissionCheckMode, require_permission, require_permissions
from server.helpers.custom_graphql_exception_helper import CustomGraphQLExceptionHelper


class ResolverTarget:
    @require_permission(type="users", action="read")
    async def read_users(self, parent, info):
        return {"ok": True}

    @require_permissions(
        permissions=[
            {"type": "users", "action": "read"},
            {"type": "roles", "action": "update"},
        ],
        mode=PermissionCheckMode.ALL,
    )
    async def manage_users_and_roles(self, parent, info):
        return {"ok": True}


def make_info(current_user=None):
    return SimpleNamespace(context={"current_user": current_user})


@pytest.mark.asyncio
async def test_require_permission_allows_user_with_matching_permission():
    current_user = {"role": {"permissions": [{"type": "users", "action": "read"}]}}

    result = await ResolverTarget().read_users(None, make_info(current_user))

    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_require_permission_rejects_unauthenticated_user():
    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await ResolverTarget().read_users(None, make_info())

    assert exc_info.value.status_code == 401
    assert exc_info.value.code == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_require_permissions_all_mode_requires_every_permission():
    current_user = {"role": {"permissions": [{"type": "users", "action": "read"}]}}

    with pytest.raises(CustomGraphQLExceptionHelper) as exc_info:
        await ResolverTarget().manage_users_and_roles(None, make_info(current_user))

    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "FORBIDDEN"

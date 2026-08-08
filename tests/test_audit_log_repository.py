import pytest

from server.repositories.audit_log_repository import AuditLogRepository


class FakeSession:
    def __init__(self):
        self.added = None
        self.committed = False
        self.refreshed = None

    def add(self, item):
        self.added = item

    async def commit(self):
        self.committed = True

    async def refresh(self, item):
        self.refreshed = item


@pytest.mark.asyncio
async def test_audit_log_repository_create_uses_provided_session():
    session = FakeSession()

    result = await AuditLogRepository().create(
        {
            "module": "tasks",
            "action": "update",
            "status": "success",
            "metadata_json": {"reason": "ok"},
        },
        session=session,
    )

    assert result.module == "tasks"
    assert session.added is result
    assert session.committed is True
    assert session.refreshed is result

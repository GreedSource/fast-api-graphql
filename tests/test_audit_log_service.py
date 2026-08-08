from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from server.models.dto.audit_log_dto import CreateAuditLogModel
from server.services.audit_log_service import AuditLogService

AUDIT_ID = UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def make_audit_log(**overrides):
    data = {
        "id": AUDIT_ID,
        "user_id": USER_ID,
        "module": "tasks",
        "action": "update",
        "resource_type": "task",
        "resource_id": "task-1",
        "status": "success",
        "metadata_json": {"reason": "allowed_by_task_policy"},
        "created_at": datetime.now(timezone.utc),
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_create_audit_log_model_strips_and_serializes_metadata_alias():
    payload = CreateAuditLogModel(
        userId=str(USER_ID),
        module=" tasks ",
        action=" update ",
        resourceType=" task ",
        resourceId=" task-1 ",
        status=" success ",
        metadata={"reason": "ok"},
    )

    assert payload.module == "tasks"
    assert payload.action == "update"
    assert payload.metadata_json == {"reason": "ok"}


@pytest.mark.asyncio
async def test_audit_log_service_records_successful_action():
    repository = SimpleNamespace(create=AsyncMock(return_value=make_audit_log()))
    service = AuditLogService()
    service._AuditLogService__repository = repository

    result = await service.record(
        user_id=str(USER_ID),
        module="tasks",
        action="update",
        status="success",
        resource_type="task",
        resource_id="task-1",
        metadata={"reason": "allowed_by_task_policy"},
    )

    assert result["id"] == str(AUDIT_ID)
    assert result["metadata"] == {"reason": "allowed_by_task_policy"}
    repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_audit_log_service_records_denied_action():
    repository = SimpleNamespace(create=AsyncMock(return_value=make_audit_log(status="denied")))
    service = AuditLogService()
    service._AuditLogService__repository = repository

    result = await service.record(
        user_id=str(USER_ID),
        module="projects",
        action="delete",
        status="denied",
        metadata={"reason": "missing_project_membership"},
    )

    assert result["status"] == "denied"


@pytest.mark.asyncio
async def test_audit_log_service_non_strict_failure_does_not_raise():
    repository = SimpleNamespace(create=AsyncMock(side_effect=RuntimeError("db down")))
    service = AuditLogService()
    service._AuditLogService__repository = repository

    assert await service.record(None, "tasks", "read", "denied", strict=False) is None


@pytest.mark.asyncio
async def test_audit_log_service_strict_failure_raises():
    repository = SimpleNamespace(create=AsyncMock(side_effect=RuntimeError("db down")))
    service = AuditLogService()
    service._AuditLogService__repository = repository

    with pytest.raises(RuntimeError):
        await service.record(None, "tasks", "read", "denied", strict=True)


@pytest.mark.asyncio
async def test_audit_log_service_lists_logs():
    repository = SimpleNamespace(find_all=AsyncMock(return_value=[make_audit_log()]))
    service = AuditLogService()
    service._AuditLogService__repository = repository

    result = await service.list_logs(limit=10)

    assert result[0]["module"] == "tasks"
    repository.find_all.assert_awaited_once_with(limit=10)

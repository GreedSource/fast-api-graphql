from typing import Any

from server.decorators.singleton_decorator import singleton
from server.helpers.logger_helper import LoggerHelper
from server.models.dto.audit_log_dto import AuditLogItemModel, AuditLogListModel
from server.repositories.audit_log_repository import AuditLogRepository


@singleton
class AuditLogService:
    def __init__(self):
        self.__repository = AuditLogRepository()

    async def record(
        self,
        user_id: str | None,
        module: str,
        action: str,
        status: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        strict: bool = False,
    ):
        payload = {
            "user_id": user_id,
            "module": module,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "status": status,
            "metadata_json": metadata or {},
        }
        try:
            audit_log = await self.__repository.create(payload)
            return AuditLogItemModel.model_validate(audit_log).model_dump(by_alias=True, mode="json")
        except Exception as exc:
            LoggerHelper.warning(f"No se pudo registrar audit log {module}:{action}:{status}: {exc}")
            if strict:
                raise
            return None

    async def list_logs(self, limit: int = 100):
        logs = await self.__repository.find_all(limit=limit)
        return AuditLogListModel.model_validate(logs).model_dump(by_alias=True, mode="json")

from fastapi import APIRouter, Depends, Query

from server.api.dependencies import require_rest_permission
from server.api.responses import api_response
from server.services.audit_log_service import AuditLogService

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])
service = AuditLogService()


@router.get("")
async def list_audit_logs(
    limit: int = Query(default=100, ge=1, le=500),
    user: dict = Depends(require_rest_permission("activity", "read")),
):
    return api_response(await service.list_logs(limit), "Audit logs fetched")

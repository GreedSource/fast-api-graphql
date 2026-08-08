from ariadne import QueryType, ScalarType

from server.decorators.require_permission_decorator import require_permission
from server.decorators.require_token_decorator import require_token
from server.models.dto.response_dto import ResponseModel
from server.services.audit_log_service import AuditLogService

json_scalar = ScalarType("JSON")


@json_scalar.serializer
def serialize_json(value):
    return value


class AuditLogResolver:
    def __init__(self):
        self.query = QueryType()
        self.__service = AuditLogService()

        self.query.set_field("auditLogs", self.resolve_audit_logs)

    @require_token
    @require_permission(type="activity", action="read")
    async def resolve_audit_logs(self, _, info, limit=100):
        data = await self.__service.list_logs(limit=limit)
        return ResponseModel(status=200, message="Audit logs fetched", data=data)

    def get_resolvers(self):
        return [self.query, json_scalar]

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

version = "010_create_audit_logs_postgresql_20260807215000"
description = "Create audit logs table"


async def upgrade(conn: AsyncConnection) -> None:
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id UUID PRIMARY KEY,
                user_id UUID REFERENCES users(id) ON DELETE SET NULL,
                module VARCHAR(50) NOT NULL,
                action VARCHAR(50) NOT NULL,
                resource_type VARCHAR(50),
                resource_id VARCHAR(100),
                status VARCHAR(30) NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL
            )
            """
        )
    )
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_audit_logs_user_id ON audit_logs (user_id)"))
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_audit_logs_module_action ON audit_logs (module, action)"))
    await conn.execute(
        text("CREATE INDEX IF NOT EXISTS ix_audit_logs_resource ON audit_logs (resource_type, resource_id)")
    )
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_audit_logs_status ON audit_logs (status)"))
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_audit_logs_created_at ON audit_logs (created_at)"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

version = "003_create_roles_postgresql_20260806223035"
description = "Create roles table"


async def upgrade(conn: AsyncConnection) -> None:
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS roles (
                id UUID PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                description VARCHAR(255),
                active BOOLEAN NOT NULL DEFAULT TRUE
            )
            """
        )
    )
    await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_roles_name ON roles (name)"))

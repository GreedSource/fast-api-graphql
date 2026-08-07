from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

version = "007_add_graphql_contract_columns_postgresql_20260807000000"
description = "Add GraphQL contract columns to existing tables"


async def upgrade(conn: AsyncConnection) -> None:
    await conn.execute(text("ALTER TABLE modules ADD COLUMN IF NOT EXISTS key VARCHAR(50)"))
    await conn.execute(text("ALTER TABLE modules ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT TRUE"))
    await conn.execute(text("ALTER TABLE actions ADD COLUMN IF NOT EXISTS key VARCHAR(50)"))
    await conn.execute(text("ALTER TABLE actions ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT TRUE"))
    await conn.execute(text("ALTER TABLE roles ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT TRUE"))
    await conn.execute(text("ALTER TABLE permissions ADD COLUMN IF NOT EXISTS description VARCHAR(255)"))

    await conn.execute(text("UPDATE modules SET key = lower(name) WHERE key IS NULL"))
    await conn.execute(text("UPDATE actions SET key = lower(name) WHERE key IS NULL"))
    await conn.execute(text("ALTER TABLE modules ALTER COLUMN key SET NOT NULL"))
    await conn.execute(text("ALTER TABLE actions ALTER COLUMN key SET NOT NULL"))
    await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_modules_key ON modules (key)"))
    await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_actions_key ON actions (key)"))

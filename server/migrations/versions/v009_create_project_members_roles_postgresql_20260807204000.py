from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

version = "009_create_project_members_roles_postgresql_20260807204000"
description = "Create project roles, project role permissions and project members"


async def upgrade(conn: AsyncConnection) -> None:
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS project_roles (
                id UUID PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                description VARCHAR(255),
                active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL
            )
            """
        )
    )
    await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_project_roles_name ON project_roles (name)"))

    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS project_role_permissions (
                project_role_id UUID NOT NULL REFERENCES project_roles(id) ON DELETE CASCADE,
                permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
                PRIMARY KEY (project_role_id, permission_id)
            )
            """
        )
    )

    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS project_members (
                id UUID PRIMARY KEY,
                project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                project_role_id UUID NOT NULL REFERENCES project_roles(id) ON DELETE RESTRICT,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
                CONSTRAINT uq_project_member_user UNIQUE (project_id, user_id)
            )
            """
        )
    )
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_project_members_project_id ON project_members (project_id)"))
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_project_members_user_id ON project_members (user_id)"))

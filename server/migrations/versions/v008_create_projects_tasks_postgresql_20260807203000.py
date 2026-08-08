from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

version = "008_create_projects_tasks_postgresql_20260807203000"
description = "Create projects and tasks tables"


async def upgrade(conn: AsyncConnection) -> None:
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id UUID PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                description TEXT,
                status VARCHAR(30) NOT NULL DEFAULT 'active',
                owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
                archived_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL
            )
            """
        )
    )
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_projects_owner_id ON projects (owner_id)"))
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_projects_status ON projects (status)"))

    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id UUID PRIMARY KEY,
                project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                title VARCHAR(160) NOT NULL,
                description TEXT,
                status VARCHAR(30) NOT NULL DEFAULT 'todo',
                priority VARCHAR(30) NOT NULL DEFAULT 'medium',
                assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
                created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
                due_date TIMESTAMP WITH TIME ZONE,
                completed_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL
            )
            """
        )
    )
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_project_id ON tasks (project_id)"))
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_assignee_id ON tasks (assignee_id)"))
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_created_by_id ON tasks (created_by_id)"))
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_status ON tasks (status)"))

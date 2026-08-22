# ruff: noqa: E501

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

version = "011_create_crm_platform_postgresql_20260822120000"
description = "Create CRM organizations, teams, memberships and commercial resources"


async def upgrade(conn: AsyncConnection) -> None:
    await conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS crm_organizations (
            id UUID PRIMARY KEY, name VARCHAR(160) NOT NULL, slug VARCHAR(160) NOT NULL UNIQUE,
            created_at TIMESTAMPTZ NOT NULL, updated_at TIMESTAMPTZ NOT NULL
        )
    """)
    )
    await conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS crm_teams (
            id UUID PRIMARY KEY, organization_id UUID NOT NULL REFERENCES crm_organizations(id) ON DELETE CASCADE,
            name VARCHAR(160) NOT NULL, description TEXT, created_at TIMESTAMPTZ NOT NULL, updated_at TIMESTAMPTZ NOT NULL,
            UNIQUE (organization_id, name)
        )
    """)
    )
    await conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS crm_team_members (
            id UUID PRIMARY KEY, team_id UUID NOT NULL REFERENCES crm_teams(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role VARCHAR(40) NOT NULL, scope VARCHAR(20) NOT NULL CHECK (scope IN ('OWN','TEAM','ORGANIZATION','GLOBAL')),
            created_at TIMESTAMPTZ NOT NULL, UNIQUE (team_id, user_id)
        )
    """)
    )
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_crm_team_members_user_id ON crm_team_members (user_id)"))

    await conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS crm_companies (
            id UUID PRIMARY KEY, organization_id UUID NOT NULL REFERENCES crm_organizations(id) ON DELETE CASCADE,
            team_id UUID REFERENCES crm_teams(id) ON DELETE SET NULL, owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
            name VARCHAR(160) NOT NULL, industry VARCHAR(100), website VARCHAR(255), phone VARCHAR(40), email VARCHAR(255),
            address TEXT, status VARCHAR(30) NOT NULL DEFAULT 'active', archived_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL, updated_at TIMESTAMPTZ NOT NULL
        )
    """)
    )
    await conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS crm_contacts (
            id UUID PRIMARY KEY, organization_id UUID NOT NULL REFERENCES crm_organizations(id) ON DELETE CASCADE,
            company_id UUID REFERENCES crm_companies(id) ON DELETE SET NULL, team_id UUID REFERENCES crm_teams(id) ON DELETE SET NULL,
            owner_id UUID REFERENCES users(id) ON DELETE SET NULL, name VARCHAR(100) NOT NULL, lastname VARCHAR(100) NOT NULL,
            email VARCHAR(255), phone VARCHAR(40), position VARCHAR(120), status VARCHAR(30) NOT NULL DEFAULT 'active',
            created_at TIMESTAMPTZ NOT NULL, updated_at TIMESTAMPTZ NOT NULL
        )
    """)
    )
    await conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS crm_leads (
            id UUID PRIMARY KEY, organization_id UUID NOT NULL REFERENCES crm_organizations(id) ON DELETE CASCADE,
            company_id UUID REFERENCES crm_companies(id) ON DELETE SET NULL, contact_id UUID REFERENCES crm_contacts(id) ON DELETE SET NULL,
            team_id UUID REFERENCES crm_teams(id) ON DELETE SET NULL, owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
            name VARCHAR(160) NOT NULL, source VARCHAR(80), status VARCHAR(30) NOT NULL DEFAULT 'new', score INTEGER NOT NULL DEFAULT 0,
            archived_at TIMESTAMPTZ, converted_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL, updated_at TIMESTAMPTZ NOT NULL,
            CHECK (score BETWEEN 0 AND 100)
        )
    """)
    )
    await conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS crm_opportunities (
            id UUID PRIMARY KEY, organization_id UUID NOT NULL REFERENCES crm_organizations(id) ON DELETE CASCADE,
            company_id UUID REFERENCES crm_companies(id) ON DELETE SET NULL, contact_id UUID REFERENCES crm_contacts(id) ON DELETE SET NULL,
            lead_id UUID REFERENCES crm_leads(id) ON DELETE SET NULL, team_id UUID REFERENCES crm_teams(id) ON DELETE SET NULL,
            owner_id UUID REFERENCES users(id) ON DELETE SET NULL, name VARCHAR(160) NOT NULL,
            value NUMERIC(14,2) NOT NULL DEFAULT 0, probability INTEGER NOT NULL DEFAULT 0,
            stage VARCHAR(30) NOT NULL DEFAULT 'qualified', expected_close_date TIMESTAMPTZ, closed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL, updated_at TIMESTAMPTZ NOT NULL,
            CHECK (value >= 0), CHECK (probability BETWEEN 0 AND 100)
        )
    """)
    )
    await conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS crm_activities (
            id UUID PRIMARY KEY, organization_id UUID NOT NULL REFERENCES crm_organizations(id) ON DELETE CASCADE,
            company_id UUID REFERENCES crm_companies(id) ON DELETE CASCADE, contact_id UUID REFERENCES crm_contacts(id) ON DELETE CASCADE,
            lead_id UUID REFERENCES crm_leads(id) ON DELETE CASCADE, opportunity_id UUID REFERENCES crm_opportunities(id) ON DELETE CASCADE,
            team_id UUID REFERENCES crm_teams(id) ON DELETE SET NULL, owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
            activity_type VARCHAR(30) NOT NULL, subject VARCHAR(180) NOT NULL, description TEXT, status VARCHAR(30) NOT NULL DEFAULT 'pending',
            scheduled_at TIMESTAMPTZ, completed_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL, updated_at TIMESTAMPTZ NOT NULL
        )
    """)
    )
    for table in ("crm_companies", "crm_contacts", "crm_leads", "crm_opportunities", "crm_activities"):
        await conn.execute(text(f"CREATE INDEX IF NOT EXISTS ix_{table}_organization_id ON {table} (organization_id)"))
        await conn.execute(text(f"CREATE INDEX IF NOT EXISTS ix_{table}_team_id ON {table} (team_id)"))
        await conn.execute(text(f"CREATE INDEX IF NOT EXISTS ix_{table}_owner_id ON {table} (owner_id)"))

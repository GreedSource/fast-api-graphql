from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

version = "012_move_crm_tables_to_schema_postgresql_20260822133000"
description = "Move CRM tables into the crm schema and remove the crm_ table prefix"

CRM_TABLES = (
    ("crm_organizations", "organizations"),
    ("crm_teams", "teams"),
    ("crm_team_members", "team_members"),
    ("crm_companies", "companies"),
    ("crm_contacts", "contacts"),
    ("crm_leads", "leads"),
    ("crm_opportunities", "opportunities"),
    ("crm_activities", "activities"),
)


async def upgrade(conn: AsyncConnection) -> None:
    await conn.execute(text("CREATE SCHEMA IF NOT EXISTS crm"))

    for legacy_name, new_name in CRM_TABLES:
        await conn.execute(
            text(
                f"""
                DO $$
                BEGIN
                    IF to_regclass('public.{legacy_name}') IS NOT NULL THEN
                        ALTER TABLE public.{legacy_name} SET SCHEMA crm;
                    END IF;
                END $$;
                """
            )
        )
        await conn.execute(
            text(
                f"""
                DO $$
                BEGIN
                    IF to_regclass('crm.{legacy_name}') IS NOT NULL
                       AND to_regclass('crm.{new_name}') IS NULL THEN
                        ALTER TABLE crm.{legacy_name} RENAME TO {new_name};
                    END IF;
                END $$;
                """
            )
        )

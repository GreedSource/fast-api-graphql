import pytest

from server.migrations.versions.v012_move_crm_tables_to_schema_postgresql_20260822133000 import (
    CRM_TABLES,
    description,
    upgrade,
    version,
)
from server.models.orm.activity_orm import ActivityORM
from server.models.orm.company_orm import CompanyORM
from server.models.orm.contact_orm import ContactORM
from server.models.orm.crm_organization_orm import CRMOrganizationORM
from server.models.orm.crm_team_orm import CRMTeamMemberORM, CRMTeamORM
from server.models.orm.lead_orm import LeadORM
from server.models.orm.opportunity_orm import OpportunityORM


class RecordingConnection:
    def __init__(self):
        self.statements = []

    async def execute(self, statement):
        self.statements.append(str(statement))


@pytest.mark.asyncio
async def test_crm_schema_migration_creates_schema_and_renames_every_legacy_table():
    connection = RecordingConnection()

    await upgrade(connection)

    sql = "\n".join(connection.statements)
    assert "CREATE SCHEMA IF NOT EXISTS crm" in sql
    assert len(connection.statements) == 1 + len(CRM_TABLES) * 2
    for legacy_name, new_name in CRM_TABLES:
        assert f"public.{legacy_name} SET SCHEMA crm" in sql
        assert f"crm.{legacy_name} RENAME TO {new_name}" in sql


def test_crm_schema_migration_has_a_unique_version_and_descriptive_contract():
    assert version.startswith("012_")
    assert "schema" in description.lower()
    assert {new_name for _, new_name in CRM_TABLES} == {
        "organizations",
        "teams",
        "team_members",
        "companies",
        "contacts",
        "leads",
        "opportunities",
        "activities",
    }


def test_crm_models_use_the_new_schema_and_table_names():
    models = {
        CRMOrganizationORM: "crm.organizations",
        CRMTeamORM: "crm.teams",
        CRMTeamMemberORM: "crm.team_members",
        CompanyORM: "crm.companies",
        ContactORM: "crm.contacts",
        LeadORM: "crm.leads",
        OpportunityORM: "crm.opportunities",
        ActivityORM: "crm.activities",
    }

    assert {model.__table__.fullname for model in models} == set(models.values())

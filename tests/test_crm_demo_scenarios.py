from server.seeders.crm_demo_scenarios import (
    DEMO_CRM_ACTIVITIES,
    DEMO_CRM_COMPANIES,
    DEMO_CRM_CONTACTS,
    DEMO_CRM_LEADS,
    DEMO_CRM_OPPORTUNITIES,
    DEMO_CRM_ORGANIZATION,
    DEMO_CRM_TEAM_MEMBERS,
    DEMO_CRM_TEAMS,
)
from server.seeders.demo_scenarios import DEMO_USERS


def test_crm_demo_catalog_is_unique_and_covers_the_main_views():
    assert DEMO_CRM_ORGANIZATION["slug"] == "northstar-labs"
    assert len({team["name"] for team in DEMO_CRM_TEAMS}) == len(DEMO_CRM_TEAMS)
    assert len({company["name"] for company in DEMO_CRM_COMPANIES}) == len(DEMO_CRM_COMPANIES)
    assert len({lead["name"] for lead in DEMO_CRM_LEADS}) == len(DEMO_CRM_LEADS)
    assert len({opportunity["name"] for opportunity in DEMO_CRM_OPPORTUNITIES}) == len(DEMO_CRM_OPPORTUNITIES)
    assert len({activity["subject"] for activity in DEMO_CRM_ACTIVITIES}) == len(DEMO_CRM_ACTIVITIES)

    assert {lead["status"] for lead in DEMO_CRM_LEADS} == {"new", "contacted", "qualified", "opportunity", "lost"}
    assert {opportunity["stage"] for opportunity in DEMO_CRM_OPPORTUNITIES} == {
        "qualified",
        "proposal",
        "negotiation",
        "won",
        "lost",
    }
    assert {activity["status"] for activity in DEMO_CRM_ACTIVITIES} == {"pending", "completed"}


def test_crm_demo_references_are_resolvable():
    users = {user["email"] for user in DEMO_USERS}
    teams = {team["name"] for team in DEMO_CRM_TEAMS}
    companies = {company["name"] for company in DEMO_CRM_COMPANIES}
    contacts_by_email = {contact["email"]: contact for contact in DEMO_CRM_CONTACTS}
    leads = {lead["name"] for lead in DEMO_CRM_LEADS}
    opportunities = {opportunity["name"] for opportunity in DEMO_CRM_OPPORTUNITIES}

    for member in DEMO_CRM_TEAM_MEMBERS:
        assert member["team_name"] in teams
        assert member["user_email"] in users

    for company in DEMO_CRM_COMPANIES:
        assert company["team_name"] in teams
        assert company["owner_email"] in users

    for contact in DEMO_CRM_CONTACTS:
        assert contact["company_name"] in companies
        assert contact["team_name"] in teams
        assert contact["owner_email"] in users

    for lead in DEMO_CRM_LEADS:
        assert lead["company_name"] in companies
        assert lead["contact_email"] in contacts_by_email
        assert lead["team_name"] in teams
        assert lead["owner_email"] in users

    for opportunity in DEMO_CRM_OPPORTUNITIES:
        assert opportunity["company_name"] in companies
        assert opportunity["contact_email"] in contacts_by_email
        assert opportunity["lead_name"] in leads
        assert opportunity["team_name"] in teams
        assert opportunity["owner_email"] in users

    for activity in DEMO_CRM_ACTIVITIES:
        assert activity["company_name"] in companies
        assert activity["contact_email"] in contacts_by_email
        assert activity["team_name"] in teams
        assert activity["owner_email"] in users
        assert activity.get("lead_name", activity.get("opportunity_name")) in leads | opportunities

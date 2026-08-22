from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.helpers.logger_helper import LoggerHelper
from server.models.orm.activity_orm import ActivityORM
from server.models.orm.audit_log_orm import AuditLogORM
from server.models.orm.company_orm import CompanyORM
from server.models.orm.contact_orm import ContactORM
from server.models.orm.crm_organization_orm import CRMOrganizationORM
from server.models.orm.crm_team_orm import CRMTeamMemberORM, CRMTeamORM
from server.models.orm.lead_orm import LeadORM
from server.models.orm.opportunity_orm import OpportunityORM
from server.models.orm.user_orm import UserORM
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


async def seed():
    async with AsyncSessionLocal() as session:
        users = await _map_users(session)
        organization = await _get_or_create_organization(session)
        teams = await _get_or_create_teams(session, organization)
        await _ensure_team_members(session, organization, teams, users)
        companies = await _get_or_create_companies(session, organization, teams, users)
        contacts = await _get_or_create_contacts(session, organization, teams, users, companies)
        leads = await _get_or_create_leads(session, organization, teams, users, companies, contacts)
        opportunities = await _get_or_create_opportunities(
            session, organization, teams, users, companies, contacts, leads
        )
        activities = await _get_or_create_activities(
            session, organization, teams, users, companies, contacts, leads, opportunities
        )
        await _ensure_audit_logs(session, users, companies, leads, opportunities, activities)
        await session.commit()

        LoggerHelper.success(
            "CRM demo sembrado: "
            f"1 organización, {len(teams)} equipos, {len(companies)} empresas, "
            f"{len(contacts)} contactos, {len(leads)} leads, {len(opportunities)} oportunidades "
            f"y {len(activities)} actividades."
        )


async def _map_users(session):
    result = await session.execute(select(UserORM))
    return {user.email: user for user in result.scalars().all()}


async def _get_or_create_organization(session):
    result = await session.execute(
        select(CRMOrganizationORM).where(CRMOrganizationORM.slug == DEMO_CRM_ORGANIZATION["slug"])
    )
    organization = result.scalar_one_or_none()
    if organization:
        return organization

    organization = CRMOrganizationORM(**DEMO_CRM_ORGANIZATION)
    session.add(organization)
    await session.flush()
    LoggerHelper.success(f"Organización CRM creada: {organization.name}")
    return organization


async def _get_or_create_teams(session, organization):
    result = await session.execute(select(CRMTeamORM).where(CRMTeamORM.organization_id == organization.id))
    teams = {team.name: team for team in result.scalars().all()}
    for item in DEMO_CRM_TEAMS:
        if item["name"] in teams:
            continue
        team = CRMTeamORM(organization_id=organization.id, **item)
        session.add(team)
        await session.flush()
        teams[team.name] = team
        LoggerHelper.success(f"Equipo CRM creado: {team.name}")
    return teams


async def _ensure_team_members(session, organization, teams, users):
    result = await session.execute(
        select(CRMTeamMemberORM)
        .join(CRMTeamORM, CRMTeamORM.id == CRMTeamMemberORM.team_id)
        .where(CRMTeamORM.organization_id == organization.id)
    )
    existing = {(member.team_id, member.user_id) for member in result.scalars().all()}
    for item in DEMO_CRM_TEAM_MEMBERS:
        team = teams.get(item["team_name"])
        user = users.get(item["user_email"])
        if not team or not user or (team.id, user.id) in existing:
            continue
        session.add(
            CRMTeamMemberORM(
                team_id=team.id,
                user_id=user.id,
                role=item["role"],
                scope=item["scope"],
            )
        )
        existing.add((team.id, user.id))


async def _get_or_create_companies(session, organization, teams, users):
    result = await session.execute(select(CompanyORM).where(CompanyORM.organization_id == organization.id))
    companies = {company.name: company for company in result.scalars().all()}
    for item in DEMO_CRM_COMPANIES:
        if item["name"] in companies:
            continue
        company = CompanyORM(
            organization_id=organization.id,
            team_id=teams[item["team_name"]].id,
            owner_id=users[item["owner_email"]].id,
            **{key: value for key, value in item.items() if key not in {"team_name", "owner_email"}},
        )
        session.add(company)
        await session.flush()
        companies[company.name] = company
    return companies


async def _get_or_create_contacts(session, organization, teams, users, companies):
    result = await session.execute(select(ContactORM).where(ContactORM.organization_id == organization.id))
    contacts = {(contact.name, contact.lastname): contact for contact in result.scalars().all()}
    for item in DEMO_CRM_CONTACTS:
        key = (item["name"], item["lastname"])
        if key in contacts:
            continue
        contact = ContactORM(
            organization_id=organization.id,
            company_id=companies[item["company_name"]].id,
            team_id=teams[item["team_name"]].id,
            owner_id=users[item["owner_email"]].id,
            **{key: value for key, value in item.items() if key not in {"company_name", "team_name", "owner_email"}},
        )
        session.add(contact)
        await session.flush()
        contacts[key] = contact
    return contacts


async def _get_or_create_leads(session, organization, teams, users, companies, contacts):
    result = await session.execute(select(LeadORM).where(LeadORM.organization_id == organization.id))
    leads = {lead.name: lead for lead in result.scalars().all()}
    for item in DEMO_CRM_LEADS:
        if item["name"] in leads:
            continue
        contact = contacts[_contact_key(item["contact_email"], contacts)]
        lead = LeadORM(
            organization_id=organization.id,
            company_id=companies[item["company_name"]].id,
            contact_id=contact.id,
            team_id=teams[item["team_name"]].id,
            owner_id=users[item["owner_email"]].id,
            **{
                key: value
                for key, value in item.items()
                if key not in {"company_name", "contact_email", "team_name", "owner_email"}
            },
        )
        session.add(lead)
        await session.flush()
        leads[lead.name] = lead
    return leads


async def _get_or_create_opportunities(session, organization, teams, users, companies, contacts, leads):
    result = await session.execute(select(OpportunityORM).where(OpportunityORM.organization_id == organization.id))
    opportunities = {opportunity.name: opportunity for opportunity in result.scalars().all()}
    now = datetime.now(timezone.utc)
    for item in DEMO_CRM_OPPORTUNITIES:
        if item["name"] in opportunities:
            continue
        contact = contacts[_contact_key(item["contact_email"], contacts)]
        lead = leads.get(item.get("lead_name"))
        expected_close = now + timedelta(days=item["expected_close_days"])
        closed_at = now if item["stage"] in {"won", "lost"} else None
        opportunity = OpportunityORM(
            organization_id=organization.id,
            company_id=companies[item["company_name"]].id,
            contact_id=contact.id,
            lead_id=lead.id if lead else None,
            team_id=teams[item["team_name"]].id,
            owner_id=users[item["owner_email"]].id,
            value=Decimal(item["value"]),
            expected_close_date=expected_close,
            closed_at=closed_at,
            **{
                key: value
                for key, value in item.items()
                if key
                not in {
                    "company_name",
                    "contact_email",
                    "team_name",
                    "owner_email",
                    "value",
                    "expected_close_days",
                    "lead_name",
                }
            },
        )
        session.add(opportunity)
        await session.flush()
        opportunities[opportunity.name] = opportunity
    return opportunities


async def _get_or_create_activities(session, organization, teams, users, companies, contacts, leads, opportunities):
    result = await session.execute(select(ActivityORM).where(ActivityORM.organization_id == organization.id))
    activities = {activity.subject: activity for activity in result.scalars().all()}
    now = datetime.now(timezone.utc)
    for item in DEMO_CRM_ACTIVITIES:
        if item["subject"] in activities:
            continue
        contact = contacts[_contact_key(item["contact_email"], contacts)]
        lead = leads.get(item.get("lead_name"))
        opportunity = opportunities.get(item.get("opportunity_name"))
        activity = ActivityORM(
            organization_id=organization.id,
            company_id=companies[item["company_name"]].id,
            contact_id=contact.id,
            lead_id=lead.id if lead else None,
            opportunity_id=opportunity.id if opportunity else None,
            team_id=teams[item["team_name"]].id,
            owner_id=users[item["owner_email"]].id,
            scheduled_at=now + timedelta(days=item["scheduled_days"]),
            completed_at=now + timedelta(days=item["scheduled_days"]) if item["status"] == "completed" else None,
            **{
                key: value
                for key, value in item.items()
                if key
                not in {
                    "company_name",
                    "contact_email",
                    "team_name",
                    "owner_email",
                    "scheduled_days",
                    "lead_name",
                    "opportunity_name",
                }
            },
        )
        session.add(activity)
        await session.flush()
        activities[activity.subject] = activity
    return activities


async def _ensure_audit_logs(session, users, companies, leads, opportunities, activities):
    result = await session.execute(select(AuditLogORM))
    existing = {(log.module, log.action, log.resource_id, log.status) for log in result.scalars().all()}
    samples = [
        ("sofia.director@example.com", "companies", "create", "Company", next(iter(companies.values())).id),
        ("diego.rep@example.com", "leads", "update", "Lead", next(iter(leads.values())).id),
        ("sofia.director@example.com", "opportunities", "update", "Opportunity", next(iter(opportunities.values())).id),
        ("lucia.assistant@example.com", "activities", "create", "Activity", next(iter(activities.values())).id),
    ]
    for user_email, module, action, resource_type, resource_id in samples:
        key = (module, action, str(resource_id), "success")
        if key in existing:
            continue
        user = users.get(user_email)
        session.add(
            AuditLogORM(
                user_id=user.id if user else None,
                module=module,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id),
                status="success",
                metadata_json={"source": "demo-seeder", "organization": DEMO_CRM_ORGANIZATION["slug"]},
            )
        )
        existing.add(key)


def _contact_key(email, contacts):
    for key, contact in contacts.items():
        if contact.email == email:
            return key
    raise KeyError(f"No se encontró contacto demo para {email}")

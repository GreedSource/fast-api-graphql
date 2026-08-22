from sqlalchemy import func, select

from server.db.session import AsyncSessionLocal
from server.models.orm.activity_orm import ActivityORM
from server.models.orm.company_orm import CompanyORM
from server.models.orm.contact_orm import ContactORM
from server.models.orm.lead_orm import LeadORM
from server.models.orm.opportunity_orm import OpportunityORM
from server.repositories.base_repository import parse_uuid


class CRMDashboardRepository:
    models = {
        "companies": CompanyORM,
        "contacts": ContactORM,
        "leads": LeadORM,
        "opportunities": OpportunityORM,
        "activities": ActivityORM,
    }

    def apply_scope(self, stmt, model, access):
        if access["scope"] == "OWN":
            return stmt.where(model.owner_id == parse_uuid(access["user_id"]))
        if access["scope"] == "TEAM":
            return stmt.where(model.team_id == parse_uuid(access["team_id"]))
        return stmt

    async def summarize(self, organization_id, access):
        result = {}
        async with AsyncSessionLocal() as db:
            for key, model in self.models.items():
                stmt = select(func.count(model.id)).where(model.organization_id == parse_uuid(organization_id))
                result[key] = (await db.execute(self.apply_scope(stmt, model, access))).scalar_one()
            pipeline = select(func.coalesce(func.sum(OpportunityORM.value), 0)).where(
                OpportunityORM.organization_id == parse_uuid(organization_id),
                OpportunityORM.stage.notin_(("won", "lost")),
            )
            result["pipelineValue"] = str(
                (await db.execute(self.apply_scope(pipeline, OpportunityORM, access))).scalar_one()
            )
        return result

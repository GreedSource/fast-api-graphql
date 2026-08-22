from server.models.dto.activity_dto import CreateActivityModel, UpdateActivityModel
from server.schema.crm_resource_resolver import CRMResourceResolver
from server.services.activity_service import ActivityService


class ActivityResolver(CRMResourceResolver):
    module = "activities"
    singular = "Activity"
    create_model = CreateActivityModel
    update_model = UpdateActivityModel
    service = ActivityService()

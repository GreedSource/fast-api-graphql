from server.decorators.singleton_decorator import singleton
from server.models.dto.activity_dto import ActivityItemModel, CreateActivityModel, UpdateActivityModel
from server.repositories.activity_repository import ActivityRepository
from server.services.base_service import BaseService


@singleton
class ActivityService(BaseService[CreateActivityModel, UpdateActivityModel, ActivityItemModel]):
    repository = ActivityRepository()
    item_model = ActivityItemModel
    resource_not_found = "Activity not found"

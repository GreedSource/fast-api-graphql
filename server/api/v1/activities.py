from server.api.crud_router import build_scoped_crud_router
from server.models.dto.activity_dto import CreateActivityModel, UpdateActivityModel
from server.services.activity_service import ActivityService

router = build_scoped_crud_router("activities", ActivityService(), CreateActivityModel, UpdateActivityModel)

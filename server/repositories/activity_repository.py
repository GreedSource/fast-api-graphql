from server.decorators.singleton_decorator import singleton
from server.models.orm.activity_orm import ActivityORM
from server.repositories.scoped_resource_repository import ScopedResourceRepository


@singleton
class ActivityRepository(ScopedResourceRepository[ActivityORM]):
    model = ActivityORM

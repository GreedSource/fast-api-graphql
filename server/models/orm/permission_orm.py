import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.db.session import Base

if TYPE_CHECKING:
    from server.models.orm.action_orm import ActionORM
    from server.models.orm.module_orm import ModuleORM
    from server.models.orm.role_orm import RoleORM


class PermissionORM(Base):
    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("module_id", "action_id", name="uq_module_action"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False
    )
    action_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("actions.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    module: Mapped["ModuleORM"] = relationship("ModuleORM", back_populates="permissions", lazy="joined")
    action: Mapped["ActionORM"] = relationship("ActionORM", back_populates="permissions", lazy="joined")
    roles: Mapped[list["RoleORM"]] = relationship("RoleORM", secondary="role_permissions", back_populates="permissions")

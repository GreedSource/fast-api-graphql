import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.db.session import Base

if TYPE_CHECKING:
    from server.models.orm.permission_orm import PermissionORM
    from server.models.orm.project_member_orm import ProjectMemberORM

project_role_permissions = Table(
    "project_role_permissions",
    Base.metadata,
    Column("project_role_id", UUID(as_uuid=True), ForeignKey("project_roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class ProjectRoleORM(Base):
    __tablename__ = "project_roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    permissions: Mapped[list["PermissionORM"]] = relationship(
        "PermissionORM", secondary=project_role_permissions, lazy="selectin"
    )
    members: Mapped[list["ProjectMemberORM"]] = relationship("ProjectMemberORM", back_populates="project_role")

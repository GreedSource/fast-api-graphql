from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from server.db.session import AsyncSessionLocal
from server.helpers.logger_helper import LoggerHelper
from server.models.orm.audit_log_orm import AuditLogORM
from server.models.orm.project_member_orm import ProjectMemberORM
from server.models.orm.project_orm import ProjectORM
from server.models.orm.project_role_orm import ProjectRoleORM
from server.models.orm.role_orm import RoleORM
from server.models.orm.task_orm import TaskORM
from server.models.orm.user_orm import UserORM
from server.seeders.demo_scenarios import DEMO_MEMBERSHIPS, DEMO_PROJECTS, DEMO_TASKS, DEMO_USERS
from server.utils.auth_utils import hash_password


async def seed():
    async with AsyncSessionLocal() as session:
        roles = await _map_by(session, RoleORM, RoleORM.name)
        project_roles = await _map_by(session, ProjectRoleORM, ProjectRoleORM.name)

        users = await _map_by(session, UserORM, UserORM.email)
        for item in DEMO_USERS:
            if item["email"] in users:
                continue
            user = UserORM(
                name=item["name"],
                lastname=item["lastname"],
                email=item["email"],
                password=hash_password(item["password"]),
                role_id=roles[item["role_name"]].id if item["role_name"] in roles else None,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            users[item["email"]] = user
            LoggerHelper.success(f"Demo user creado: {item['email']}")

        projects = await _map_by(session, ProjectORM, ProjectORM.name)
        for item in DEMO_PROJECTS:
            if item["name"] in projects:
                continue
            project = ProjectORM(
                name=item["name"],
                description=item["description"],
                owner_id=users[item["owner_email"]].id if item["owner_email"] in users else None,
                status=item.get("status", "active"),
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
            projects[item["name"]] = project
            LoggerHelper.success(f"Demo project creado: {item['name']}")

        existing_memberships = await session.execute(select(ProjectMemberORM))
        membership_keys = {(member.project_id, member.user_id) for member in existing_memberships.scalars().all()}
        for item in DEMO_MEMBERSHIPS:
            project = projects.get(item["project_name"])
            user = users.get(item["user_email"])
            project_role = project_roles.get(item["project_role_name"])
            if not project or not user or not project_role or (project.id, user.id) in membership_keys:
                continue
            member = ProjectMemberORM(project_id=project.id, user_id=user.id, project_role_id=project_role.id)
            session.add(member)
            await session.commit()
            membership_keys.add((project.id, user.id))
            LoggerHelper.success(f"Demo membership creado: {item['project_name']}:{item['user_email']}")

        tasks = await _map_by(session, TaskORM, TaskORM.title)
        for item in DEMO_TASKS:
            if item["title"] in tasks:
                continue
            project = projects.get(item["project_name"])
            if not project:
                continue
            task = TaskORM(
                project_id=project.id,
                title=item["title"],
                description=item["description"],
                priority=item["priority"],
                status=item.get("status", "todo"),
                assignee_id=users[item["assignee_email"]].id if item["assignee_email"] in users else None,
                created_by_id=users[item["created_by_email"]].id if item["created_by_email"] in users else None,
                due_date=datetime.now(timezone.utc) + timedelta(days=item.get("due_days", 14)),
                completed_at=datetime.now(timezone.utc) if item.get("status") == "done" else None,
            )
            session.add(task)
            await session.commit()
            LoggerHelper.success(f"Demo task creada: {item['title']}")

        tasks = await _map_by(session, TaskORM, TaskORM.title)
        await _ensure_audit_logs(session, users, projects, tasks)
        await session.commit()


async def _map_by(session, model, column):
    result = await session.execute(select(model))
    return {getattr(item, column.key): item for item in result.scalars().all()}


async def _ensure_audit_logs(session, users, projects, tasks):
    result = await session.execute(select(AuditLogORM))
    existing = {(log.module, log.action, log.resource_id, log.status) for log in result.scalars().all()}
    project = projects["Plataforma de autorización"]
    blocked_task = tasks["Resolver bloqueo de WebSocket"]
    completed_task = tasks["Validar permisos contextuales"]
    samples = [
        ("joel.manager@example.com", "projects", "create", "Project", project.id),
        ("joel.manager@example.com", "project_members", "assign", "ProjectMember", project.id),
        ("maria.developer@example.com", "tasks", "update", "Task", blocked_task.id),
        ("joel.manager@example.com", "tasks", "complete", "Task", completed_task.id),
        (
            "joel.manager@example.com",
            "projects",
            "archive",
            "Project",
            projects["Migración de reportes"].id,
        ),
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
                metadata_json={"source": "demo-seeder"},
            )
        )
        existing.add(key)

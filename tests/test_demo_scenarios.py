from server.seeders.demo_scenarios import DEMO_MEMBERSHIPS, DEMO_PROJECTS, DEMO_TASKS, DEMO_USERS


def test_demo_users_are_unique_and_cover_portfolio_roles():
    emails = [user["email"] for user in DEMO_USERS]
    role_names = {user["role_name"] for user in DEMO_USERS}

    assert len(emails) == len(set(emails))
    assert {"project_manager", "developer", "client", "viewer"}.issubset(role_names)


def test_demo_memberships_show_same_user_with_multiple_project_roles():
    joel_roles = {
        item["project_name"]: item["project_role_name"]
        for item in DEMO_MEMBERSHIPS
        if item["user_email"] == "joel.manager@example.com"
    }

    assert joel_roles == {
        "Project A": "project_manager",
        "Project B": "developer",
        "Project C": "viewer",
    }


def test_demo_tasks_reference_existing_projects_and_users():
    project_names = {project["name"] for project in DEMO_PROJECTS}
    user_emails = {user["email"] for user in DEMO_USERS}

    for task in DEMO_TASKS:
        assert task["project_name"] in project_names
        assert task["created_by_email"] in user_emails
        assert task["assignee_email"] is None or task["assignee_email"] in user_emails

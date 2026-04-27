from __future__ import annotations

from collections import Counter

from services.project_service import count_tasks_by_owner, sort_key_for_priority


def build_dashboard_data(projects):
    actions = [action for project in projects for action in project.get("actions", [])]

    summary = {
        "total_projects": len(projects),
        "active_projects": len(
            [project for project in projects if project.get("project_status") not in {"Completed", "Cancelled"}]
        ),
        "completed_projects": len([project for project in projects if project.get("project_status") == "Completed"]),
        "total_actions": len(actions),
        "overdue_actions": len([action for action in actions if action.get("is_overdue")]),
        "high_priority_actions": len(
            [action for action in actions if action.get("priority") in {"High", "Urgent"}]
        ),
        "upcoming_due_tasks": len([action for action in actions if action.get("is_upcoming")]),
    }

    projects_by_status = Counter(project.get("project_status", "Not Started") for project in projects)
    actions_by_priority = Counter(action.get("priority", "Medium") for action in actions)
    tasks_by_owner = count_tasks_by_owner(projects)

    overdue_actions = sorted(
        [action for action in actions if action.get("is_overdue")],
        key=lambda item: item.get("due_date") or "",
    )[:8]
    upcoming_actions = sorted(
        [action for action in actions if action.get("is_upcoming")],
        key=lambda item: item.get("due_date") or "",
    )[:8]
    attention_projects = sorted(
        projects,
        key=lambda item: (
            item.get("overdue_count", 0),
            sort_key_for_priority(item.get("priority", "Low")),
            item.get("updated_at", ""),
        ),
        reverse=True,
    )[:6]

    return {
        "summary": summary,
        "projects_by_status": projects_by_status,
        "actions_by_priority": actions_by_priority,
        "tasks_by_owner": tasks_by_owner,
        "overdue_actions": overdue_actions,
        "upcoming_actions": upcoming_actions,
        "attention_projects": attention_projects,
    }

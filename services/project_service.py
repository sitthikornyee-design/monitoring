from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

ACTION_STATUS_OPTIONS = [
    "Not Started",
    "In Progress",
    "Pending",
    "Completed",
    "On Hold",
    "Cancelled",
]

BOARD_COLUMNS = ["Not Started", "In Progress", "Pending", "Completed", "On Hold"]
PRIORITY_OPTIONS = ["Low", "Medium", "High", "Urgent"]
SORT_OPTIONS = [
    ("updated_desc", "Recently updated"),
    ("due_asc", "Due date ascending"),
    ("due_desc", "Due date descending"),
    ("priority_desc", "Highest priority"),
    ("name_asc", "Project name A-Z"),
]

STATUS_BADGE_CLASSES = {
    "Not Started": "badge-neutral",
    "In Progress": "badge-info",
    "Pending": "badge-warning",
    "Completed": "badge-success",
    "On Hold": "badge-purple",
    "Cancelled": "badge-dark",
    "Overdue": "badge-danger",
    "At Risk": "badge-danger",
}

PRIORITY_BADGE_CLASSES = {
    "Low": "badge-neutral",
    "Medium": "badge-info",
    "High": "badge-warning",
    "Urgent": "badge-danger",
}


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def status_badge_class(status):
    return STATUS_BADGE_CLASSES.get(status, "badge-neutral")


def priority_badge_class(priority):
    return PRIORITY_BADGE_CLASSES.get(priority, "badge-neutral")


def get_action_display_status(action, today_value=None):
    today_value = today_value or date.today()
    action_status = action.get("action_status", "Not Started")
    due_date = parse_date(action.get("due_date"))
    if due_date and due_date < today_value and action_status not in {"Completed", "Cancelled"}:
        return "Overdue"
    return action_status


def is_action_overdue(action, today_value=None):
    return get_action_display_status(action, today_value) == "Overdue"


def is_action_upcoming(action, today_value=None):
    today_value = today_value or date.today()
    due_date = parse_date(action.get("due_date"))
    if not due_date:
        return False
    if action.get("action_status") in {"Completed", "Cancelled"}:
        return False
    return today_value <= due_date <= today_value + timedelta(days=3)


def calculate_project_status(actions):
    if not actions:
        return "Not Started"

    statuses = [action.get("action_status", "Not Started") for action in actions]

    if all(status == "Completed" for status in statuses):
        return "Completed"
    if all(status == "Cancelled" for status in statuses):
        return "Cancelled"
    if any(action.get("is_overdue") for action in actions):
        return "At Risk"
    if any(status in {"In Progress", "Pending"} for status in statuses):
        return "In Progress"
    return "Not Started"


def sort_key_for_priority(priority):
    return {
        "Urgent": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1,
    }.get(priority, 0)


def decorate_action(action):
    display_status = get_action_display_status(action)
    due_date = parse_date(action.get("due_date"))
    start_date = parse_date(action.get("start_date"))
    action_data = {**action}
    action_data.pop("progress_percent", None)

    return {
        **action_data,
        "display_status": display_status,
        "is_overdue": display_status == "Overdue",
        "is_upcoming": is_action_upcoming(action),
        "badge_class": status_badge_class(display_status),
        "priority_badge_class": priority_badge_class(action.get("priority", "Medium")),
        "start_date_obj": start_date,
        "due_date_obj": due_date,
    }


def compute_project_metrics(projects, actions):
    grouped_actions = defaultdict(list)
    for action in actions:
        grouped_actions[action.get("project_id")].append(decorate_action(action))

    computed = []
    for project in projects:
        project_actions = grouped_actions.get(project.get("id"), [])
        project_status = calculate_project_status(project_actions)
        overdue_count = len([action for action in project_actions if action["is_overdue"]])
        upcoming_count = len([action for action in project_actions if action["is_upcoming"]])

        computed.append(
            {
                **project,
                "actions": sorted(
                    project_actions,
                    key=lambda item: (
                        item.get("due_date_obj") or date.max,
                        item.get("action_name", "").lower(),
                    ),
                ),
                "project_status": project_status,
                "project_status_badge_class": status_badge_class(project_status),
                "priority_badge_class": priority_badge_class(project.get("priority", "Medium")),
                "action_count": len(project_actions),
                "completed_action_count": len(
                    [action for action in project_actions if action.get("action_status") == "Completed"]
                ),
                "overdue_count": overdue_count,
                "upcoming_count": upcoming_count,
                "has_alert": overdue_count > 0 or upcoming_count > 0,
                "is_at_risk": project_status == "At Risk",
                "owner_label": project.get("owner", "Unassigned"),
                "updated_at_obj": project.get("updated_at", ""),
            }
        )

    return computed


def filter_projects(projects, filters):
    q = filters.get("q", "").strip().lower()
    status = filters.get("status", "all")
    priority = filters.get("priority", "all")
    owner = filters.get("owner", "all")
    alert = filters.get("alert", "all")
    sort = filters.get("sort", "updated_desc")

    filtered = []
    for project in projects:
        if q:
            haystack = " ".join(
                [
                    project.get("service_name", ""),
                    project.get("project_name", ""),
                    project.get("client_name", ""),
                    project.get("owner", ""),
                    project.get("remark", ""),
                    *[
                        " ".join(
                            [
                                action.get("action_name", ""),
                                action.get("description", ""),
                                action.get("assignee", ""),
                                action.get("next_action", ""),
                                action.get("remark", ""),
                            ]
                        )
                        for action in project.get("actions", [])
                    ],
                ]
            ).lower()
            if q not in haystack:
                continue

        if status != "all" and project.get("project_status") != status:
            continue
        if priority != "all" and project.get("priority") != priority:
            continue
        if owner != "all" and project.get("owner") != owner:
            continue
        if alert == "overdue" and not project.get("overdue_count"):
            continue
        if alert == "upcoming" and not project.get("upcoming_count"):
            continue
        if alert == "at_risk" and not project.get("is_at_risk"):
            continue

        filtered.append(project)

    if sort == "due_asc":
        filtered.sort(key=lambda item: parse_date(item.get("due_date")) or date.max)
    elif sort == "due_desc":
        filtered.sort(key=lambda item: parse_date(item.get("due_date")) or date.min, reverse=True)
    elif sort == "priority_desc":
        filtered.sort(key=lambda item: sort_key_for_priority(item.get("priority")), reverse=True)
    elif sort == "name_asc":
        filtered.sort(key=lambda item: item.get("project_name", "").lower())
    else:
        filtered.sort(key=lambda item: item.get("updated_at", ""), reverse=True)

    return filtered


def compute_filter_options(projects):
    owners = sorted({project.get("owner", "") for project in projects if project.get("owner")})
    statuses = [
        "Not Started",
        "In Progress",
        "Completed",
        "At Risk",
        "Cancelled",
    ]
    return {
        "owners": owners,
        "statuses": statuses,
    }


def compute_action_status_groups(projects):
    groups = {column: [] for column in BOARD_COLUMNS}
    for project in projects:
        for action in project.get("actions", []):
            raw_status = action.get("action_status", "Not Started")
            if raw_status in groups:
                groups[raw_status].append(
                    {
                        **action,
                        "project_name": project.get("project_name"),
                        "client_name": project.get("client_name"),
                        "project_id": project.get("id"),
                    }
                )
    return groups


def _gantt_position(item_start, item_end, timeline_start, timeline_end):
    if not item_start or not item_end or item_end < item_start:
        return {
            "offset": None,
            "span": None,
            "is_clipped_start": False,
            "is_clipped_end": False,
        }

    visible_start = max(item_start, timeline_start)
    visible_end = min(item_end, timeline_end)
    if visible_end < timeline_start or visible_start > timeline_end:
        return {
            "offset": None,
            "span": None,
            "is_clipped_start": item_start < timeline_start,
            "is_clipped_end": item_end > timeline_end,
        }

    return {
        "offset": (visible_start - timeline_start).days,
        "span": (visible_end - visible_start).days + 1,
        "is_clipped_start": item_start < timeline_start,
        "is_clipped_end": item_end > timeline_end,
    }


def compute_gantt_data(projects, visible_start=None, visible_end=None):
    all_dates = []
    for project in projects:
        for value in [project.get("start_date"), project.get("due_date")]:
            parsed = parse_date(value)
            if parsed:
                all_dates.append(parsed)
        for action in project.get("actions", []):
            for value in [action.get("start_date"), action.get("due_date")]:
                parsed = parse_date(value)
                if parsed:
                    all_dates.append(parsed)

    if visible_start and visible_end:
        start = min(visible_start, visible_end)
        end = max(visible_start, visible_end)
    elif all_dates:
        start = min(all_dates)
        end = max(all_dates)
    else:
        start = date.today()
        end = date.today() + timedelta(days=14)

    days = []
    cursor = start
    while cursor <= end:
        days.append(cursor)
        cursor += timedelta(days=1)

    rows = []
    project_groups = []
    for project in projects:
        project_start = parse_date(project.get("start_date"))
        project_due = parse_date(project.get("due_date"))
        project_position = _gantt_position(project_start, project_due, start, end)
        project_row = {
            "type": "project",
            "project_id": project["id"],
            "label": project.get("project_name"),
            "subtitle": project.get("client_name"),
            "status": project.get("project_status"),
            "start": project_start,
            "end": project_due,
            **project_position,
            "action_count": project.get("action_count", 0),
        }
        rows.append(project_row)

        action_rows = []
        for action in project.get("actions", []):
            action_start = parse_date(action.get("start_date"))
            action_due = parse_date(action.get("due_date"))
            action_position = _gantt_position(action_start, action_due, start, end)
            action_row = {
                "type": "action",
                "action_id": action["id"],
                "project_id": project["id"],
                "label": action.get("action_name"),
                "description": action.get("description", ""),
                "subtitle": action.get("assignee") or "Unassigned",
                "status": action.get("display_status"),
                "start": action_start,
                "end": action_due,
                **action_position,
                "priority": action.get("priority", "Medium"),
            }
            rows.append(action_row)
            action_rows.append(action_row)

        project_groups.append(
            {
                "project": project_row,
                "actions": action_rows,
            }
        )

    return {
        "start": start,
        "end": end,
        "days": days,
        "rows": rows,
        "project_groups": project_groups,
    }


def count_tasks_by_owner(projects):
    counter = Counter()
    for project in projects:
        for action in project.get("actions", []):
            owner = action.get("assignee") or project.get("owner") or "Unassigned"
            counter[owner] += 1
    return counter

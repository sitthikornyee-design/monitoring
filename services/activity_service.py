from __future__ import annotations

from datetime import datetime


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def build_log(project_id, action_id, field_name, old_value, new_value, updated_by, comment):
    return {
        "id": f"log-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "project_id": project_id,
        "action_id": action_id,
        "field_name": field_name,
        "old_value": old_value,
        "new_value": new_value,
        "updated_by": updated_by,
        "updated_at": now_iso(),
        "comment": comment,
    }


def build_creation_log(project_id, action_id, field_name, new_value, updated_by, comment):
    return build_log(project_id, action_id, field_name, "", new_value, updated_by, comment)


def build_deletion_log(project_id, action_id, field_name, old_value, updated_by, comment):
    return build_log(project_id, action_id, field_name, old_value, "", updated_by, comment)


def build_field_change_logs(before, after, tracked_fields, project_id, action_id, updated_by):
    logs = []
    for field_name in tracked_fields:
        before_value = before.get(field_name, "")
        after_value = after.get(field_name, "")
        if str(before_value) == str(after_value):
            continue
        logs.append(
            build_log(
                project_id=project_id,
                action_id=action_id,
                field_name=field_name,
                old_value=str(before_value),
                new_value=str(after_value),
                updated_by=updated_by,
                comment=f"Changed {field_name.replace('_', ' ')} from {before_value or '-'} to {after_value or '-'}.",
            )
        )
    return logs


def build_rollup_logs(before_project, after_project, project_id, updated_by):
    logs = []

    if before_project.get("project_status") != after_project.get("project_status"):
        logs.append(
            build_log(
                project_id=project_id,
                action_id="",
                field_name="project_status",
                old_value=before_project.get("project_status", ""),
                new_value=after_project.get("project_status", ""),
                updated_by=updated_by,
                comment=(
                    f"Project status recalculated from {before_project.get('project_status', '-')}"
                    f" to {after_project.get('project_status', '-')}."
                ),
            )
        )

    if int(before_project.get("progress_percent", 0)) != int(after_project.get("progress_percent", 0)):
        logs.append(
            build_log(
                project_id=project_id,
                action_id="",
                field_name="project_progress",
                old_value=str(before_project.get("progress_percent", 0)),
                new_value=str(after_project.get("progress_percent", 0)),
                updated_by=updated_by,
                comment=(
                    f"Project progress recalculated from {before_project.get('progress_percent', 0)}%"
                    f" to {after_project.get('progress_percent', 0)}%."
                ),
            )
        )

    return logs

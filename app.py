from __future__ import annotations

import os
from datetime import date, datetime

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for

from config import get_config, validate_config
from services.activity_service import (
    build_creation_log,
    build_deletion_log,
    build_field_change_logs,
    build_rollup_logs,
)
from services.dashboard_service import build_dashboard_data
from services.project_service import (
    ACTION_STATUS_OPTIONS,
    BOARD_COLUMNS,
    PRIORITY_OPTIONS,
    SORT_OPTIONS,
    compute_action_status_groups,
    compute_filter_options,
    compute_gantt_data,
    compute_project_metrics,
    filter_projects,
    parse_date,
    parse_int,
)
from services.repository import SQLiteRepository

app = Flask(__name__)
app.config.from_object(get_config())
validate_config(app.config)
app.secret_key = app.config["SECRET_KEY"]

BASE_DIR = app.config["BASE_DIR"]
DATA_DIR = app.config["DATA_DIR"]
RUNTIME_DIR = app.config["RUNTIME_DIR"]
DATABASE_PATH = app.config["DATABASE_PATH"]
SCHEMA_PATH = app.config["SCHEMA_PATH"]
repository = SQLiteRepository(
    DATABASE_PATH,
    SCHEMA_PATH,
    seed_dir=DATA_DIR if app.config["SEED_DATA"] else None,
)

DEFAULT_ACTOR = app.config["DEFAULT_ACTOR"]
WORKSPACE_NAME = app.config["WORKSPACE_NAME"]
SPACE_NAME = app.config["SPACE_NAME"]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_workspace():
    return repository.load_workspace()


def save_workspace(projects, actions, comments, activity_logs) -> None:
    repository.save_workspace(projects, actions, comments, activity_logs)


def build_workspace_view():
    workspace = load_workspace()
    computed_projects = compute_project_metrics(workspace["projects"], workspace["actions"])
    return workspace, computed_projects


def current_actor() -> str:
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        return str(payload.get("updated_by", "")).strip() or DEFAULT_ACTOR
    return request.form.get("updated_by", "").strip() or DEFAULT_ACTOR


def project_form_defaults(existing=None):
    record = existing or {}
    return {
        "service_name": record.get("service_name", ""),
        "project_name": record.get("project_name", ""),
        "client_name": record.get("client_name", ""),
        "priority": record.get("priority", "Medium"),
        "owner": record.get("owner", DEFAULT_ACTOR),
        "start_date": record.get("start_date", ""),
        "due_date": record.get("due_date", ""),
        "contact_number": record.get("contact_number", ""),
        "remark": record.get("remark", ""),
    }


def action_form_defaults(project_id="", existing=None):
    record = existing or {}
    return {
        "project_id": record.get("project_id", project_id),
        "action_name": record.get("action_name", ""),
        "description": record.get("description", ""),
        "action_status": record.get("action_status", "Not Started"),
        "priority": record.get("priority", "Medium"),
        "assignee": record.get("assignee", DEFAULT_ACTOR),
        "start_date": record.get("start_date", ""),
        "due_date": record.get("due_date", ""),
        "progress_percent": record.get("progress_percent", 0),
        "remark": record.get("remark", ""),
    }


def validate_project_payload(payload):
    errors = []

    if not payload["service_name"]:
        errors.append("Service name is required.")
    if not payload["project_name"]:
        errors.append("Project name is required.")
    if not payload["owner"]:
        errors.append("Owner is required.")
    if payload["start_date"] and payload["due_date"]:
        if parse_date(payload["due_date"]) and parse_date(payload["start_date"]):
            if parse_date(payload["due_date"]) < parse_date(payload["start_date"]):
                errors.append("Project due date must be after or equal to the start date.")

    return errors


def validate_action_payload(payload):
    errors = []

    if not payload["project_id"]:
        errors.append("Project is required.")
    if not payload["action_name"]:
        errors.append("Action name is required.")
    if payload["start_date"] and payload["due_date"]:
        if parse_date(payload["due_date"]) and parse_date(payload["start_date"]):
            if parse_date(payload["due_date"]) < parse_date(payload["start_date"]):
                errors.append("Action due date must be after or equal to the start date.")
    progress = parse_int(payload["progress_percent"], 0)
    if progress < 0 or progress > 100:
        errors.append("Progress percent must be between 0 and 100.")

    return errors


def build_project_payload(form_data):
    return {
        "service_name": form_data.get("service_name", "").strip(),
        "project_name": form_data.get("project_name", "").strip(),
        "client_name": form_data.get("client_name", "").strip(),
        "priority": form_data.get("priority", "Medium").strip() or "Medium",
        "owner": form_data.get("owner", "").strip(),
        "start_date": form_data.get("start_date", "").strip(),
        "due_date": form_data.get("due_date", "").strip(),
        "contact_number": form_data.get("contact_number", "").strip(),
        "remark": form_data.get("remark", "").strip(),
    }


def build_action_payload(form_data):
    progress_percent = parse_int(form_data.get("progress_percent"), 0)
    return {
        "project_id": form_data.get("project_id", "").strip(),
        "action_name": form_data.get("action_name", "").strip(),
        "description": form_data.get("description", "").strip(),
        "action_status": form_data.get("action_status", "Not Started").strip() or "Not Started",
        "priority": form_data.get("priority", "Medium").strip() or "Medium",
        "assignee": form_data.get("assignee", "").strip() or DEFAULT_ACTOR,
        "start_date": form_data.get("start_date", "").strip(),
        "due_date": form_data.get("due_date", "").strip(),
        "progress_percent": progress_percent,
        "remark": form_data.get("remark", "").strip(),
    }


def build_filters():
    return {
        "q": request.args.get("q", "").strip(),
        "status": request.args.get("status", "all").strip(),
        "priority": request.args.get("priority", "all").strip(),
        "owner": request.args.get("owner", "all").strip(),
        "alert": request.args.get("alert", "all").strip(),
        "sort": request.args.get("sort", "updated_desc").strip(),
    }


@app.template_filter("date_label")
def date_label(value):
    parsed = parse_date(value)
    if not parsed:
        return "-"
    return parsed.strftime("%d %b %Y")


@app.template_filter("datetime_label")
def datetime_label(value):
    if not value:
        return "-"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value
    return parsed.strftime("%d %b %Y %H:%M")


@app.context_processor
def inject_globals():
    workspace = load_workspace()
    sidebar_projects = compute_project_metrics(workspace["projects"], workspace["actions"])
    sidebar_summary = {
        "total_projects": len(sidebar_projects),
        "active_projects": len(
            [project for project in sidebar_projects if project.get("project_status") not in {"Completed", "Cancelled"}]
        ),
        "at_risk_projects": len([project for project in sidebar_projects if project.get("is_at_risk")]),
        "overdue_actions": sum(project.get("overdue_count", 0) for project in sidebar_projects),
        "upcoming_actions": sum(project.get("upcoming_count", 0) for project in sidebar_projects),
    }
    return {
        "today_date": date.today(),
        "action_status_options": ACTION_STATUS_OPTIONS,
        "priority_options": PRIORITY_OPTIONS,
        "sort_options": SORT_OPTIONS,
        "board_columns": BOARD_COLUMNS,
        "workspace_name": WORKSPACE_NAME,
        "space_name": SPACE_NAME,
        "sidebar_projects": sidebar_projects,
        "sidebar_summary": sidebar_summary,
    }


@app.route("/")
def home():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    workspace, computed_projects = build_workspace_view()
    dashboard_data = build_dashboard_data(computed_projects)
    return render_template(
        "dashboard/index.html",
        page_title="Dashboard",
        page_intro="A CRM-style monitoring dashboard for project health, action ownership, deadlines, and delivery risk.",
        page_key="dashboard",
        dashboard=dashboard_data,
        project_count=len(computed_projects),
    )


@app.get("/healthz")
def healthcheck():
    try:
        storage = repository.healthcheck()
    except Exception as exc:  # pragma: no cover - defensive operational path
        return (
            jsonify(
                {
                    "ok": False,
                    "app_env": app.config["APP_ENV"],
                    "status": "unhealthy",
                    "error": str(exc),
                    "timestamp": now_iso(),
                }
            ),
            503,
        )

    return jsonify(
        {
            "ok": True,
            "app_env": app.config["APP_ENV"],
            "status": "healthy",
            "storage": storage,
            "timestamp": now_iso(),
        }
    )


def render_project_view(template_name, current_view):
    _, computed_projects = build_workspace_view()
    filters = build_filters()
    filtered_projects = filter_projects(computed_projects, filters)
    filter_options = compute_filter_options(computed_projects)
    board_groups = compute_action_status_groups(filtered_projects)
    gantt = compute_gantt_data(filtered_projects)

    return render_template(
        template_name,
        page_title="Client Projects",
        page_intro="Manage project and action data from one shared workspace with list, table, board, and gantt views.",
        page_key="projects",
        current_view=current_view,
        projects=filtered_projects,
        filters=filters,
        filter_options=filter_options,
        board_groups=board_groups,
        gantt=gantt,
    )


@app.route("/projects")
@app.route("/projects/table")
def projects_table():
    return render_project_view("projects/table.html", "table")


@app.route("/projects/list")
def projects_list():
    return render_project_view("projects/list.html", "list")


@app.route("/projects/board")
def projects_board():
    return render_project_view("projects/board.html", "board")


@app.route("/projects/gantt")
def projects_gantt():
    return render_project_view("projects/gantt.html", "gantt")


@app.route("/projects/<project_id>")
def project_detail(project_id):
    workspace, computed_projects = build_workspace_view()
    project = next((item for item in computed_projects if item["id"] == project_id), None)
    if not project:
        abort(404)

    activity_logs = sorted(
        [item for item in workspace["activity_logs"] if item["project_id"] == project_id],
        key=lambda item: item.get("updated_at", ""),
        reverse=True,
    )

    return render_template(
        "projects/detail.html",
        page_title=project["project_name"],
        page_intro="Project summary, action tracking, and audit history for this client delivery stream.",
        page_key="projects",
        project=project,
        activity_logs=activity_logs,
    )


@app.route("/projects/new", methods=["GET", "POST"])
def new_project():
    if request.method == "POST":
        projects, actions, comments, activity_logs = repository.load_workspace_values()
        payload = build_project_payload(request.form)
        errors = validate_project_payload(payload)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "projects/project_form.html",
                page_title="Create Project",
                page_intro="Capture the main project information before you start adding actions.",
                page_key="projects",
                form_mode="create",
                form_action=url_for("new_project"),
                project=payload,
            )

        timestamp = now_iso()
        project = {
            "id": repository.new_id("project"),
            **payload,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        projects.append(project)
        activity_logs.insert(
            0,
            build_creation_log(
                project_id=project["id"],
                action_id="",
                field_name="project_created",
                new_value=project["project_name"],
                updated_by=current_actor(),
                comment=f"Created project {project['project_name']}.",
            ),
        )
        save_workspace(projects, actions, comments, activity_logs)
        flash("Project created.", "success")
        return redirect(url_for("project_detail", project_id=project["id"]))

    return render_template(
        "projects/project_form.html",
        page_title="Create Project",
        page_intro="Capture the main project information before you start adding actions.",
        page_key="projects",
        form_mode="create",
        form_action=url_for("new_project"),
        project=project_form_defaults(),
    )


@app.route("/projects/<project_id>/edit", methods=["GET", "POST"])
def edit_project(project_id):
    projects, actions, comments, activity_logs = repository.load_workspace_values()
    existing = next((item for item in projects if item["id"] == project_id), None)
    if not existing:
        abort(404)

    if request.method == "POST":
        payload = build_project_payload(request.form)
        errors = validate_project_payload(payload)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "projects/project_form.html",
                page_title="Edit Project",
                page_intro="Update project information without changing the action history.",
                page_key="projects",
                form_mode="edit",
                form_action=url_for("edit_project", project_id=project_id),
                project=payload,
            )

        updated = {**existing, **payload, "updated_at": now_iso()}
        logs = build_field_change_logs(
            before=existing,
            after=updated,
            tracked_fields=[
                "service_name",
                "project_name",
                "client_name",
                "priority",
                "owner",
                "start_date",
                "due_date",
                "contact_number",
                "remark",
            ],
            project_id=project_id,
            action_id="",
            updated_by=current_actor(),
        )
        for index, project in enumerate(projects):
            if project["id"] == project_id:
                projects[index] = updated
                break
        activity_logs = logs + activity_logs
        save_workspace(projects, actions, comments, activity_logs)
        flash("Project updated.", "success")
        return redirect(url_for("project_detail", project_id=project_id))

    return render_template(
        "projects/project_form.html",
        page_title="Edit Project",
        page_intro="Update project information without changing the action history.",
        page_key="projects",
        form_mode="edit",
        form_action=url_for("edit_project", project_id=project_id),
        project=project_form_defaults(existing),
    )


@app.route("/projects/<project_id>/actions/new", methods=["GET", "POST"])
def new_action(project_id):
    projects, actions, comments, activity_logs = repository.load_workspace_values()
    project = next((item for item in projects if item["id"] == project_id), None)
    if not project:
        abort(404)

    before_metrics = compute_project_metrics(projects, actions)
    before_project = next(item for item in before_metrics if item["id"] == project_id)

    if request.method == "POST":
        payload = build_action_payload(request.form)
        errors = validate_action_payload(payload)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "projects/action_form.html",
                page_title="Add Action",
                page_intro="Actions drive project progress, risk, and activity logs.",
                page_key="projects",
                form_mode="create",
                form_action=url_for("new_action", project_id=project_id),
                action=payload,
                project=project,
                projects=projects,
            )

        timestamp = now_iso()
        action = {
            "id": repository.new_id("action"),
            **payload,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        actions.append(action)
        target_project_id = action["project_id"]
        target_project = next(item for item in projects if item["id"] == target_project_id)
        before_target_project = next(item for item in before_metrics if item["id"] == target_project_id)
        activity_logs.insert(
            0,
            build_creation_log(
                project_id=target_project_id,
                action_id=action["id"],
                field_name="action_created",
                new_value=action["action_name"],
                updated_by=current_actor(),
                comment=f"Added action {action['action_name']} under {target_project['project_name']}.",
            ),
        )

        after_metrics = compute_project_metrics(projects, actions)
        after_project = next(item for item in after_metrics if item["id"] == target_project_id)
        activity_logs = build_rollup_logs(before_target_project, after_project, target_project_id, current_actor()) + activity_logs
        save_workspace(projects, actions, comments, activity_logs)
        flash("Action created.", "success")
        return redirect(url_for("project_detail", project_id=target_project_id))

    return render_template(
        "projects/action_form.html",
        page_title="Add Action",
        page_intro="Actions drive project progress, risk, and activity logs.",
        page_key="projects",
        form_mode="create",
        form_action=url_for("new_action", project_id=project_id),
        action=action_form_defaults(project_id=project_id),
        project=project,
        projects=projects,
    )


@app.route("/actions/<action_id>/edit", methods=["GET", "POST"])
def edit_action(action_id):
    projects, actions, comments, activity_logs = repository.load_workspace_values()
    existing = next((item for item in actions if item["id"] == action_id), None)
    if not existing:
        abort(404)

    old_project_id = existing["project_id"]
    project = next((item for item in projects if item["id"] == old_project_id), None)
    if not project:
        abort(404)

    before_metrics = compute_project_metrics(projects, actions)
    before_project = next(item for item in before_metrics if item["id"] == old_project_id)

    if request.method == "POST":
        payload = build_action_payload(request.form)
        errors = validate_action_payload(payload)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "projects/action_form.html",
                page_title="Edit Action",
                page_intro="Update an action and automatically recalculate project status and progress.",
                page_key="projects",
                form_mode="edit",
                form_action=url_for("edit_action", action_id=action_id),
                action=payload,
                project=project,
                projects=projects,
            )

        updated = {**existing, **payload, "updated_at": now_iso()}
        new_project_id = updated["project_id"]
        logs = build_field_change_logs(
            before=existing,
            after=updated,
            tracked_fields=[
                "action_name",
                "description",
                "action_status",
                "priority",
                "assignee",
                "start_date",
                "due_date",
                "progress_percent",
                "remark",
            ],
            project_id=new_project_id,
            action_id=action_id,
            updated_by=current_actor(),
        )

        for index, action_item in enumerate(actions):
            if action_item["id"] == action_id:
                actions[index] = updated
                break

        after_metrics = compute_project_metrics(projects, actions)
        rollup_logs = []
        if old_project_id == new_project_id:
            after_project = next(item for item in after_metrics if item["id"] == old_project_id)
            rollup_logs.extend(build_rollup_logs(before_project, after_project, old_project_id, current_actor()))
        else:
            after_old_project = next(item for item in after_metrics if item["id"] == old_project_id)
            before_new_project = next(item for item in before_metrics if item["id"] == new_project_id)
            after_new_project = next(item for item in after_metrics if item["id"] == new_project_id)
            rollup_logs.extend(build_rollup_logs(before_project, after_old_project, old_project_id, current_actor()))
            rollup_logs.extend(build_rollup_logs(before_new_project, after_new_project, new_project_id, current_actor()))

        activity_logs = logs + rollup_logs + activity_logs
        save_workspace(projects, actions, comments, activity_logs)
        flash("Action updated.", "success")
        return redirect(url_for("project_detail", project_id=new_project_id))

    return render_template(
        "projects/action_form.html",
        page_title="Edit Action",
        page_intro="Update an action and automatically recalculate project status and progress.",
        page_key="projects",
        form_mode="edit",
        form_action=url_for("edit_action", action_id=action_id),
        action=action_form_defaults(existing=existing),
        project=project,
        projects=projects,
    )


@app.route("/actions/<action_id>/status", methods=["POST"])
def update_action_status(action_id):
    projects, actions, comments, activity_logs = repository.load_workspace_values()
    existing = next((item for item in actions if item["id"] == action_id), None)
    if not existing:
        abort(404)

    payload = request.get_json(silent=True) if request.is_json else request.form
    payload = payload or {}
    new_status = str(payload.get("action_status") or payload.get("status") or "").strip()

    if new_status not in BOARD_COLUMNS:
        return jsonify({"ok": False, "message": "Unsupported board status."}), 400

    if new_status == existing.get("action_status"):
        return jsonify(
            {
                "ok": True,
                "action_id": action_id,
                "action_status": new_status,
                "message": "No status change needed.",
            }
        )

    project_id = existing["project_id"]
    before_metrics = compute_project_metrics(projects, actions)
    before_project = next(item for item in before_metrics if item["id"] == project_id)
    updated = {**existing, "action_status": new_status, "updated_at": now_iso()}

    logs = build_field_change_logs(
        before=existing,
        after=updated,
        tracked_fields=["action_status"],
        project_id=project_id,
        action_id=action_id,
        updated_by=current_actor(),
    )

    for index, action_item in enumerate(actions):
        if action_item["id"] == action_id:
            actions[index] = updated
            break

    after_metrics = compute_project_metrics(projects, actions)
    after_project = next(item for item in after_metrics if item["id"] == project_id)
    rollup_logs = build_rollup_logs(before_project, after_project, project_id, current_actor())
    activity_logs = logs + rollup_logs + activity_logs
    save_workspace(projects, actions, comments, activity_logs)

    return jsonify(
        {
            "ok": True,
            "action_id": action_id,
            "action_status": new_status,
            "project_id": project_id,
            "project_status": after_project.get("project_status"),
            "project_progress": after_project.get("progress_percent"),
        }
    )


@app.route("/actions/<action_id>/delete", methods=["POST"])
def delete_action(action_id):
    projects, actions, comments, activity_logs = repository.load_workspace_values()
    existing = next((item for item in actions if item["id"] == action_id), None)
    if not existing:
        abort(404)

    project_id = existing["project_id"]
    before_metrics = compute_project_metrics(projects, actions)
    before_project = next(item for item in before_metrics if item["id"] == project_id)

    actions = [item for item in actions if item["id"] != action_id]
    activity_logs.insert(
        0,
        build_deletion_log(
            project_id=project_id,
            action_id=action_id,
            field_name="action_deleted",
            old_value=existing["action_name"],
            updated_by=current_actor(),
            comment=f"Deleted action {existing['action_name']}.",
        ),
    )

    after_metrics = compute_project_metrics(projects, actions)
    after_project = next(item for item in after_metrics if item["id"] == project_id)
    activity_logs = build_rollup_logs(before_project, after_project, project_id, current_actor()) + activity_logs
    save_workspace(projects, actions, comments, activity_logs)
    flash("Action deleted.", "success")
    return redirect(url_for("project_detail", project_id=project_id))

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=app.config["DEBUG"],
    )

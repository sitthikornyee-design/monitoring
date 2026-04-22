import csv
import io
import os
import sqlite3
from calendar import monthrange
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, Response, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "local-monitoring-workspace-v2"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PROJECT_DATABASE_PATH = DATA_DIR / "monitoring.db"
LOCALAPPDATA_DIR = Path(os.environ.get("LOCALAPPDATA", BASE_DIR))
FALLBACK_DATABASE_PATH = LOCALAPPDATA_DIR / "Monitoring Workspace" / "monitoring.db"
DATABASE_PATH = PROJECT_DATABASE_PATH
SCHEMA_PATH = BASE_DIR / "schema.sql"
DEFAULT_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    kpi_category TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'start',
    priority TEXT NOT NULL DEFAULT 'Medium',
    assignee TEXT,
    owner TEXT,
    contact_number TEXT,
    department TEXT,
    progress_percent TEXT,
    tags TEXT,
    stage TEXT,
    due_date TEXT,
    next_step TEXT,
    issue TEXT,
    current_status TEXT,
    last_update TEXT,
    internal_action TEXT,
    client_feedback TEXT,
    company_name TEXT,
    requested_date TEXT,
    industry TEXT,
    x_number_total TEXT,
    x_number_range TEXT,
    business_scenario TEXT,
    fit_level TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);
CREATE INDEX IF NOT EXISTS idx_tasks_kpi_category ON tasks (kpi_category);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks (due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks (updated_at);

CREATE TABLE IF NOT EXISTS timeline_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    update_title TEXT,
    update_type TEXT,
    priority TEXT,
    description TEXT,
    related_status TEXT,
    created_by TEXT,
    attachment_url TEXT,
    stage_label TEXT NOT NULL,
    status_label TEXT NOT NULL,
    update_note TEXT NOT NULL,
    start_date TEXT,
    due_date TEXT,
    update_date TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_timeline_updates_task_id ON timeline_updates (task_id);
CREATE INDEX IF NOT EXISTS idx_timeline_updates_created_at ON timeline_updates (created_at);
"""

MONITORING_MODULES = [
    {
        "slug": "virtual-phone",
        "name": "Virtual Phone Management",
        "short_name": "Virtual Phone",
        "weight": 30,
        "description": "Track customer rollout, X number assignment, testing progress, issue resolution, and launch readiness for Virtual Phone projects.",
        "db_values": ["Virtual Phone Management", "J&T Follow-up"],
        "main_fields": [
            "Customer name",
            "Project name",
            "Service type",
            "Assigned number owner",
            "Current stage",
            "Target go-live date",
        ],
        "sub_sections": [
            "Project Overview",
            "X Number Assignment",
            "Testing Progress",
            "Issue Tracking",
            "Summary Report",
        ],
        "recommended_views": ["Summary cards", "Project table", "Issue list", "Timeline"],
    },
    {
        "slug": "one-click-login",
        "name": "One-Click Login Management",
        "short_name": "One-Click Login",
        "weight": 25,
        "description": "Monitor platform integration, SDK or API readiness, testing outcomes, blockers, and go-live recommendations for One-Click Login work.",
        "db_values": ["One-Click Login Management"],
        "main_fields": [
            "Customer name",
            "App or platform name",
            "Platform type",
            "API or SDK version",
            "Environment",
            "Target go-live date",
        ],
        "sub_sections": [
            "Integration Details",
            "Testing Progress",
            "Issue Tracking",
            "Launch Readiness Summary",
        ],
        "recommended_views": ["Summary cards", "Integration table", "Testing progress", "Launch checklist"],
    },
    {
        "slug": "customer-pipeline",
        "name": "Customer Pipeline",
        "short_name": "Pipeline",
        "weight": 20,
        "description": "Track opportunities from lead to go-live, keep the next action clear, and give business teams a simple pipeline view.",
        "db_values": ["Customer Pipeline", "Lead Development"],
        "main_fields": [
            "Customer name",
            "Industry",
            "Interested product",
            "Current stage",
            "Next action",
            "Probability",
        ],
        "sub_sections": [
            "Kanban Pipeline View",
            "Table View",
            "Opportunity Detail Page",
        ],
        "recommended_views": ["Kanban board", "Pipeline table", "Opportunity detail"],
    },
    {
        "slug": "business-support",
        "name": "Business Support",
        "short_name": "Support",
        "weight": 25,
        "description": "Manage support tickets, issue ownership, severity, workaround tracking, and final resolution across business support work.",
        "db_values": ["Business Support"],
        "main_fields": [
            "Ticket ID",
            "Customer name",
            "Product",
            "Severity",
            "Status",
            "Target resolution date",
        ],
        "sub_sections": [
            "Issue Intake",
            "Investigation",
            "Fixing and Retesting",
            "Customer Confirmation",
            "Closure and Lesson Learned",
        ],
        "recommended_views": ["Ticket queue", "Severity table", "Resolution status", "Activity log"],
    },
]

MODULE_LOOKUP_BY_SLUG = {item["slug"]: item for item in MONITORING_MODULES}
MODULE_LOOKUP_BY_NAME = {item["name"]: item for item in MONITORING_MODULES}

MODULE_NAME_ALIASES = {}
MODULE_DATABASE_VALUES = {}
for module in MONITORING_MODULES:
    MODULE_DATABASE_VALUES[module["name"]] = module["db_values"]
    for value in module["db_values"]:
        MODULE_NAME_ALIASES[value] = module["name"]

KPI_CATEGORIES = [
    {
        "name": module["name"],
        "label": module["short_name"],
        "weight": module["weight"],
        "description": module["description"],
    }
    for module in MONITORING_MODULES
]
KPI_LOOKUP = {item["name"]: item for item in KPI_CATEGORIES}

STATUS_OPTIONS = ["start", "in_progress", "complete", "blocked"]
STATUS_LABELS = {
    "start": "Start",
    "in_progress": "In Progress",
    "complete": "Complete",
    "blocked": "Blocked",
}
STATUS_CHOICES = [{"value": value, "label": label} for value, label in STATUS_LABELS.items()]
PRIORITY_OPTIONS = ["Low", "Medium", "High", "Urgent"]
FIT_LEVEL_OPTIONS = ["Low", "Medium", "High", "Strategic"]
TIMELINE_STATUS_OPTIONS = STATUS_OPTIONS

STANDARD_PROJECT_STAGES = [
    "Requirement Gathering",
    "Solution Discussion",
    "Technical Alignment",
    "Sandbox Setup",
    "Internal Testing",
    "Customer Testing / UAT",
    "Issue Fixing",
    "Retesting",
    "Go-Live Preparation",
    "Production Launch",
    "Post-Launch Monitoring",
]

PIPELINE_STAGES = [
    "Lead",
    "Contacted",
    "Qualified",
    "Meeting Scheduled",
    "Requirement Discussion",
    "Solution Proposed",
    "Commercial Discussion",
    "POC / Testing",
    "Negotiation",
    "Won",
    "Lost",
    "On Hold",
]

SUPPORT_TICKET_STATUSES = [
    "New",
    "Investigating",
    "Waiting for Customer",
    "Waiting for Partner",
    "Fixing",
    "Retesting",
    "Resolved",
    "Closed",
]

SEVERITY_LEVELS = ["S1 Critical", "S2 High", "S3 Medium", "S4 Low", "Feature Request"]

UPDATE_TYPE_OPTIONS = [
    "Created",
    "Progress",
    "Issue",
    "Note",
    "Risk",
    "Delay",
    "Follow-up",
    "Decision",
    "Testing Result",
    "Customer Feedback",
    "Support Response",
]

CORE_USERS = [
    {
        "title": "Business / Sales Team",
        "description": "Track customer status, pipeline movement, next actions, and business support cases.",
    },
    {
        "title": "Project Manager / BD Owner",
        "description": "Coordinate responsibilities, review blockers, and keep projects moving between teams.",
    },
    {
        "title": "Technical Team",
        "description": "Update testing progress, fix issues, confirm root causes, and validate launch readiness.",
    },
    {
        "title": "Management",
        "description": "Monitor overall project status, urgent issues, and delivery health through summary views.",
    },
]

ALERT_SUGGESTIONS = [
    "New issue created",
    "Critical issue created",
    "Project delayed",
    "Target go-live date approaching",
    "Ticket unresolved beyond SLA",
    "Testing stage not updated for too long",
    "Number allocation running low",
]

PERMISSION_GROUPS = [
    {"title": "Admin", "description": "Full access across monitoring modules, projects, and configuration."},
    {"title": "Business / Sales", "description": "Pipeline, customer information, and project update access."},
    {"title": "Project Manager", "description": "Cross-team coordination, project stage tracking, and reporting."},
    {"title": "Technical Team", "description": "Testing, issue updates, and support case management."},
    {"title": "Viewer / Management", "description": "Read-only dashboard and report access."},
]

REPORT_TYPES = [
    "Virtual Phone project summary",
    "One-Click Login project summary",
    "Open issues summary",
    "Business support case summary",
    "Customer pipeline summary",
    "Monthly progress report",
]

EXPORT_OPTIONS = ["PDF", "Excel", "CSV"]

MVP_FEATURES = [
    "Dashboard summary",
    "Virtual Phone tracking",
    "One-Click Login tracking",
    "Customer pipeline tracking",
    "Business support ticket tracking",
    "Basic reports",
    "Search and filter",
]

TASK_FIELDS = [
    "title",
    "description",
    "kpi_category",
    "status",
    "priority",
    "assignee",
    "owner",
    "contact_number",
    "department",
    "progress_percent",
    "tags",
    "stage",
    "due_date",
    "next_step",
    "issue",
    "current_status",
    "last_update",
    "internal_action",
    "client_feedback",
    "company_name",
    "requested_date",
    "industry",
    "x_number_total",
    "x_number_range",
    "business_scenario",
    "fit_level",
]

OPTIONAL_TASK_COLUMNS = {
    "requested_date": "TEXT",
    "x_number_total": "TEXT",
    "x_number_range": "TEXT",
    "assignee": "TEXT",
    "contact_number": "TEXT",
    "department": "TEXT",
    "progress_percent": "TEXT",
    "tags": "TEXT",
    "stage": "TEXT",
}

OPTIONAL_TIMELINE_UPDATE_COLUMNS = {
    "update_title": "TEXT",
    "update_type": "TEXT",
    "priority": "TEXT",
    "description": "TEXT",
    "related_status": "TEXT",
    "created_by": "TEXT",
    "attachment_url": "TEXT",
    "start_date": "TEXT",
    "due_date": "TEXT",
}


def current_timestamp():
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def clean_text(value):
    return (value or "").strip()


def normalize_project_status(value, fallback=None):
    normalized = clean_text(value).lower().replace("-", " ").replace("_", " ")
    status_map = {
        "start": "start",
        "to do": "start",
        "todo": "start",
        "not started": "start",
        "in progress": "in_progress",
        "complete": "complete",
        "completed": "complete",
        "blocked": "blocked",
    }

    if normalized in status_map:
        return status_map[normalized]

    if fallback is not None:
        return fallback

    return STATUS_OPTIONS[0]


def project_status_label(value):
    return STATUS_LABELS.get(normalize_project_status(value), STATUS_LABELS[STATUS_OPTIONS[0]])


def normalize_percentage(value):
    cleaned = clean_text(value)
    if not cleaned:
        return ""

    try:
        numeric_value = float(cleaned)
    except ValueError:
        return cleaned

    numeric_value = max(0.0, min(100.0, numeric_value))
    if numeric_value.is_integer():
        return str(int(numeric_value))

    return f"{numeric_value:.1f}".rstrip("0").rstrip(".")


def split_tags(value):
    return [tag.strip() for tag in clean_text(value).split(",") if tag.strip()]


def slugify(value):
    cleaned = []
    previous_dash = False

    for character in (value or "").lower():
        if character.isalnum():
            cleaned.append(character)
            previous_dash = False
        elif not previous_dash:
            cleaned.append("-")
            previous_dash = True

    return "".join(cleaned).strip("-")


@app.template_filter("slugify")
def slugify_filter(value):
    return slugify(value)


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_datetime(value):
    if not value:
        return None

    normalized = value.replace("T", " ")

    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def normalize_module_name(value):
    cleaned_value = clean_text(value)
    return MODULE_NAME_ALIASES.get(cleaned_value, cleaned_value)


def get_module(module_slug):
    return MODULE_LOOKUP_BY_SLUG.get(module_slug)


def open_database_connection(database_path):
    database_path.parent.mkdir(parents=True, exist_ok=True)
    database_path.touch(exist_ok=True)

    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode = MEMORY")
    connection.execute("PRAGMA synchronous = OFF")
    return connection


def load_schema_sql():
    if SCHEMA_PATH.exists():
        return SCHEMA_PATH.read_text(encoding="utf-8")

    return DEFAULT_SCHEMA_SQL


def init_db():
    global DATABASE_PATH

    schema_sql = load_schema_sql()
    configured_path = clean_text(os.environ.get("KPI_MONITOR_DB_PATH"))

    database_candidates = [Path(configured_path)] if configured_path else [
        PROJECT_DATABASE_PATH,
        FALLBACK_DATABASE_PATH,
    ]

    last_error = None

    for candidate in database_candidates:
        try:
            with open_database_connection(candidate) as connection:
                connection.executescript(schema_sql)
                ensure_optional_task_columns(connection)
                ensure_optional_timeline_update_columns(connection)
                connection.commit()
            DATABASE_PATH = candidate
            return
        except (sqlite3.Error, OSError) as error:
            last_error = error

    raise RuntimeError(f"Unable to initialize SQLite database: {last_error}")


def ensure_optional_task_columns(connection):
    existing_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(tasks)").fetchall()
    }

    for column_name, column_type in OPTIONAL_TASK_COLUMNS.items():
        if column_name in existing_columns:
            continue
        connection.execute(f"ALTER TABLE tasks ADD COLUMN {column_name} {column_type}")


def ensure_optional_timeline_update_columns(connection):
    existing_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(timeline_updates)").fetchall()
    }

    for column_name, column_type in OPTIONAL_TIMELINE_UPDATE_COLUMNS.items():
        if column_name in existing_columns:
            continue
        connection.execute(f"ALTER TABLE timeline_updates ADD COLUMN {column_name} {column_type}")


def get_db_connection():
    return open_database_connection(DATABASE_PATH)


def build_task_form_data(existing_task=None, form_data=None, default_status=None, default_category=None):
    task_data = {}

    for field_name in TASK_FIELDS:
        if form_data is not None and field_name in form_data:
            task_data[field_name] = clean_text(form_data.get(field_name))
        elif existing_task is not None:
            task_data[field_name] = clean_text(existing_task.get(field_name))
        else:
            task_data[field_name] = ""

    task_data["status"] = normalize_project_status(task_data.get("status"), default_status or STATUS_OPTIONS[0])

    if not task_data["priority"] or task_data["priority"] not in PRIORITY_OPTIONS:
        task_data["priority"] = "Medium"

    normalized_category = normalize_module_name(task_data["kpi_category"])
    if normalized_category not in KPI_LOOKUP:
        normalized_category = default_category or KPI_CATEGORIES[0]["name"]
    task_data["kpi_category"] = normalized_category

    if task_data["fit_level"] and task_data["fit_level"] not in FIT_LEVEL_OPTIONS:
        task_data["fit_level"] = ""

    task_data["progress_percent"] = normalize_percentage(task_data.get("progress_percent"))

    return task_data


def validate_task_form(task_data):
    errors = []

    if not task_data["title"]:
        errors.append("Project or ticket title is required.")

    if task_data["kpi_category"] not in KPI_LOOKUP:
        errors.append("Please choose a valid service.")

    if normalize_project_status(task_data["status"]) not in STATUS_OPTIONS:
        errors.append("Please choose a valid overall status.")

    if task_data["priority"] not in PRIORITY_OPTIONS:
        errors.append("Please choose a valid priority.")

    progress_percent = clean_text(task_data.get("progress_percent"))
    if progress_percent:
        try:
            numeric_progress = float(progress_percent)
        except ValueError:
            errors.append("Progress percent must be a number between 0 and 100.")
        else:
            if numeric_progress < 0 or numeric_progress > 100:
                errors.append("Progress percent must stay between 0 and 100.")

    start_date = parse_date(task_data.get("requested_date"))
    due_date = parse_date(task_data.get("due_date"))
    if task_data.get("requested_date") and not start_date:
        errors.append("Please provide a valid start date.")

    if task_data.get("due_date") and not due_date:
        errors.append("Please provide a valid due date.")

    if start_date and due_date and due_date < start_date:
        errors.append("Due date must be on or after the start date.")

    return errors


def build_project_creation_update(task_data, created_timestamp):
    created_date = created_timestamp.split(" ")[0]
    project_status = normalize_project_status(task_data.get("status"))
    description = clean_text(task_data.get("description")) or "Project created and ready for processing updates."

    return {
        "update_title": "Project created",
        "update_type": "Created",
        "priority": clean_text(task_data.get("priority")) or "Medium",
        "related_status": project_status,
        "status_label": project_status,
        "description": description,
        "created_by": clean_text(task_data.get("owner")) or clean_text(task_data.get("assignee")) or "System",
        "start_date": clean_text(task_data.get("requested_date")) or created_date,
        "due_date": clean_text(task_data.get("due_date")),
        "update_date": clean_text(task_data.get("requested_date")) or created_date,
        "attachment_url": "",
    }


def insert_timeline_update_row(connection, task_id, update_data, created_at):
    connection.execute(
        """
        INSERT INTO timeline_updates (
            task_id,
            update_title,
            update_type,
            priority,
            description,
            related_status,
            created_by,
            attachment_url,
            stage_label,
            status_label,
            update_note,
            start_date,
            due_date,
            update_date,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_id,
            update_data["update_title"],
            update_data["update_type"],
            update_data.get("priority") or "Medium",
            update_data["description"],
            update_data["related_status"],
            update_data["created_by"],
            update_data["attachment_url"],
            update_data["related_status"],
            update_data["status_label"],
            update_data["description"],
            update_data.get("start_date") or None,
            update_data.get("due_date") or None,
            update_data["update_date"] or None,
            created_at,
        ),
    )


def create_task(task_data):
    now = current_timestamp()

    with get_db_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (
                title,
                description,
                kpi_category,
                status,
                priority,
                assignee,
                owner,
                contact_number,
                department,
                progress_percent,
                tags,
                stage,
                due_date,
                next_step,
                issue,
                current_status,
                last_update,
                internal_action,
                client_feedback,
                company_name,
                requested_date,
                industry,
                x_number_total,
                x_number_range,
                business_scenario,
                fit_level,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_data["title"],
                task_data["description"],
                task_data["kpi_category"],
                normalize_project_status(task_data["status"]),
                task_data["priority"],
                task_data["assignee"],
                task_data["owner"],
                task_data["contact_number"],
                task_data["department"],
                task_data["progress_percent"],
                task_data["tags"],
                task_data["stage"],
                task_data["due_date"] or None,
                task_data["next_step"],
                task_data["issue"],
                task_data["current_status"],
                task_data["last_update"],
                task_data["internal_action"],
                task_data["client_feedback"],
                task_data["company_name"],
                task_data["requested_date"] or None,
                task_data["industry"],
                task_data["x_number_total"],
                task_data["x_number_range"],
                task_data["business_scenario"],
                task_data["fit_level"],
                now,
                now,
            ),
        )
        task_id = cursor.lastrowid
        creation_update = build_project_creation_update(task_data, now)
        insert_timeline_update_row(connection, task_id, creation_update, now)
        connection.commit()
        return task_id


def update_task(task_id, task_data):
    now = current_timestamp()

    with get_db_connection() as connection:
        connection.execute(
            """
            UPDATE tasks
            SET
                title = ?,
                description = ?,
                kpi_category = ?,
                status = ?,
                priority = ?,
                assignee = ?,
                owner = ?,
                contact_number = ?,
                department = ?,
                progress_percent = ?,
                tags = ?,
                stage = ?,
                due_date = ?,
                next_step = ?,
                issue = ?,
                current_status = ?,
                last_update = ?,
                internal_action = ?,
                client_feedback = ?,
                company_name = ?,
                requested_date = ?,
                industry = ?,
                x_number_total = ?,
                x_number_range = ?,
                business_scenario = ?,
                fit_level = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                task_data["title"],
                task_data["description"],
                task_data["kpi_category"],
                normalize_project_status(task_data["status"]),
                task_data["priority"],
                task_data["assignee"],
                task_data["owner"],
                task_data["contact_number"],
                task_data["department"],
                task_data["progress_percent"],
                task_data["tags"],
                task_data["stage"],
                task_data["due_date"] or None,
                task_data["next_step"],
                task_data["issue"],
                task_data["current_status"],
                task_data["last_update"],
                task_data["internal_action"],
                task_data["client_feedback"],
                task_data["company_name"],
                task_data["requested_date"] or None,
                task_data["industry"],
                task_data["x_number_total"],
                task_data["x_number_range"],
                task_data["business_scenario"],
                task_data["fit_level"],
                now,
                task_id,
            ),
        )
        connection.commit()


def delete_task(task_id):
    with get_db_connection() as connection:
        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        connection.commit()


def build_timeline_update_data(form_data=None, task=None):
    form_data = form_data or {}
    task = task or {}
    update_status = normalize_project_status(
        form_data.get("status_label") or form_data.get("status") or task.get("status"),
        task.get("status") or STATUS_OPTIONS[0],
    )
    note = clean_text(form_data.get("note")) or clean_text(form_data.get("description")) or clean_text(form_data.get("update_note"))
    start_date = clean_text(form_data.get("start_date"))
    due_date = clean_text(form_data.get("due_date"))

    return {
        "status": update_status,
        "note": note,
        "priority": clean_text(form_data.get("priority")) or clean_text(task.get("priority")) or "Medium",
        "start_date": start_date,
        "due_date": due_date,
        "update_title": clean_text(form_data.get("update_title")) or f"{project_status_label(update_status)} update",
        "update_type": clean_text(form_data.get("update_type")) or "Progress",
        "related_status": update_status,
        "status_label": update_status,
        "description": note,
        "created_by": clean_text(form_data.get("created_by")) or clean_text(task.get("owner")) or clean_text(task.get("assignee")),
        "update_date": start_date or due_date or date.today().isoformat(),
        "attachment_url": clean_text(form_data.get("attachment_url")),
    }


def validate_timeline_update(update_data):
    errors = []

    if update_data["status"] not in TIMELINE_STATUS_OPTIONS:
        errors.append("Please choose a valid project status for the timeline update.")

    if update_data["priority"] not in PRIORITY_OPTIONS:
        errors.append("Please choose a valid priority.")

    if not update_data["note"]:
        errors.append("Please add the update note.")

    if update_data["start_date"] and not parse_date(update_data["start_date"]):
        errors.append("Please provide a valid processing start date.")

    if update_data["due_date"] and not parse_date(update_data["due_date"]):
        errors.append("Please provide a valid processing due date.")

    if (
        update_data["start_date"]
        and update_data["due_date"]
        and parse_date(update_data["start_date"])
        and parse_date(update_data["due_date"])
        and parse_date(update_data["due_date"]) < parse_date(update_data["start_date"])
    ):
        errors.append("Processing due date must be on or after the processing start date.")

    if update_data["update_date"] and not parse_date(update_data["update_date"]):
        errors.append("Please provide a valid update date.")

    return errors


def create_timeline_update(task_id, update_data):
    now = current_timestamp()

    with get_db_connection() as connection:
        insert_timeline_update_row(connection, task_id, update_data, now)

        connection.execute(
            """
            UPDATE tasks
            SET
                status = ?,
                stage = ?,
                current_status = ?,
                last_update = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                normalize_project_status(update_data["status"]),
                project_status_label(update_data["status"]),
                project_status_label(update_data["status"]),
                update_data["note"],
                now,
                task_id,
            ),
        )
        connection.commit()


def decorate_timeline_updates(rows):
    updates = []
    update_counter = 0

    for row in rows:
        item = dict(row)
        parsed_update_date = parse_date(item.get("update_date"))
        parsed_created_at = parse_datetime(item.get("created_at"))
        parsed_start_date = parse_date(item.get("start_date"))
        parsed_due_date = parse_date(item.get("due_date"))
        canonical_status = normalize_project_status(item.get("status_label") or item.get("related_status"))

        item["status_value"] = canonical_status
        item["status_display"] = project_status_label(canonical_status)
        item["update_title_display"] = clean_text(item.get("update_title")) or f"{item['status_display']} update"
        item["update_type_display"] = clean_text(item.get("update_type")) or "Progress"
        item["priority_display"] = clean_text(item.get("priority")) or "Medium"
        item["note_display"] = clean_text(item.get("description")) or clean_text(item.get("update_note")) or "No update note recorded."
        item["description_display"] = item["note_display"]
        item["related_status_display"] = item["status_display"]
        item["created_by_display"] = clean_text(item.get("created_by")) or "-"
        item["attachment_url_display"] = clean_text(item.get("attachment_url"))
        item["display_start_date"] = parsed_start_date.strftime("%d %b %Y") if parsed_start_date else "-"
        item["display_due_date"] = parsed_due_date.strftime("%d %b %Y") if parsed_due_date else "-"
        item["display_update_date"] = parsed_update_date.strftime("%d %b %Y") if parsed_update_date else "-"
        item["display_created_at"] = parsed_created_at.strftime("%d %b %Y, %I:%M %p") if parsed_created_at else "-"
        item["is_creation_entry"] = item["update_type_display"].lower() == "created" or item["update_title_display"].lower() == "project created"
        if item["is_creation_entry"]:
            item["timeline_entry_label"] = "Project created"
            item["timeline_sequence"] = 0
        else:
            update_counter += 1
            item["timeline_entry_label"] = f"Update {update_counter}"
            item["timeline_sequence"] = update_counter
        updates.append(item)

    return updates


def get_task_timeline_updates(task_id, limit=None):
    with get_db_connection() as connection:
        query = """
            SELECT *
            FROM timeline_updates
            WHERE task_id = ?
            ORDER BY
                CASE WHEN update_date IS NULL OR update_date = '' THEN 1 ELSE 0 END,
                update_date ASC,
                created_at ASC
        """
        parameters = [task_id]
        if limit is not None:
            query += " LIMIT ?"
            parameters.append(limit)

        rows = connection.execute(query, parameters).fetchall()

    return decorate_timeline_updates(rows)


def attach_timeline_update_collections(tasks):
    if not tasks:
        return tasks

    task_ids = [task["id"] for task in tasks]
    placeholders = ", ".join("?" for _ in task_ids)

    with get_db_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT *
            FROM timeline_updates
            WHERE task_id IN ({placeholders})
            ORDER BY
                task_id ASC,
                CASE WHEN update_date IS NULL OR update_date = '' THEN 1 ELSE 0 END,
                update_date ASC,
                created_at ASC
            """,
            task_ids,
        ).fetchall()

    grouped_rows = {}
    for row in rows:
        grouped_rows.setdefault(row["task_id"], []).append(row)

    for task in tasks:
        timeline_updates = decorate_timeline_updates(grouped_rows.get(task["id"], []))
        task["timeline_updates"] = timeline_updates
        task["timeline_update_count"] = len(timeline_updates)
        task["non_creation_timeline_update_count"] = len(
            [update for update in timeline_updates if not update.get("is_creation_entry")]
        )

    return tasks


def attach_timeline_update_summaries(tasks):
    if not tasks:
        return tasks

    task_ids = [task["id"] for task in tasks]
    placeholders = ", ".join("?" for _ in task_ids)

    with get_db_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT tu.*
            FROM timeline_updates tu
            JOIN (
                SELECT task_id, MAX(created_at) AS latest_created_at
                FROM timeline_updates
                WHERE task_id IN ({placeholders})
                GROUP BY task_id
            ) latest
                ON latest.task_id = tu.task_id
               AND latest.latest_created_at = tu.created_at
            """,
            task_ids,
        ).fetchall()

    latest_by_task = {row["task_id"]: dict(row) for row in rows}

    for task in tasks:
        latest = latest_by_task.get(task["id"])
        if not latest:
            task["latest_timeline_update"] = ""
            task["latest_timeline_stage"] = ""
            task["latest_timeline_date"] = ""
            task["latest_timeline_type"] = ""
            task["latest_processing_status"] = ""
            task["latest_processing_priority"] = ""
            task["latest_processing_start_date"] = ""
            task["latest_processing_due_date"] = ""
        else:
            latest_status = normalize_project_status(latest.get("status_label") or latest.get("related_status"))
            update_date = parse_date(latest.get("update_date"))
            latest_start_date = parse_date(latest.get("start_date"))
            latest_due_date = parse_date(latest.get("due_date"))
            task["latest_timeline_update"] = clean_text(latest.get("description")) or clean_text(latest.get("update_note"))
            task["latest_timeline_stage"] = project_status_label(latest_status)
            task["latest_timeline_date"] = update_date.strftime("%d %b %Y") if update_date else ""
            task["latest_timeline_type"] = clean_text(latest.get("update_type"))
            task["latest_processing_status"] = latest_status
            task["latest_processing_priority"] = clean_text(latest.get("priority")) or ""
            task["latest_processing_start_date"] = latest_start_date.strftime("%d %b %Y") if latest_start_date else ""
            task["latest_processing_due_date"] = latest_due_date.strftime("%d %b %Y") if latest_due_date else ""

        task["has_timeline_update"] = bool(task.get("non_creation_timeline_update_count"))
        task["record_status_stage"] = task.get("latest_timeline_stage") or task.get("stage") or task.get("current_status") or task.get("display_stage") or ""
        task["record_status_text"] = task.get("latest_timeline_update") or task.get("update_summary") or "No recent update note."
        task["record_status_meta"] = " | ".join(
            part for part in [task["record_status_stage"], task.get("latest_timeline_date", "")] if part
        )

    return tasks


def build_text_blob(task):
    fields = [
        task.get("title"),
        task.get("description"),
        task.get("stage"),
        task.get("current_status"),
        task.get("last_update"),
        task.get("next_step"),
        task.get("issue"),
        task.get("assignee"),
        task.get("department"),
        task.get("tags"),
        task.get("contact_number"),
        task.get("client_feedback"),
        task.get("business_scenario"),
        task.get("x_number_total"),
        task.get("x_number_range"),
    ]
    return " ".join(clean_text(value).lower() for value in fields if clean_text(value))


def infer_project_stage(task):
    explicit_stage = clean_text(task.get("stage"))
    if explicit_stage:
        return explicit_stage

    text_blob = build_text_blob(task)

    if "post-launch" in text_blob or "post launch" in text_blob or "post-live" in text_blob:
        return "Post-Launch Monitoring"
    if "production launch" in text_blob or "go-live" in text_blob or "go live" in text_blob or "launch" in text_blob:
        return "Production Launch"
    if "go-live preparation" in text_blob or "launch prep" in text_blob or "final approval" in text_blob:
        return "Go-Live Preparation"
    if "retesting" in text_blob or "retest" in text_blob:
        return "Retesting"
    if "issue fixing" in text_blob or "workaround" in text_blob or "blocker" in text_blob:
        return "Issue Fixing"
    if "uat" in text_blob or "customer testing" in text_blob:
        return "Customer Testing / UAT"
    if "internal testing" in text_blob or "functional testing" in text_blob or "testing" in text_blob:
        return "Internal Testing"
    if "sandbox" in text_blob:
        return "Sandbox Setup"
    if "integration" in text_blob or "technical alignment" in text_blob or "sdk" in text_blob or "api" in text_blob:
        return "Technical Alignment"
    if "solution" in text_blob or "commercial" in text_blob or "proposal" in text_blob:
        return "Solution Discussion"
    if "requirement" in text_blob or "discovery" in text_blob or "kickoff" in text_blob:
        return "Requirement Gathering"

    if normalize_project_status(task.get("status")) == "complete":
        return "Production Launch"
    if normalize_project_status(task.get("status")) == "blocked":
        return "Issue Fixing"
    if normalize_project_status(task.get("status")) == "in_progress":
        return "Internal Testing"

    return "Requirement Gathering"


def infer_pipeline_stage(task):
    explicit_stage = clean_text(task.get("stage"))
    if explicit_stage in PIPELINE_STAGES:
        return explicit_stage

    text_blob = build_text_blob(task)
    pipeline_keywords = {
        "Lead": ["lead"],
        "Contacted": ["contacted", "first touch"],
        "Qualified": ["qualified"],
        "Meeting Scheduled": ["meeting scheduled", "meeting"],
        "Requirement Discussion": ["requirement discussion", "requirements"],
        "Solution Proposed": ["solution proposed", "proposal"],
        "Commercial Discussion": ["commercial discussion", "pricing"],
        "POC / Testing": ["poc", "testing", "trial"],
        "Negotiation": ["negotiation", "contract"],
        "Won": ["won", "signed", "closed won"],
        "Lost": ["lost", "closed lost"],
        "On Hold": ["on hold", "hold"],
    }

    for stage, keywords in pipeline_keywords.items():
        if any(keyword in text_blob for keyword in keywords):
            return stage

    if normalize_project_status(task.get("status")) == "complete":
        return "Won"
    if normalize_project_status(task.get("status")) == "blocked":
        return "On Hold"
    if normalize_project_status(task.get("status")) == "in_progress":
        return "POC / Testing"
    return "Lead"


def infer_support_status(task):
    explicit_stage = clean_text(task.get("stage"))
    if explicit_stage in SUPPORT_TICKET_STATUSES:
        return explicit_stage

    text_blob = build_text_blob(task)
    support_keywords = {
        "New": ["new issue", "new ticket"],
        "Investigating": ["investigating", "analysis", "root cause"],
        "Waiting for Customer": ["waiting for customer", "customer feedback"],
        "Waiting for Partner": ["waiting for partner", "partner response"],
        "Fixing": ["fixing", "implementation", "patch"],
        "Retesting": ["retesting", "retest"],
        "Resolved": ["resolved", "workaround provided"],
        "Closed": ["closed", "confirmed complete"],
    }

    for status_label, keywords in support_keywords.items():
        if any(keyword in text_blob for keyword in keywords):
            return status_label

    if normalize_project_status(task.get("status")) == "complete":
        return "Resolved"
    if normalize_project_status(task.get("status")) == "blocked":
        return "Waiting for Customer"
    if normalize_project_status(task.get("status")) == "in_progress":
        return "Investigating"
    return "New"


def infer_severity(task):
    text_blob = build_text_blob(task)

    if "feature request" in text_blob:
        return "Feature Request"
    if task.get("priority") == "Urgent":
        return "S1 Critical"
    if task.get("priority") == "High":
        return "S2 High"
    if task.get("priority") == "Medium":
        return "S3 Medium"
    return "S4 Low"


def is_open_issue(task):
    latest_status = normalize_project_status(task.get("latest_processing_status") or task.get("status"))
    return bool(clean_text(task.get("issue"))) or latest_status == "blocked"


def is_critical_issue(task):
    return is_open_issue(task) and infer_severity(task) in {"S1 Critical", "S2 High"}


def customer_identity(task):
    return clean_text(task.get("company_name")) or clean_text(task.get("title"))


def count_unique_customers(tasks):
    return len({customer_identity(task) for task in tasks if customer_identity(task)})


def decorate_task(row):
    task = dict(row)
    today = date.today()
    now = datetime.now()

    due_date = parse_date(task["due_date"])
    requested_date = parse_date(task.get("requested_date"))
    created_at = parse_datetime(task["created_at"])
    updated_at = parse_datetime(task["updated_at"])
    progress_percent = clean_text(task.get("progress_percent"))
    tag_list = split_tags(task.get("tags"))
    canonical_status = normalize_project_status(task.get("status"))

    task["status"] = canonical_status
    task["project_status"] = canonical_status
    task["project_status_display"] = project_status_label(canonical_status)

    task["module_name"] = normalize_module_name(task["kpi_category"])
    module_definition = MODULE_LOOKUP_BY_NAME.get(task["module_name"])
    task["module_slug"] = module_definition["slug"] if module_definition else slugify(task["module_name"])
    task["module_short_name"] = module_definition["short_name"] if module_definition else task["module_name"]
    task["service_display"] = task["module_short_name"]
    task["project_id_display"] = f"PRJ-{task['id']:04d}"
    task["project_name_display"] = task["title"] or "Untitled project"
    task["project_type_display"] = task["module_short_name"]
    task["assignee_display"] = task.get("assignee") or task["owner"] or "Unassigned"
    task["owner_display"] = task["owner"] or "Unassigned"
    task["customer_display"] = task["company_name"] or "Customer not set"
    task["contact_number_display"] = task.get("contact_number") or "-"
    task["display_requested_date"] = requested_date.strftime("%d %b %Y") if requested_date else "No start date"
    task["display_due_date"] = due_date.strftime("%d %b %Y") if due_date else "No due date"
    task["display_created_at"] = created_at.strftime("%d %b %Y, %I:%M %p") if created_at else "-"
    task["display_updated_at"] = updated_at.strftime("%d %b %Y, %I:%M %p") if updated_at else "-"
    task["display_fit_level"] = task["fit_level"] or "-"
    task["department_display"] = task.get("department") or "-"
    task["display_progress_percent"] = f"{progress_percent}%" if progress_percent else "-"
    task["tag_list"] = tag_list
    task["display_tags"] = ", ".join(tag_list) if tag_list else "-"
    task["display_x_number_total"] = task.get("x_number_total") or "-"
    task["display_x_number_range"] = task.get("x_number_range") or "-"
    task["update_summary"] = task["last_update"] or task["current_status"] or "No recent update note."
    task["record_status_stage"] = task.get("latest_timeline_stage") or task.get("stage") or task.get("current_status") or ""
    task["record_status_text"] = task.get("latest_timeline_update") or task["update_summary"]
    task["record_status_meta"] = " | ".join(
        part for part in [task["record_status_stage"], task.get("latest_timeline_date", "")] if part
    )
    task["display_stage"] = infer_project_stage(task)
    task["display_pipeline_stage"] = infer_pipeline_stage(task)
    task["display_support_status"] = infer_support_status(task)
    task["display_severity"] = infer_severity(task)

    is_complete = task["status"] == "complete"
    task["is_complete"] = is_complete
    task["is_overdue"] = bool(due_date and due_date < today and not is_complete)
    task["is_due_today"] = bool(due_date and due_date == today and not is_complete)
    task["is_missing_next_step"] = bool(not clean_text(task["next_step"]) and not is_complete)
    task["is_stale"] = bool(updated_at and updated_at < now - timedelta(hours=24) and not is_complete)
    task["is_blocked"] = task["status"] == "blocked"
    task["has_open_issue"] = is_open_issue(task)
    task["is_critical_issue"] = is_critical_issue(task)
    task["days_overdue"] = (today - due_date).days if task["is_overdue"] else 0
    task["attention_count"] = sum(
        [
            task["is_overdue"],
            task["is_missing_next_step"],
            task["is_stale"],
            task["is_blocked"],
            task["has_open_issue"],
        ]
    )

    return task


def get_task(task_id):
    with get_db_connection() as connection:
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if row is None:
        return None

    task = decorate_task(row)
    attach_timeline_update_collections([task])
    attach_timeline_update_summaries([task])
    return task


def get_filters():
    search = clean_text(request.args.get("search"))
    category = normalize_module_name(clean_text(request.args.get("category")))
    status = normalize_project_status(request.args.get("status"), "")

    if category and category not in KPI_LOOKUP:
        category = ""

    if status and status not in STATUS_OPTIONS:
        status = ""

    return {
        "search": search,
        "category": category,
        "status": status,
    }


def get_tasks(filters=None, order="default", limit=None):
    filters = filters or {}
    where_clauses = []
    parameters = []

    search_term = clean_text(filters.get("search"))
    if search_term:
        wildcard = f"%{search_term}%"
        where_clauses.append(
            """
            (
                title LIKE ?
                OR description LIKE ?
                OR assignee LIKE ?
                OR owner LIKE ?
                OR contact_number LIKE ?
                OR department LIKE ?
                OR tags LIKE ?
                OR next_step LIKE ?
                OR stage LIKE ?
                OR current_status LIKE ?
                OR company_name LIKE ?
                OR issue LIKE ?
                OR EXISTS (
                    SELECT 1
                    FROM timeline_updates tu
                    WHERE tu.task_id = tasks.id
                      AND (
                          tu.description LIKE ?
                          OR tu.update_note LIKE ?
                          OR tu.status_label LIKE ?
                          OR tu.priority LIKE ?
                      )
                )
            )
            """
        )
        parameters.extend([wildcard] * 16)

    category = normalize_module_name(clean_text(filters.get("category")))
    if category and category in MODULE_DATABASE_VALUES:
        values = MODULE_DATABASE_VALUES[category]
        placeholders = ", ".join("?" for _ in values)
        where_clauses.append(f"kpi_category IN ({placeholders})")
        parameters.extend(values)

    status = normalize_project_status(filters.get("status"), "")
    if status:
        where_clauses.append("status = ?")
        parameters.append(status)

    order_map = {
        "default": """
            CASE WHEN due_date IS NULL OR due_date = '' THEN 1 ELSE 0 END,
            due_date ASC,
            updated_at DESC
        """,
        "recent": "updated_at DESC",
        "created": "created_at DESC",
    }
    order_by = order_map.get(order, order_map["default"])

    query = "SELECT * FROM tasks"
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += f" ORDER BY {order_by}"

    if limit:
        query += " LIMIT ?"
        parameters.append(limit)

    with get_db_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    decorated_tasks = [decorate_task(row) for row in rows]
    attach_timeline_update_collections(decorated_tasks)
    return attach_timeline_update_summaries(decorated_tasks)


def group_tasks_by_status(tasks):
    grouped_tasks = {status: [] for status in STATUS_OPTIONS}

    for task in tasks:
        grouped_tasks.setdefault(task["status"], []).append(task)

    return grouped_tasks


def build_grouped_task_sections(tasks, grouping, limit_per_status=None):
    raw_sections = []

    if grouping == "module":
        for module in MONITORING_MODULES:
            section_tasks = [task for task in tasks if task["module_name"] == module["name"]]
            if not section_tasks:
                continue

            raw_sections.append(
                {
                    "key": module["slug"],
                    "eyebrow": "Service",
                    "title": module["short_name"],
                    "subtitle": module["description"],
                    "add_category": module["name"],
                    "tasks": section_tasks,
                }
            )

    elif grouping == "customer":
        grouped_by_customer = {}
        for task in tasks:
            grouped_by_customer.setdefault(task["customer_display"], []).append(task)

        for customer_name, section_tasks in grouped_by_customer.items():
            first_task = section_tasks[0]
            raw_sections.append(
                {
                    "key": slugify(customer_name) or f"customer-{len(raw_sections) + 1}",
                    "eyebrow": "Customer",
                    "title": customer_name,
                    "subtitle": f"{first_task['module_short_name']} projects",
                    "add_category": first_task["module_name"],
                    "tasks": section_tasks,
                }
            )

    sections = []

    for raw_section in raw_sections:
        grouped_status = group_tasks_by_status(raw_section["tasks"])
        status_groups = []

        for status in STATUS_OPTIONS:
            status_tasks = grouped_status[status]
            if not status_tasks:
                continue

            rendered_tasks = status_tasks[:limit_per_status] if limit_per_status else status_tasks
            status_groups.append(
                {
                    "status": project_status_label(status),
                    "status_value": status,
                    "slug": slugify(status),
                    "count": len(status_tasks),
                    "tasks": rendered_tasks,
                    "has_more": len(rendered_tasks) < len(status_tasks),
                }
            )

        if not status_groups:
            continue

        sections.append(
            {
                "key": raw_section["key"],
                "eyebrow": raw_section["eyebrow"],
                "title": raw_section["title"],
                "subtitle": raw_section["subtitle"],
                "add_category": raw_section["add_category"],
                "record_count": len(raw_section["tasks"]),
                "issue_count": len([task for task in raw_section["tasks"] if task["has_open_issue"]]),
                "status_groups": status_groups,
            }
        )

    return sections


def build_delivery_timeline_sheet(tasks, module_slug):
    if module_slug not in {"virtual-phone", "one-click-login"}:
        return None

    timeline_rows = []
    timeline_source = [task for task in tasks if task["module_slug"] == module_slug]
    timeline_source.sort(
        key=lambda task: (
            1 if not clean_text(task["due_date"]) else 0,
            task["due_date"] or "9999-12-31",
            task["updated_at"],
        )
    )

    highlighted_stages = [
        "Requirement Gathering",
        "Technical Alignment",
        "Internal Testing",
        "Customer Testing / UAT",
        "Production Launch",
    ]
    stage_index = {stage: index for index, stage in enumerate(highlighted_stages)}

    for task in timeline_source:
        active_stage = task["display_stage"]
        milestone_index = stage_index.get(active_stage)
        if milestone_index is None:
            if active_stage in {"Sandbox Setup", "Issue Fixing", "Retesting"}:
                milestone_index = 2
            elif active_stage == "Go-Live Preparation":
                milestone_index = 3
            elif active_stage == "Post-Launch Monitoring":
                milestone_index = 4
            else:
                milestone_index = 0

        progress_percent = round((milestone_index / (len(highlighted_stages) - 1)) * 100)
        due_label = "No target date"
        due_tone = "neutral"
        if task["is_overdue"]:
            due_label = f"Overdue by {task['days_overdue']} day{'s' if task['days_overdue'] != 1 else ''}"
            due_tone = "danger"
        elif task["is_due_today"]:
            due_label = "Due today"
            due_tone = "warning"
        elif clean_text(task["due_date"]):
            due_label = task["display_due_date"]
            due_tone = "success" if task["status"] == "complete" else "neutral"

        timeline_rows.append(
            {
                "id": task["id"],
                "title": task["project_name_display"],
                "customer_display": task["customer_display"],
                "assignee_display": task["assignee_display"],
                "owner_display": task["owner_display"],
                "opened_display": task["display_created_at"].split(",")[0],
                "updated_display": task["display_updated_at"].split(",")[0],
                "target_display": task["display_due_date"],
                "due_label": due_label,
                "due_tone": due_tone,
                "stage_label": active_stage,
                "record_status_text": task.get("record_status_text") or task["update_summary"],
                "record_status_meta": task.get("record_status_meta") or active_stage,
                "progress_percent": progress_percent,
                "progress_label": f"{highlighted_stages[milestone_index]} checkpoint",
                "next_step": task["next_step"] or "Add the next action",
                "issue": task["issue"] or "",
                "latest_timeline_update": task.get("latest_timeline_update") or task["update_summary"],
                "latest_timeline_stage": task.get("latest_timeline_stage") or active_stage,
                "latest_timeline_date": task.get("latest_timeline_date") or task["display_updated_at"].split(",")[0],
                "has_timeline_update": task.get("has_timeline_update", False),
                "priority": task["priority"],
                "status": task["status"],
            }
        )

    return {
        "title": "Delivery timeline sheet",
        "intro": "Track recorded date, target go-live, current checkpoint, and the next action in one project timeline table.",
        "milestones": highlighted_stages,
        "rows": timeline_rows,
    }


def start_of_week(target_date=None):
    target_date = target_date or date.today()
    return target_date - timedelta(days=target_date.weekday())


def shift_month(anchor_date, month_offset):
    month_index = (anchor_date.year * 12) + (anchor_date.month - 1) + month_offset
    year = month_index // 12
    month = (month_index % 12) + 1
    return date(year, month, 1)


def parse_month_token(value):
    if value:
        try:
            parsed = datetime.strptime(value, "%Y-%m").date()
            return parsed.replace(day=1)
        except ValueError:
            pass

    today = date.today()
    return date(today.year, today.month, 1)


def parse_day_token(value, fallback):
    if value:
        parsed = parse_date(value)
        if parsed:
            return parsed
    return fallback


def parse_span_token(value):
    allowed = {7, 14, 30}
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 14

    return parsed if parsed in allowed else 14


def parse_sort_token(value):
    allowed = {"due", "updated", "priority", "title"}
    return value if value in allowed else "due"


def parse_fit_token(value):
    return value if value in {"auto", "comfortable"} else "auto"


def build_calendar_data(filters=None, month_token=None):
    tasks = get_tasks(filters=filters or {}, order="default")
    month_start = parse_month_token(month_token)
    month_end = date(month_start.year, month_start.month, monthrange(month_start.year, month_start.month)[1])
    calendar_start = month_start - timedelta(days=month_start.weekday())
    calendar_end = month_end + timedelta(days=(6 - month_end.weekday()))
    today = date.today()

    tasks_by_due_date = {}
    unscheduled_tasks = []

    for task in tasks:
        due_date = parse_date(task["due_date"])
        if due_date:
            tasks_by_due_date.setdefault(due_date, []).append(task)
        else:
            unscheduled_tasks.append(task)

    priority_order = {priority: index for index, priority in enumerate(PRIORITY_OPTIONS)}
    for due_date in tasks_by_due_date:
        tasks_by_due_date[due_date].sort(
            key=lambda task: (
                priority_order.get(task["priority"], len(PRIORITY_OPTIONS)),
                task["module_short_name"],
                task["title"],
            )
        )

    weeks = []
    cursor = calendar_start
    while cursor <= calendar_end:
        week_days = []
        for _ in range(7):
            day_tasks = tasks_by_due_date.get(cursor, [])
            week_days.append(
                {
                    "date": cursor,
                    "label": cursor.strftime("%a"),
                    "number": cursor.day,
                    "iso": cursor.isoformat(),
                    "is_today": cursor == today,
                    "is_current_month": cursor.month == month_start.month,
                    "tasks": day_tasks[:4],
                    "task_count": len(day_tasks),
                    "has_more": len(day_tasks) > 4,
                }
            )
            cursor += timedelta(days=1)
        weeks.append(week_days)

    due_this_month = [task for task in tasks if parse_date(task["due_date"]) and month_start <= parse_date(task["due_date"]) <= month_end]
    due_this_week = [
        task
        for task in tasks
        if parse_date(task["due_date"]) and start_of_week(today) <= parse_date(task["due_date"]) <= start_of_week(today) + timedelta(days=6)
    ]
    overdue_tasks = [task for task in tasks if task["is_overdue"]]
    upcoming_tasks = [task for task in tasks if parse_date(task["due_date"]) and parse_date(task["due_date"]) >= today][:8]

    upcoming_tasks.sort(key=lambda task: task["due_date"])
    unscheduled_tasks.sort(key=lambda task: task["updated_at"], reverse=True)

    return {
        "summary": {
            "scheduled_records": len(due_this_month),
            "due_this_week": len(due_this_week),
            "overdue": len(overdue_tasks),
            "without_due_date": len(unscheduled_tasks),
        },
        "period": {
            "label": month_start.strftime("%B %Y"),
            "month_token": month_start.strftime("%Y-%m"),
            "prev_token": shift_month(month_start, -1).strftime("%Y-%m"),
            "next_token": shift_month(month_start, 1).strftime("%Y-%m"),
        },
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "weeks": weeks,
        "upcoming_tasks": upcoming_tasks,
        "unscheduled_tasks": unscheduled_tasks[:8],
    }


def build_gantt_data(filters=None, start_token=None, days=14, sort_key="due", fit_mode="auto"):
    tasks = get_tasks(filters=filters or {}, order="default")
    today = date.today()
    window_start = parse_day_token(start_token, start_of_week(today))
    window_end = window_start + timedelta(days=days - 1)
    window_days = [window_start + timedelta(days=offset) for offset in range(days)]

    week_segments = []
    segment_start_index = 0
    while segment_start_index < len(window_days):
        segment_start_day = window_days[segment_start_index]
        segment_days = []
        while (
            segment_start_index + len(segment_days) < len(window_days)
            and window_days[segment_start_index + len(segment_days)].isocalendar().week == segment_start_day.isocalendar().week
        ):
            segment_days.append(window_days[segment_start_index + len(segment_days)])

        week_segments.append(
            {
                "label": f"W{segment_start_day.isocalendar().week}",
                "range_label": f"{segment_days[0].strftime('%b %d')} - {segment_days[-1].strftime('%b %d')}",
                "span": len(segment_days),
            }
        )
        segment_start_index += len(segment_days)

    scheduled_rows = []
    unscheduled_tasks = []
    priority_rank = {priority: index for index, priority in enumerate(PRIORITY_OPTIONS)}

    for task in tasks:
        created_at = parse_datetime(task["created_at"])
        requested_date = parse_date(task.get("requested_date"))
        start_date = requested_date or (created_at.date() if created_at else today)
        due_date = parse_date(task["due_date"])

        if not due_date:
            unscheduled_tasks.append(task)
            continue

        end_date = due_date if due_date >= start_date else start_date
        if end_date < window_start or start_date > window_end:
            continue

        clipped_start = max(start_date, window_start)
        clipped_end = min(end_date, window_end)
        left_percent = ((clipped_start - window_start).days / days) * 100
        width_percent = max((((clipped_end - clipped_start).days + 1) / days) * 100, 2.8)

        if task["status"] == "blocked" or task["is_overdue"]:
            bar_variant = "danger"
        elif task["status"] == "complete":
            bar_variant = "success"
        elif task["status"] == "in_progress":
            bar_variant = "active"
        else:
            bar_variant = "neutral"

        scheduled_rows.append(
            {
                "id": task["id"],
                "title": task["project_name_display"],
                "customer_display": task["customer_display"],
                "module_short_name": task["module_short_name"],
                "assignee_display": task["assignee_display"],
                "owner_display": task["owner_display"],
                "stage_label": task["display_stage"],
                "status_label": task["project_status_display"],
                "status": task["status"],
                "priority": task["priority"],
                "priority_rank": priority_rank.get(task["priority"], len(PRIORITY_OPTIONS)),
                "start_display": start_date.strftime("%d %b"),
                "end_display": due_date.strftime("%d %b %Y"),
                "sort_start_date": start_date.isoformat(),
                "sort_end_date": due_date.isoformat(),
                "updated_display": task["display_updated_at"],
                "updated_at": task["updated_at"],
                "record_status_text": task.get("record_status_text") or task["update_summary"],
                "record_status_meta": task.get("record_status_meta") or task["display_stage"],
                "has_timeline_update": task.get("has_timeline_update", False),
                "timeline_updates": task.get("timeline_updates", []),
                "timeline_update_count": task.get("timeline_update_count", 0),
                "next_step": task["next_step"] or "Add next action",
                "issue": task["issue"] or "",
                "left_percent": round(left_percent, 3),
                "width_percent": round(width_percent, 3),
                "is_overdue": task["is_overdue"],
                "bar_variant": bar_variant,
            }
        )

    sorters = {
        "due": lambda row: (row["sort_end_date"], row["title"].lower()),
        "updated": lambda row: (row["updated_at"], row["title"].lower()),
        "priority": lambda row: (-row["priority_rank"], row["sort_end_date"], row["title"].lower()),
        "title": lambda row: row["title"].lower(),
    }
    reverse_sort = sort_key == "updated"
    scheduled_rows.sort(key=sorters[sort_key], reverse=reverse_sort)
    unscheduled_tasks.sort(key=lambda task: task["updated_at"], reverse=True)
    due_in_window = [task for task in tasks if parse_date(task["due_date"]) and window_start <= parse_date(task["due_date"]) <= window_end]
    today_position = None
    if window_start <= today <= window_end:
        today_position = round((((today - window_start).days + 0.5) / days) * 100, 3)

    grouped_rows = {}
    for row in scheduled_rows:
        grouped_rows.setdefault(row["customer_display"], []).append(row)

    groups = []
    for customer_name, rows in grouped_rows.items():
        first_due = min(row["sort_end_date"] for row in rows)
        groups.append(
            {
                "title": customer_name,
                "task_count": len(rows),
                "earliest_due": first_due,
                "rows": rows,
            }
        )

    groups.sort(key=lambda group: (group["earliest_due"], group["title"].lower()))
    visible_row_count = sum(group["task_count"] for group in groups)
    if fit_mode == "comfortable":
        day_cell_size = 90 if days == 7 else 74 if days == 14 else 58
    else:
        day_cell_size = 72 if days == 7 else 58 if days == 14 else 46
    is_today_window = window_start <= today <= window_end

    return {
        "summary": {
            "visible_records": visible_row_count,
            "due_in_window": len(due_in_window),
            "overdue": len([row for row in scheduled_rows if row["is_overdue"]]),
            "unscheduled": len(unscheduled_tasks),
        },
        "period": {
            "label": f"{window_start.strftime('%d %b')} - {window_end.strftime('%d %b %Y')}",
            "start_token": window_start.isoformat(),
            "today_start_token": start_of_week(today).isoformat(),
            "prev_token": (window_start - timedelta(days=days)).isoformat(),
            "next_token": (window_start + timedelta(days=days)).isoformat(),
            "days": days,
            "sort_key": sort_key,
            "fit_mode": fit_mode,
        },
        "days": [
            {
                "label": day.strftime("%a"),
                "short_label": day.strftime("%a")[:2],
                "number": day.day,
                "month_label": day.strftime("%b"),
                "iso": day.isoformat(),
                "is_today": day == today,
                "is_weekend": day.weekday() >= 5,
            }
            for day in window_days
        ],
        "week_segments": week_segments,
        "rows": scheduled_rows,
        "groups": groups,
        "unscheduled_tasks": unscheduled_tasks[:8],
        "today_position": today_position,
        "day_cell_size": day_cell_size,
        "is_today_window": is_today_window,
    }


def build_gantt_export_csv(gantt_data):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Customer",
            "Project",
            "Project Type",
            "Assignee",
            "Stage",
            "Status",
            "Priority",
            "Start",
            "Target",
            "Next Action",
            "Issue",
        ]
    )

    for group in gantt_data["groups"]:
        for row in group["rows"]:
            writer.writerow(
                [
                    group["title"],
                    row["title"],
                    row["module_short_name"],
                    row["assignee_display"],
                    row["stage_label"],
                    row["status_label"],
                    row["priority"],
                    row["start_display"],
                    row["end_display"],
                    row["next_step"],
                    row["issue"],
                ]
            )

    return buffer.getvalue()


def build_table_data(filters=None):
    tasks = get_tasks(filters=filters or {}, order="default")
    due_this_week_end = start_of_week(date.today()) + timedelta(days=6)
    due_this_week = [
        task
        for task in tasks
        if parse_date(task["due_date"]) and start_of_week(date.today()) <= parse_date(task["due_date"]) <= due_this_week_end
    ]

    return {
        "summary": {
            "records": len(tasks),
            "open_issues": len([task for task in tasks if task["has_open_issue"]]),
            "overdue": len([task for task in tasks if task["is_overdue"]]),
            "due_this_week": len(due_this_week),
            "without_due_date": len([task for task in tasks if not clean_text(task["due_date"])]),
        },
        "tasks": tasks,
    }


def build_module_cards(tasks):
    module_cards = []
    weighted_total = 0

    for category in KPI_CATEGORIES:
        module_tasks = [task for task in tasks if task["module_name"] == category["name"]]
        total_tasks = len(module_tasks)
        completed_tasks = len([task for task in module_tasks if task["status"] == "complete"])
        active_count = len([task for task in module_tasks if task["status"] != "complete"])
        overdue_count = len([task for task in module_tasks if task["is_overdue"]])
        blocked_count = len([task for task in module_tasks if task["status"] == "blocked"])
        issue_count = len([task for task in module_tasks if task["has_open_issue"]])
        customer_count = count_unique_customers(module_tasks)

        progress_percent = round((completed_tasks / total_tasks) * 100, 1) if total_tasks else 0
        weighted_score = round((progress_percent / 100) * category["weight"], 1)
        weighted_total += weighted_score

        module_definition = MODULE_LOOKUP_BY_NAME[category["name"]]
        module_cards.append(
            {
                **category,
                "slug": module_definition["slug"],
                "short_name": module_definition["short_name"],
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "active_count": active_count,
                "overdue_count": overdue_count,
                "blocked_count": blocked_count,
                "issue_count": issue_count,
                "customer_count": customer_count,
                "progress_percent": progress_percent,
                "weighted_score": weighted_score,
            }
        )

    return module_cards, round(weighted_total, 1)


def build_status_breakdown(tasks):
    return [
        {
            "label": project_status_label(status),
            "value": len([task for task in tasks if task["status"] == status]),
            "slug": slugify(status),
        }
        for status in STATUS_OPTIONS
    ]


def build_module_breakdown(tasks):
    return [
        {
            "label": module["short_name"],
            "value": len([task for task in tasks if task["module_name"] == module["name"]]),
            "slug": module["slug"],
        }
        for module in MONITORING_MODULES
    ]


def build_severity_breakdown(tasks):
    return [
        {
            "label": severity,
            "value": len([task for task in tasks if task["display_severity"] == severity and task["has_open_issue"]]),
            "slug": slugify(severity),
        }
        for severity in SEVERITY_LEVELS
    ]


def build_project_stage_breakdown(tasks):
    key_stages = [
        "Requirement Gathering",
        "Technical Alignment",
        "Sandbox Setup",
        "Internal Testing",
        "Customer Testing / UAT",
        "Issue Fixing",
        "Production Launch",
    ]

    return [
        {
            "label": stage,
            "value": len([task for task in tasks if task["display_stage"] == stage]),
            "slug": slugify(stage),
        }
        for stage in key_stages
    ]


def build_pipeline_stage_breakdown(tasks):
    return [
        {
            "label": stage,
            "value": len([task for task in tasks if task["display_pipeline_stage"] == stage]),
            "slug": slugify(stage),
        }
        for stage in PIPELINE_STAGES
    ]


def build_support_status_breakdown(tasks):
    return [
        {
            "label": status_label,
            "value": len([task for task in tasks if task["display_support_status"] == status_label]),
            "slug": slugify(status_label),
        }
        for status_label in SUPPORT_TICKET_STATUSES
    ]


def build_monthly_progress_series(tasks, months=6):
    labels = []
    values = []
    today = date.today()

    for offset in range(months - 1, -1, -1):
        month_anchor = date(today.year, today.month, 1)
        current_month = month_anchor.month - offset
        current_year = month_anchor.year

        while current_month <= 0:
            current_month += 12
            current_year -= 1

        month_label = date(current_year, current_month, 1)
        labels.append(month_label.strftime("%b %Y"))

        month_total = 0
        for task in tasks:
            updated_at = parse_datetime(task["updated_at"])
            if updated_at and updated_at.year == current_year and updated_at.month == current_month:
                month_total += 1

        values.append(month_total)

    return {"labels": labels, "values": values}


def build_chart_payload(items):
    return {
        "labels": [item["label"] for item in items],
        "values": [item["value"] for item in items],
    }


def build_focus_message(summary):
    if summary["critical_issues"]:
        return {
            "title": "Critical issues need management attention",
            "copy": f"{summary['critical_issues']} critical or high-severity item(s) are open across the workspace. Review issue owners and unblock the next action quickly.",
        }

    if summary["projects_in_uat"]:
        return {
            "title": "Customer validation is active",
            "copy": f"{summary['projects_in_uat']} project(s) are in customer testing or UAT. This is the right time to keep updates, blockers, and approvals visible.",
        }

    return {
        "title": "The monitoring workspace is giving a clean overview",
        "copy": "Use the module pages to drill into product-specific details, and use reports to keep operational visibility consistent for management.",
    }


def get_dashboard_data():
    tasks = get_tasks(order="recent")
    active_tasks = [task for task in tasks if task["status"] != "complete"]
    recent_updates = tasks[:6]
    attention_tasks = [task for task in active_tasks if task["attention_count"] > 0]
    attention_tasks.sort(
        key=lambda task: (
            task["is_critical_issue"],
            task["attention_count"],
            task["is_overdue"],
            task["is_blocked"],
        ),
        reverse=True,
    )

    virtual_phone_tasks = [task for task in tasks if task["module_name"] == "Virtual Phone Management"]
    one_click_tasks = [task for task in tasks if task["module_name"] == "One-Click Login Management"]
    pipeline_tasks = [task for task in tasks if task["module_name"] == "Customer Pipeline"]
    support_tasks = [task for task in tasks if task["module_name"] == "Business Support"]

    testing_projects = [
        task
        for task in tasks
        if task["display_stage"] in {"Sandbox Setup", "Internal Testing", "Issue Fixing", "Retesting"}
    ]
    uat_projects = [task for task in tasks if task["display_stage"] == "Customer Testing / UAT"]
    live_projects = [
        task
        for task in tasks
        if task["display_stage"] in {"Production Launch", "Post-Launch Monitoring"} or task["status"] == "complete"
    ]
    open_issues = [task for task in tasks if task["has_open_issue"]]
    critical_issues = [task for task in tasks if task["is_critical_issue"]]

    module_cards, weighted_total = build_module_cards(tasks)

    summary = {
        "total_records": len(tasks),
        "active_customers": count_unique_customers(active_tasks),
        "virtual_phone_customers": count_unique_customers(virtual_phone_tasks),
        "one_click_customers": count_unique_customers(one_click_tasks),
        "projects_in_testing": len(testing_projects),
        "projects_in_uat": len(uat_projects),
        "live_projects": len(live_projects),
        "open_issues": len(open_issues),
        "critical_issues": len(critical_issues),
        "support_open": len([task for task in support_tasks if task["status"] != "complete"]),
        "weighted_total": weighted_total,
    }

    charts = {
        "modules": build_chart_payload(build_module_breakdown(tasks)),
        "stages": build_chart_payload(build_project_stage_breakdown(tasks)),
        "severity": build_chart_payload(build_severity_breakdown(tasks)),
        "pipeline": build_chart_payload(build_pipeline_stage_breakdown(pipeline_tasks)),
    }

    return {
        "summary": summary,
        "focus": build_focus_message(summary),
        "module_cards": module_cards,
        "module_sections": build_grouped_task_sections(tasks, "module", limit_per_status=4),
        "recent_updates": recent_updates,
        "attention_tasks": attention_tasks[:6],
        "support_status": build_support_status_breakdown(support_tasks),
        "pipeline_status": build_pipeline_stage_breakdown(pipeline_tasks),
        "dashboard_charts": charts,
    }


def get_report_data(filters=None):
    tasks = get_tasks(filters=filters or {}, order="default")
    active_tasks = [task for task in tasks if task["status"] != "complete"]
    module_cards, weighted_total = build_module_cards(tasks)

    summary = {
        "filtered_task_count": len(tasks),
        "active_projects": len(active_tasks),
        "open_issues": len([task for task in tasks if task["has_open_issue"]]),
        "critical_issues": len([task for task in tasks if task["is_critical_issue"]]),
        "live_projects": len([task for task in tasks if task["display_stage"] in {"Production Launch", "Post-Launch Monitoring"}]),
        "weighted_total": weighted_total,
    }

    report_charts = {
        "modules": build_chart_payload(build_module_breakdown(tasks)),
        "stages": build_chart_payload(build_project_stage_breakdown(tasks)),
        "severity": build_chart_payload(build_severity_breakdown(tasks)),
        "monthly": build_monthly_progress_series(tasks),
    }

    return {
        "summary": summary,
        "tasks": tasks,
        "module_cards": module_cards,
        "module_sections": build_grouped_task_sections(tasks, "module", limit_per_status=6),
        "report_charts": report_charts,
    }


def get_module_data(module_slug):
    module = get_module(module_slug)
    if module is None:
        return None

    tasks = get_tasks(filters={"category": module["name"]}, order="recent")
    active_tasks = [task for task in tasks if task["status"] != "complete"]
    recent_updates = tasks[:6]
    attention_tasks = [task for task in active_tasks if task["attention_count"] > 0][:6]

    if module_slug == "customer-pipeline":
        primary_breakdown = build_pipeline_stage_breakdown(tasks)
    elif module_slug == "business-support":
        primary_breakdown = build_support_status_breakdown(tasks)
    else:
        primary_breakdown = build_project_stage_breakdown(tasks)

    secondary_breakdown = build_status_breakdown(tasks)

    summary = {
        "records": len(tasks),
        "customers": count_unique_customers(tasks),
        "active": len(active_tasks),
        "open_issues": len([task for task in tasks if task["has_open_issue"]]),
        "overdue": len([task for task in active_tasks if task["is_overdue"]]),
        "blocked": len([task for task in active_tasks if task["is_blocked"]]),
    }

    return {
        "module": module,
        "tasks": tasks,
        "summary": summary,
        "timeline_sheet": build_delivery_timeline_sheet(tasks, module_slug),
        "customer_sections": build_grouped_task_sections(tasks, "customer", limit_per_status=6),
        "recent_updates": recent_updates,
        "attention_tasks": attention_tasks,
        "primary_breakdown": primary_breakdown,
        "secondary_breakdown": secondary_breakdown,
        "module_charts": {
            "primary": build_chart_payload(primary_breakdown),
            "secondary": build_chart_payload(secondary_breakdown),
        },
    }


def get_settings_data():
    tasks = get_tasks(order="recent")
    active_tasks = [task for task in tasks if task["status"] != "complete"]
    module_cards, weighted_total = build_module_cards(tasks)
    latest_activity = tasks[0]["display_updated_at"] if tasks else "No activity yet"
    schema_source = str(SCHEMA_PATH) if SCHEMA_PATH.exists() else "Embedded default schema"

    storage_details = [
        {"label": "Storage mode", "value": "SQLite local file"},
        {"label": "Database path", "value": str(DATABASE_PATH)},
        {"label": "Schema source", "value": schema_source},
        {"label": "Latest activity", "value": latest_activity},
    ]

    workspace_health = [
        {"label": "Total projects", "value": len(tasks)},
        {"label": "Active projects", "value": len(active_tasks)},
        {"label": "Unique customers", "value": count_unique_customers(tasks)},
        {"label": "Weighted readiness score", "value": f"{weighted_total}%"},
    ]

    data_quality = [
        {"label": "Missing next action", "value": len([task for task in active_tasks if task["is_missing_next_step"]])},
        {"label": "Overdue projects", "value": len([task for task in active_tasks if task["is_overdue"]])},
        {"label": "Blocked projects", "value": len([task for task in active_tasks if task["is_blocked"]])},
        {"label": "Open issues", "value": len([task for task in tasks if task["has_open_issue"]])},
    ]

    return {
        "storage_details": storage_details,
        "workspace_health": workspace_health,
        "data_quality": data_quality,
        "module_cards": module_cards,
    }


def redirect_to_next_page():
    next_page = clean_text(request.form.get("next"))

    route_map = {
        "dashboard": lambda: url_for("dashboard"),
        "board": lambda: url_for("board_view"),
        "calendar": lambda: url_for("calendar_view"),
        "gantt": lambda: url_for("gantt_view"),
        "table": lambda: url_for("table_view"),
        "reports": lambda: url_for("report_view"),
        "settings": lambda: url_for("settings_view"),
    }

    if next_page in MODULE_LOOKUP_BY_SLUG:
        return redirect(url_for("module_view", module_slug=next_page))

    if next_page in route_map:
        return redirect(route_map[next_page]())

    return redirect(url_for("report_view"))


@app.context_processor
def inject_template_data():
    return {
        "kpi_categories": KPI_CATEGORIES,
        "status_options": STATUS_OPTIONS,
        "status_choices": STATUS_CHOICES,
        "status_labels": STATUS_LABELS,
        "priority_options": PRIORITY_OPTIONS,
        "fit_level_options": FIT_LEVEL_OPTIONS,
        "update_type_options": UPDATE_TYPE_OPTIONS,
        "monitoring_modules": MONITORING_MODULES,
        "standard_project_stages": STANDARD_PROJECT_STAGES,
        "pipeline_stages": PIPELINE_STAGES,
        "support_ticket_statuses": SUPPORT_TICKET_STATUSES,
        "severity_levels": SEVERITY_LEVELS,
        "core_users": CORE_USERS,
        "alert_suggestions": ALERT_SUGGESTIONS,
        "permission_groups": PERMISSION_GROUPS,
        "report_types": REPORT_TYPES,
        "export_options": EXPORT_OPTIONS,
        "mvp_features": MVP_FEATURES,
        "workspace_snapshot_date": date.today().strftime("%d %b %Y"),
    }


@app.route("/")
@app.route("/dashboard")
def dashboard():
    dashboard_data = get_dashboard_data()
    return render_template(
        "index.html",
        active_page="dashboard",
        summary=dashboard_data["summary"],
        focus=dashboard_data["focus"],
        module_cards=dashboard_data["module_cards"],
        module_sections=dashboard_data["module_sections"],
        recent_updates=dashboard_data["recent_updates"],
        attention_tasks=dashboard_data["attention_tasks"],
        support_status=dashboard_data["support_status"],
        pipeline_status=dashboard_data["pipeline_status"],
        dashboard_charts=dashboard_data["dashboard_charts"],
    )


@app.route("/modules/<module_slug>")
def module_view(module_slug):
    module_data = get_module_data(module_slug)
    if module_data is None:
        flash("Monitoring module not found.", "error")
        return redirect(url_for("dashboard"))

    return render_template(
        "module.html",
        active_page=module_slug,
        module=module_data["module"],
        summary=module_data["summary"],
        tasks=module_data["tasks"],
        timeline_sheet=module_data["timeline_sheet"],
        customer_sections=module_data["customer_sections"],
        recent_updates=module_data["recent_updates"],
        attention_tasks=module_data["attention_tasks"],
        primary_breakdown=module_data["primary_breakdown"],
        secondary_breakdown=module_data["secondary_breakdown"],
        module_charts=module_data["module_charts"],
    )


@app.route("/board")
def board_view():
    filters = get_filters()
    tasks = get_tasks(filters=filters)
    grouped_tasks = group_tasks_by_status(tasks)

    return render_template(
        "board.html",
        active_page="board",
        filters=filters,
        grouped_tasks=grouped_tasks,
        filtered_task_count=len(tasks),
    )


@app.route("/calendar")
def calendar_view():
    filters = get_filters()
    calendar_data = build_calendar_data(filters=filters, month_token=clean_text(request.args.get("month")))

    return render_template(
        "calendar.html",
        active_page="calendar",
        filters=filters,
        summary=calendar_data["summary"],
        calendar_period=calendar_data["period"],
        weekdays=calendar_data["weekdays"],
        calendar_weeks=calendar_data["weeks"],
        upcoming_tasks=calendar_data["upcoming_tasks"],
        unscheduled_tasks=calendar_data["unscheduled_tasks"],
    )


@app.route("/gantt")
def gantt_view():
    filters = get_filters()
    span_days = parse_span_token(request.args.get("span"))
    sort_key = parse_sort_token(clean_text(request.args.get("sort")))
    fit_mode = parse_fit_token(clean_text(request.args.get("fit")))
    gantt_data = build_gantt_data(
        filters=filters,
        start_token=clean_text(request.args.get("start")),
        days=span_days,
        sort_key=sort_key,
        fit_mode=fit_mode,
    )

    return render_template(
        "gantt.html",
        active_page="gantt",
        filters=filters,
        summary=gantt_data["summary"],
        gantt=gantt_data,
    )


@app.route("/gantt/export")
def gantt_export_view():
    filters = get_filters()
    span_days = parse_span_token(request.args.get("span"))
    sort_key = parse_sort_token(clean_text(request.args.get("sort")))
    fit_mode = parse_fit_token(clean_text(request.args.get("fit")))
    gantt_data = build_gantt_data(
        filters=filters,
        start_token=clean_text(request.args.get("start")),
        days=span_days,
        sort_key=sort_key,
        fit_mode=fit_mode,
    )

    csv_content = build_gantt_export_csv(gantt_data)
    filename = f"monitoring-gantt-{gantt_data['period']['start_token']}.csv"
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.route("/list")
@app.route("/reports")
def report_view():
    filters = get_filters()
    report_data = get_report_data(filters=filters)

    return render_template(
        "report.html",
        active_page="reports",
        filters=filters,
        summary=report_data["summary"],
        tasks=report_data["tasks"],
        module_cards=report_data["module_cards"],
        module_sections=report_data["module_sections"],
        report_charts=report_data["report_charts"],
    )


@app.route("/table")
def table_view():
    filters = get_filters()
    table_data = build_table_data(filters=filters)

    return render_template(
        "table.html",
        active_page="table",
        filters=filters,
        summary=table_data["summary"],
        tasks=table_data["tasks"],
    )


@app.route("/settings")
def settings_view():
    settings_data = get_settings_data()
    return render_template(
        "settings.html",
        active_page="settings",
        settings_data=settings_data,
    )


@app.route("/tasks/new", methods=["GET", "POST"])
@app.route("/records/new", methods=["GET", "POST"])
def add_task():
    default_status = normalize_project_status(request.args.get("status"), STATUS_OPTIONS[0])

    default_category = normalize_module_name(clean_text(request.args.get("category")))
    if default_category not in KPI_LOOKUP:
        default_category = KPI_CATEGORIES[0]["name"]

    if request.method == "POST":
        task_data = build_task_form_data(
            form_data=request.form,
            default_status=default_status,
            default_category=default_category,
        )
        errors = validate_task_form(task_data)

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "task_form.html",
                active_page="new-record",
                page_mode="add",
                page_title="Add Project",
                page_intro="Capture the main project information for a service and then add processing updates under the project detail page.",
                form_action=url_for("add_task"),
                task=task_data,
            )

        task_id = create_task(task_data)
        flash("Project created successfully.", "success")
        return redirect(url_for("task_detail", task_id=task_id))

    task_data = build_task_form_data(default_status=default_status, default_category=default_category)
    return render_template(
        "task_form.html",
        active_page="new-record",
        page_mode="add",
        page_title="Add Project",
        page_intro="Capture the main project information for a service and then add processing updates under the project detail page.",
        form_action=url_for("add_task"),
        task=task_data,
    )


@app.route("/tasks/<int:task_id>")
@app.route("/kpis/<int:task_id>")
def task_detail(task_id):
    task = get_task(task_id)
    if task is None:
        flash("Project not found.", "error")
        return redirect(url_for("report_view"))

    return render_template(
        "task_detail.html",
        active_page=task["module_slug"],
        task=task,
        timeline_updates=get_task_timeline_updates(task_id),
        timeline_update_form=build_timeline_update_data(task=task),
    )


@app.route("/tasks/<int:task_id>/timeline-update", methods=["POST"])
def add_task_timeline_update(task_id):
    task = get_task(task_id)
    if task is None:
        flash("Project not found.", "error")
        return redirect(url_for("report_view"))

    update_data = build_timeline_update_data(form_data=request.form, task=task)
    errors = validate_timeline_update(update_data)

    if errors:
        for error in errors:
            flash(error, "error")
    else:
        create_timeline_update(task_id, update_data)
        flash("Project processing update added.", "success")

    return redirect(url_for("task_detail", task_id=task_id) + "#timeline-updates")


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@app.route("/records/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    existing_task = get_task(task_id)
    if existing_task is None:
        flash("Project not found.", "error")
        return redirect(url_for("report_view"))

    if request.method == "POST":
        task_data = build_task_form_data(existing_task=existing_task, form_data=request.form)
        errors = validate_task_form(task_data)

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "task_form.html",
                active_page=existing_task["module_slug"],
                page_mode="edit",
                page_title="Edit Project",
                page_intro="Update the main project information for this project without overwriting the processing update history.",
                form_action=url_for("edit_task", task_id=task_id),
                task=task_data,
                task_id=task_id,
            )

        update_task(task_id, task_data)
        flash("Project updated successfully.", "success")
        return redirect(url_for("task_detail", task_id=task_id))

    task_data = build_task_form_data(existing_task=existing_task)
    return render_template(
        "task_form.html",
        active_page=existing_task["module_slug"],
        page_mode="edit",
        page_title="Edit Project",
        page_intro="Update the main project information for this project without overwriting the processing update history.",
        form_action=url_for("edit_task", task_id=task_id),
        task=task_data,
        task_id=task_id,
    )


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@app.route("/records/<int:task_id>/delete", methods=["POST"])
def remove_task(task_id):
    task = get_task(task_id)
    if task is None:
        flash("Project not found.", "error")
        return redirect(url_for("report_view"))

    delete_task(task_id)
    flash(f"Project #{task_id} was deleted.", "success")
    return redirect_to_next_page()


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)

# Flask CRM Dashboard Architecture

## Product Architecture

The current implementation uses a simple Flask-first architecture that keeps the main entry point in `app.py` while separating business rules and persistence into small service modules.

### Layers

1. Route and page composition
   - `app.py`
   - Owns Flask app setup, routes, request parsing, form validation, flash messages, and template rendering.

2. Domain and business logic
   - `services/project_service.py`
   - `services/dashboard_service.py`
   - `services/activity_service.py`
   - Owns project rollups, status calculation, progress calculation, board grouping, gantt timeline shaping, alerts, and audit log generation.

3. Persistence
   - `services/repository.py`
   - Uses SQLite for runtime persistence and seeds the first workspace from JSON sample files in `data/`.

4. Presentation
   - `templates/`
   - `static/`
   - Jinja templates render the workspace layout, reusable partials, views, and forms. Static CSS and JavaScript provide UI styling and small interactions.

## Recommended Folder Structure

```text
app.py
services/
  __init__.py
  repository.py
  project_service.py
  dashboard_service.py
  activity_service.py
templates/
  base.html
  dashboard/
    index.html
  partials/
    _sidebar.html
    _topbar.html
    _toolbar.html
    _macros.html
    _activity_timeline.html
    _comment_list.html
  projects/
    list.html
    table.html
    board.html
    gantt.html
    detail.html
    project_form.html
    action_form.html
static/
  style.css
  app.js
runtime/
  workspace.sqlite3
data/
  projects.json
  actions.json
  comments.json
  activity_logs.json
docs/
  flask-crm-dashboard-architecture.md
```

## Data Model

### Projects

- `id`
- `service_name`
- `project_name`
- `client_name`
- `priority`
- `owner`
- `start_date`
- `due_date`
- `contact_number`
- `remark`
- `created_at`
- `updated_at`

### Actions

- `id`
- `project_id`
- `action_name`
- `description`
- `action_status`
- `priority`
- `assignee`
- `start_date`
- `due_date`
- `progress_percent`
- `remark`
- `created_at`
- `updated_at`

### Comments

- `id`
- `project_id`
- `action_id`
- `comment_text`
- `created_by`
- `created_at`

### Activity Logs

- `id`
- `project_id`
- `action_id`
- `field_name`
- `old_value`
- `new_value`
- `updated_by`
- `updated_at`
- `comment`

## Business Logic

### Action status rules

- Base statuses: `Not Started`, `In Progress`, `Pending`, `Completed`, `On Hold`, `Cancelled`
- Display status becomes `Overdue` when `today > due_date` and the action is not `Completed` or `Cancelled`
- Upcoming alert becomes active when due date is within 3 days

### Project status rollup

- No child actions: `Not Started`
- All child actions completed: `Completed`
- All child actions cancelled: `Cancelled`
- Any overdue child action: `At Risk`
- Any child action in `In Progress` or `Pending`: `In Progress`
- Otherwise: `Not Started`

### Project progress rollup

- Project progress is the average of all child `progress_percent` values
- If there are no actions, project progress is `0`

### Activity log rules

The app writes logs for:

- project creation
- project field changes
- action creation
- action field changes
- action deletion
- comment creation
- project rollup changes after action updates

## Page Map

### Main views

- `/dashboard`
  - KPI cards, status breakdowns, ownership, overdue work, and attention projects

- `/projects` and `/projects/table`
  - Main table view with filters and project-level columns

- `/projects/list`
  - Card-based list for quick scanning

- `/projects/board`
  - Kanban board grouped by action status

- `/projects/gantt`
  - Timeline view for projects and actions

### Detail and forms

- `/projects/<project_id>`
  - Project detail, action list, comments, and activity log

- `/projects/new`
  - Create project form

- `/projects/<project_id>/edit`
  - Edit project form

- `/projects/<project_id>/actions/new`
  - Add action form

- `/actions/<action_id>/edit`
  - Edit action form

- `/actions/<action_id>/delete`
  - Delete action POST endpoint

- `/projects/<project_id>/comments`
  - Add comment POST endpoint

## Template Map

### Layout shell

- `templates/base.html`
  - Main workspace shell with sidebar, topbar, flash messages, and content region

### Reusable partials

- `templates/partials/_sidebar.html`
  - Left workspace navigation

- `templates/partials/_topbar.html`
  - Header and utility controls

- `templates/partials/_toolbar.html`
  - Shared project view tabs and filter toolbar

- `templates/partials/_macros.html`
  - Badge, metric card, and progress bar macros

- `templates/partials/_activity_timeline.html`
  - Audit log renderer

- `templates/partials/_comment_list.html`
  - Comment stream renderer

### Feature views

- `templates/dashboard/index.html`
  - Dashboard layout

- `templates/projects/list.html`
  - List view

- `templates/projects/table.html`
  - Table view

- `templates/projects/board.html`
  - Board view

- `templates/projects/gantt.html`
  - Gantt view

- `templates/projects/detail.html`
  - Project detail page

- `templates/projects/project_form.html`
  - Create and edit project form

- `templates/projects/action_form.html`
  - Create and edit action form

## Reusable Component Plan

The current UI is organized around reusable building blocks rather than page-specific markup.

### Display components

- status badge
- priority badge
- progress bar
- metric card
- flash message block

### Layout components

- sidebar navigation
- top toolbar
- shared page header
- filter toolbar
- content panel wrapper

### Data presentation components

- project table row
- project list card
- board card
- gantt row
- activity timeline item
- comment item

### Form components

- project form fields
- action form fields
- action row controls
- delete confirmation hook

## MVP Implementation Plan

### Phase 1

- Define product structure and data model
- Separate route layer from service logic
- Load seed data from `data/`

### Phase 2

- Build base layout
- Build dashboard
- Build list, table, board, and gantt views
- Build project detail page
- Add create and edit forms for projects and actions

### Phase 3

- Add comments and activity logs
- Add automatic rollup logic
- Add filters and search
- Add delete flow and confirmation

### Next recommended phase

- Add a proper SQLAlchemy model layer and migrations on top of SQLite
- Add authentication and role-based access
- Add project deletion and soft-delete rules
- Add richer filtering, exports, and saved views
- Add chart visualizations and notification center

## Files Created or Updated In This MVP

### Main entry

- `app.py`

### Services

- `services/__init__.py`
- `services/repository.py`
- `services/project_service.py`
- `services/dashboard_service.py`
- `services/activity_service.py`

### Data

- `data/projects.json`
- `data/actions.json`
- `data/comments.json`
- `data/activity_logs.json`

### Templates

- `templates/base.html`
- `templates/dashboard/index.html`
- `templates/partials/_sidebar.html`
- `templates/partials/_topbar.html`
- `templates/partials/_toolbar.html`
- `templates/partials/_macros.html`
- `templates/partials/_activity_timeline.html`
- `templates/partials/_comment_list.html`
- `templates/projects/list.html`
- `templates/projects/table.html`
- `templates/projects/board.html`
- `templates/projects/gantt.html`
- `templates/projects/detail.html`
- `templates/projects/project_form.html`
- `templates/projects/action_form.html`

### Static

- `static/style.css`
- `static/app.js`

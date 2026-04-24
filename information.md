# design.md

## Project CRM and Monitoring Dashboard

## 1. Overview
This system is a web-based CRM and monitoring dashboard used to manage **projects** and track **actions/tasks** under each project.

The main goal is to help users:
- create and manage projects,
- track each action under each project,
- monitor progress and due dates,
- view the same data in multiple formats such as **Dashboard, List, Table, Board, and Gantt**.

---

## 2. Problem Statement
The current data is stored in a flat table format, where each row contains both project-level and action-level information.

Example:

| Service | Project | Action | Description | Project Status | Priority | Owner | Start Date | Due Date | Contact Number | Remark |
|---|---|---|---|---|---|---|---|---|---|---|
| Virtual Phone Number | J&T | Testing | xxxxxxxxxx | Start | High | Yee | 15 Apr | 20 Apr | 888888888 | |
| OneClick Login | J&T Testing | POC | yyyyyyyyyy | First Discussion | Low | Yee | 30 Apr | | 777777777777 | |
| OneClick Login | Flash | Discuss | zzzzzzzzzz | In Process | Low | Yee | 30 Apr | | 777777777777 | |

This format is useful for recording data quickly, but it becomes difficult when:
- one project has multiple actions,
- users want to track project progress separately from action progress,
- users need dashboard views,
- users want board and gantt visualization,
- users want activity logs and notifications.

Because of this, the system should separate **Project** and **Action** into different layers.

---

## 3. Product Goal
Build a system that can:
- manage project information,
- support multiple actions under one project,
- monitor each action status,
- auto-calculate project status and progress,
- show data in different views,
- highlight overdue and upcoming tasks,
- keep update history for tracking.

---

## 4. Core Concept
The system should use a **2-layer structure**.

### 4.1 Project Layer
A project is the main work item.

Examples:
- Virtual Phone Number x J&T
- OneClick Login x Flash

### 4.2 Action Layer
An action is a task or step under a project.

Examples:
- First Discussion
- POC
- Testing
- Integration
- UAT
- Launch

### Rule
- **1 Project can have many Actions**
- **Every Action must belong to 1 Project**

---

## 5. User Roles

### 5.1 Admin
Can:
- manage all projects,
- manage all actions,
- manage users,
- view all dashboards,
- edit and delete records,
- export reports.

### 5.2 Manager
Can:
- manage projects in their team,
- update actions,
- monitor dashboard,
- review overdue and pending work.

### 5.3 User
Can:
- view assigned projects,
- update assigned actions,
- add remarks and comments,
- update progress and status.

---

## 6. Main Modules
The system should contain the following modules:

1. Authentication
2. Dashboard
3. Project Management
4. Action / Task Management
5. Board View
6. Table View
7. List View
8. Gantt View
9. Activity Log
10. Notification / Alert
11. User Management
12. Search and Filter

---

## 7. Data Model

## 7.1 Projects Table
Stores main project information.

| Field | Type | Description |
|---|---|---|
| project_id | UUID / INT | Unique project ID |
| service_name | string | Service type, e.g. Virtual Phone Number |
| client_name | string | Client or account name |
| project_name | string | Display project name |
| project_status | enum | Overall project status |
| priority | enum | Low / Medium / High / Urgent |
| owner_id | FK user_id | Project owner |
| start_date | date | Project start date |
| due_date | date | Project due date |
| contact_number | string | Main contact number |
| remark | text | Additional note |
| progress_percent | number | Auto-calculated project progress |
| created_at | datetime | Record creation time |
| updated_at | datetime | Last update time |
| created_by | FK user_id | User who created the record |

### Suggested Enums
**project_status**
- Not Started
- In Progress
- Completed
- Pending
- On Hold
- At Risk
- Cancelled

**priority**
- Low
- Medium
- High
- Urgent

---

## 7.2 Actions Table
Stores actions or tasks under each project.

| Field | Type | Description |
|---|---|---|
| action_id | UUID / INT | Unique action ID |
| project_id | FK project_id | Related project |
| action_name | string | Action name, e.g. Testing |
| description | text | Task detail |
| action_status | enum | Current action status |
| priority | enum | Low / Medium / High / Urgent |
| assignee_id | FK user_id | Assigned user |
| start_date | date | Action start date |
| due_date | date | Action due date |
| progress_percent | number | 0-100 |
| remark | text | Additional note |
| created_at | datetime | Record creation time |
| updated_at | datetime | Last update time |
| created_by | FK user_id | User who created the record |

### Suggested Enums
**action_status**
- Not Started
- In Progress
- Pending
- Completed
- On Hold
- Cancelled
- Overdue

---

## 7.3 Activity Logs Table
Stores all important changes for tracking and audit.

| Field | Type | Description |
|---|---|---|
| log_id | UUID / INT | Unique log ID |
| project_id | FK project_id | Related project |
| action_id | FK action_id, nullable | Related action |
| field_name | string | Changed field |
| old_value | text | Previous value |
| new_value | text | New value |
| comment | text | Optional explanation |
| updated_by | FK user_id | User who made the change |
| updated_at | datetime | Change timestamp |

Examples:
- Action status changed from `Not Started` to `In Progress`
- Due date changed from `2026-04-20` to `2026-04-25`

---

## 7.4 Comments Table
Stores update notes or comments.

| Field | Type | Description |
|---|---|---|
| comment_id | UUID / INT | Unique comment ID |
| project_id | FK project_id | Related project |
| action_id | FK action_id, nullable | Related action |
| comment_text | text | Comment content |
| created_by | FK user_id | Comment owner |
| created_at | datetime | Comment timestamp |

---

## 7.5 Users Table
Stores user information.

| Field | Type | Description |
|---|---|---|
| user_id | UUID / INT | Unique user ID |
| full_name | string | User name |
| email | string | Email |
| role | enum | Admin / Manager / User |
| team | string | Team name |
| status | enum | Active / Inactive |
| created_at | datetime | Record creation time |

---

## 8. Business Logic

## 8.1 Create Project Logic
When the user creates a new project:

### Input
- service_name
- client_name
- project_name
- priority
- owner
- start_date
- due_date
- contact_number
- remark

### Rules
- project_name is required
- service_name is required
- owner is required
- start_date must be earlier than or equal to due_date
- project_status defaults to `Not Started`
- progress_percent defaults to `0`
- system auto-generates `project_id`, `created_at`, `updated_at`

### Output
- project record created
- project visible in dashboard and list views

---

## 8.2 Add Action Logic
When the user adds an action under a project:

### Input
- project_id
- action_name
- description
- assignee
- action_status
- priority
- start_date
- due_date
- remark

### Rules
- action must belong to a valid project
- action_name is required
- action_status defaults to `Not Started`
- progress_percent defaults to `0`
- due_date must be later than or equal to start_date
- when a new action is added, system updates project `updated_at`

### Output
- action record created
- action visible in project detail, board, table, gantt

---

## 8.3 Update Action Logic
Users can update:
- action_status
- progress_percent
- due_date
- assignee
- description
- remark

### Rules
Every time an action is updated:
1. save the new action data,
2. write activity log,
3. update `updated_at`,
4. re-calculate project progress,
5. re-calculate project status,
6. refresh all views,
7. check if notification rules are triggered.

---

## 8.4 Delete Logic
### Delete Action
- action can be deleted only by Admin or Manager
- if action is deleted, system should also record deletion in activity log
- project progress and project status must be recalculated after deletion

### Delete Project
- only Admin can delete project
- engineer should decide whether to use hard delete or soft delete
- recommended: **soft delete** for better audit trail

---

## 9. Status Logic

## 9.1 Action Status Logic
### Manual Status
User can set:
- Not Started
- In Progress
- Pending
- Completed
- On Hold
- Cancelled

### Auto Overdue Rule
If:
- current date > due_date
- and action_status is not Completed
- and action_status is not Cancelled

Then system flags the action as **Overdue** in UI.

Note:
- engineer can store `Overdue` as a display state instead of a real database status, depending on architecture.

---

## 9.2 Project Status Logic
Project status should be auto-calculated from child actions.

### Rule Set
**Rule 1**
If a project has no actions:
- project_status = `Not Started`

**Rule 2**
If all actions are `Completed`:
- project_status = `Completed`

**Rule 3**
If at least one action is overdue:
- project_status = `At Risk`

**Rule 4**
If at least one action is `In Progress` or `Pending`:
- project_status = `In Progress`

**Rule 5**
If all actions are `Cancelled`:
- project_status = `Cancelled`

**Rule 6**
If actions exist but none started yet:
- project_status = `Not Started`

Recommended priority order:
1. Completed
2. At Risk
3. In Progress
4. Cancelled
5. Not Started

Engineer should finalize exact precedence if mixed cases occur.

---

## 10. Progress Logic

## 10.1 Action Progress
Each action has `progress_percent` from 0 to 100.

Suggested default mapping:
- Not Started = 0
- Completed = 100

For other statuses, user can update manually or system can use suggested values:
- In Progress = 25-75
- Pending = keep existing value
- On Hold = keep existing value

---

## 10.2 Project Progress
Project progress is calculated from all child actions.

### Formula
```text
Project Progress = sum(action progress_percent) / total number of actions
```

### Example
- Action A = 100
- Action B = 50
- Action C = 0

Project Progress = `(100 + 50 + 0) / 3 = 50`

If no actions exist:
- progress_percent = 0

---

## 11. Views and UI Logic

## 11.1 Dashboard View
The dashboard is the summary page.

### Summary Cards
- Total Projects
- Active Projects
- Completed Projects
- Total Actions
- Overdue Actions
- Upcoming Due This Week
- High Priority Actions

### Charts / Widgets
- Projects by Status
- Actions by Status
- Actions by Priority
- Projects by Owner
- Overdue Actions by Owner
- Due Timeline

### Filters
- Service
- Owner
- Status
- Priority
- Date Range
- Client

---

## 11.2 List View
Simple view for scanning projects quickly.

### Fields
- Project Name
- Service
- Owner
- Project Status
- Priority
- Due Date
- Progress

### Features
- search
- filter
- click into detail page

---

## 11.3 Table View
Detailed grid view for projects and actions.

### Suggested Columns
- Service
- Client
- Project Name
- Action Count
- Project Status
- Priority
- Owner
- Start Date
- Due Date
- Progress
- Updated At

### Features
- sort
- filter
- search
- hide/show columns
- pagination
- export CSV / Excel, optional in phase 2

---

## 11.4 Board View
Kanban-style view for actions.

### Columns
- Not Started
- In Progress
- Pending
- Completed
- On Hold

### Logic
- each card = 1 action
- drag and drop between columns changes action status
- when status changes, system:
  - updates database,
  - writes activity log,
  - recalculates project status,
  - refreshes dashboard

---

## 11.5 Gantt View
Timeline view for projects and actions.

### Logic
- parent row = project
- child row = actions
- start_date and due_date define bar length
- progress displayed inside bar
- overdue bars should be highlighted

### Features
- zoom by week / month
- expand and collapse project rows
- click a bar to open detail
- optional: drag bar to change date in later phase

---

## 12. Detail Page Logic

## 12.1 Project Detail Page
Should show:
- project information,
- current project status,
- progress,
- all actions under the project,
- comments,
- activity log,
- contact information,
- related alerts.

### Project Detail Sections
1. Header Summary
2. Project Information
3. Action List
4. Comment / Update Panel
5. Activity Log Panel
6. Quick Actions

### Quick Actions
- Edit Project
- Add Action
- Update Status
- Add Comment
- Change Owner

---

## 12.2 Action Detail Drawer / Modal
Should show:
- action name,
- description,
- assignee,
- status,
- progress,
- due date,
- remarks,
- comment history,
- activity history.

---

## 13. Search and Filter Logic

## 13.1 Global Search
System should support search by:
- service name
- client name
- project name
- action name
- owner
- remark
- description

## 13.2 Filters
System should support filtering by:
- Project Status
- Action Status
- Priority
- Owner
- Assignee
- Service
- Date Range
- Upcoming Due
- Overdue Only

## 13.3 Sorting
Suggested sorting options:
- recently updated
- due date ascending
- due date descending
- highest priority
- owner name A-Z

---

## 14. Notification Logic
Notifications help users monitor deadlines.

## 14.1 Upcoming Due Rule
If:
- due_date is within 3 days
- and action is not Completed
- and action is not Cancelled

Then:
- show `Upcoming Due` alert

## 14.2 Overdue Rule
If:
- current date > due_date
- and action is not Completed
- and action is not Cancelled

Then:
- show `Overdue` alert

## 14.3 No Update Rule
If:
- no updates for X days, e.g. 7 days

Then:
- show `No Recent Update` warning

## 14.4 Notification Target
Alerts should be visible to:
- owner,
- assignee,
- manager,
- admin.

Optional in later phase:
- email notification
- LINE / Slack notification

---

## 15. Activity Log Logic
Every important change should create a log.

### Trigger Events
- project created
- project edited
- action created
- action edited
- status changed
- due date changed
- assignee changed
- owner changed
- progress updated
- project or action deleted

### Example Logs
- `Yee changed action status from Not Started to In Progress`
- `Yee changed due date from 2026-04-20 to 2026-04-25`
- `Yee created action Testing under project J&T`

---

## 16. Validation Rules
The system should validate the following:

### Project Validation
- project_name cannot be empty
- service_name cannot be empty
- owner is required
- start_date must be before or equal to due_date

### Action Validation
- project_id is required
- action_name cannot be empty
- assignee is required if workflow requires ownership
- start_date must be before or equal to due_date
- progress_percent must be between 0 and 100

### General Validation
- enum fields must use predefined options only
- date format should be stored in ISO format: `YYYY-MM-DD`
- phone number can be optional, but if provided should match format rules

---

## 17. Workflow

## 17.1 Main Workflow
1. User logs in
2. User opens dashboard
3. User creates a project
4. User adds actions under the project
5. User assigns owner / assignee
6. User updates action status and progress over time
7. System recalculates project status and progress
8. Dashboard, board, table, and gantt refresh automatically
9. System highlights upcoming due and overdue items
10. Manager reviews workload and project risks

---

## 17.2 Flow Summary
### Create Project Flow
- Create project
- Save project
- Open project detail
- Add actions
- Start monitoring

### Update Action Flow
- Open project detail
- Open action
- Update status / due date / progress
- Save change
- Write activity log
- Recalculate project
- Refresh views

---

## 18. Sample Record Mapping
Below is how the current input should be transformed.

### Raw Input
| Service | Project | Action | Description | Project Status | Priority | Owner | Start Date | Due Date | Contact Number | Remark |
|---|---|---|---|---|---|---|---|---|---|---|
| Virtual Phone Number | J&T | Testing | xxxxxxxxxx | Start | High | Yee | 15 Apr | 20 Apr | 888888888 | |

### Project Record
| Field | Value |
|---|---|
| service_name | Virtual Phone Number |
| client_name | J&T |
| project_name | J&T |
| project_status | In Progress |
| priority | High |
| owner | Yee |
| start_date | 2026-04-15 |
| due_date | 2026-04-20 |
| contact_number | 888888888 |

### Action Record
| Field | Value |
|---|---|
| project_id | linked to J&T project |
| action_name | Testing |
| description | xxxxxxxxxx |
| action_status | In Progress |
| priority | High |
| assignee | Yee |
| start_date | 2026-04-15 |
| due_date | 2026-04-20 |

---

## 19. API Suggestion
This is optional, but useful for engineer planning.

### Project APIs
- `GET /projects`
- `POST /projects`
- `GET /projects/:id`
- `PUT /projects/:id`
- `DELETE /projects/:id`

### Action APIs
- `GET /projects/:id/actions`
- `POST /projects/:id/actions`
- `PUT /actions/:id`
- `DELETE /actions/:id`

### Log APIs
- `GET /projects/:id/logs`
- `GET /actions/:id/logs`

### Dashboard APIs
- `GET /dashboard/summary`
- `GET /dashboard/charts`

---

## 20. Non-Functional Requirements
The system should also consider the following:

### Performance
- fast loading for dashboard
- pagination for large data sets
- filter and search should remain responsive

### Security
- role-based access control
- authentication required
- activity logging for important changes

### Scalability
- should support growing number of projects and actions
- should support additional services in the future

### Usability
- clean layout
- simple navigation
- easy status update
- clear overdue highlight

---

## 21. MVP Scope

## Phase 1, MVP
Must-have features:
- login
- dashboard summary
- project list
- project detail
- create / edit project
- create / edit action
- table view
- board view
- basic gantt view
- search and filter
- status logic
- progress logic
- activity log
- overdue and upcoming due alerts

## Phase 2
Nice-to-have features:
- export report
- email notifications
- advanced analytics
- attachment upload
- comment mentions
- drag-to-edit in gantt

## Phase 3
Future expansion:
- CRM contact module
- multi-team permission setup
- SLA tracking
- external API integration
- mobile responsive optimization

---

## 22. UI Recommendation
Suggested main navigation:
- Dashboard
- Projects
- Actions
- Board
- Gantt
- Reports
- Users
- Settings

Suggested design approach:
- clean business dashboard style,
- clear status colors,
- strong date visibility,
- compact table layout,
- easy access to project detail.

Suggested status colors:
- Not Started = Gray
- In Progress = Blue
- Pending = Orange
- Completed = Green
- On Hold = Purple
- At Risk / Overdue = Red
- Cancelled = Dark Gray

---

## 23. Engineering Notes
Important points for implementation:

1. Keep **Project** and **Action** as separate data entities.
2. Use the same data source for all views.
3. Project status should not rely only on manual input.
4. Activity log should be written automatically.
5. Use ISO date format in database.
6. Build the system so future modules can be added without changing the core structure.

---

## 24. Final Summary
This product is a **Project CRM and Monitoring Dashboard**.

Its main structure is:
- **Project** = main item
- **Action** = child task
- **Dashboard** = summary monitoring
- **Board / Table / List / Gantt** = different views of the same data
- **Activity Log** = tracking history
- **Notification** = due date monitoring

The most important logic is:
- one project can have many actions,
- every action update affects project progress and status,
- the system should visualize data clearly and help users follow up work faster.

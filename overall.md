# design.md

## Project Monitoring Dashboard
Clean, simple, easy-to-use web dashboard for monitoring multiple projects and tasks.

---

## 1. Product Goal

Build a project monitoring dashboard that helps users:

- see the overall status of all projects in one place
- manage multiple projects in the same workspace
- track task progress clearly across different views
- add and update projects/tasks easily
- switch between overview, list, board, gantt, and table views smoothly
- keep the interface clean, lightweight, and easy to scan

This product should feel professional, modern, and operationally useful, without looking crowded or overly complex.

---

## 2. Core Design Direction

### 2.1 Design Keywords
- Clean
- Minimal
- Easy to scan
- Operational
- Structured
- Fast to use

### 2.2 UX Principles
1. **Show important information first**  
   Status, assignee, priority, due date, progress, and customer should always be easy to spot.

2. **Reduce clutter**  
   Secondary information should be hidden, collapsed, or shown only when needed.

3. **Keep interaction simple**  
   Add Project, Add Task, edit status, drag task card, filter, and search should be obvious.

4. **Use one consistent visual language**  
   Same spacing, same status colors, same chip style, same card style across all views.

5. **Desktop-first layout**  
   Because this dashboard contains dense project data, the main experience should be optimized for desktop.

---

## 3. Information Architecture

Top-level navigation should include:

- Overview
- List
- Board
- Gantt
- Table

Global actions:
- Add Project
- Add Task
- Search
- Filter
- Sort
- Customize columns / view settings

---

## 4. Main Data Structure

## 4.1 Project
Each project should support these fields:

- Project ID
- Project Name
- Customer
- Owner
- Assignee
- Status
- Priority
- Start Date
- Due Date
- Progress
- Description
- Tags / Labels
- Created At
- Updated At

Optional:
- Budget
- Department
- Project Type
- Attachments
- Notes

## 4.2 Task
Each task should support these fields:

- Task ID
- Project ID
- Task Name
- Description
- Status
- Assignee
- Owner
- Customer
- Priority
- Start Date
- Due Date
- Date Time
- Progress
- Subtasks
- Comment Count
- Attachment Count
- Created At
- Updated At

Optional:
- Dependencies
- Activity Log
- Reminder
- Estimated Time
- Actual Time

---

## 5. Status System

Use a simple but clear status system.

Recommended default statuses:
- To Do
- In Progress
- On Hold
- Waiting Review
- Completed
- Cancelled

Status should appear as rounded chips with consistent colors.

Example color logic:
- To Do = light gray
- In Progress = blue
- On Hold = amber
- Waiting Review = purple
- Completed = green
- Cancelled = red-gray

---

## 6. Layout System

## 6.1 Page Width
- Max content width: `1440px`
- Horizontal page padding: `24px`
- Vertical page padding: `20px`
- Content gap between sections: `16px`

## 6.2 Top Header
Top header should contain:
- workspace / page title on the left
- view tabs in the middle or below title
- global tools on the right: search, filter, assignee filter, customize, add task

Header behavior:
- sticky on scroll
- white background
- subtle bottom border
- height around `64px`

## 6.3 General Spacing
- card padding: `16px`
- section gap: `16px`
- row height in tables/lists: `44px` to `48px`
- border radius: `12px`
- small chip radius: `999px`

---

## 7. Design System

## 7.1 Color Style
Base UI should be mostly neutral.

### Primary neutrals
- Background: `#F7F8FA`
- Surface: `#FFFFFF`
- Border: `#E5E7EB`
- Text Primary: `#111827`
- Text Secondary: `#6B7280`

### Accent
- Blue for active / selected states
- Green for complete
- Amber for warning / medium attention
- Red for overdue / critical
- Purple only for secondary workflow states like review

### Usage rule
Do not use too many strong colors at once.  
The UI should stay mostly white/gray, with color used only for meaning.

## 7.2 Typography
Recommended font:
- Inter
- or system sans-serif

Type scale:
- Page Title: `24px / 700`
- Section Title: `18px / 600`
- Card Title: `16px / 600`
- Body: `14px / 400`
- Small Meta Text: `12px / 400`

## 7.3 Shadows
Very subtle shadows only.
- cards: light shadow or border only
- avoid heavy floating UI

---

## 8. View Specifications

## 8.1 Overview Page

### Goal
Give users a fast summary of all projects.

### Layout
A clean vertical layout with 3 main sections:

#### Section A: KPI Summary Cards
Use 4 to 6 compact cards in one row.

Recommended cards:
- Total Projects
- Active Tasks
- Overdue Tasks
- Due Today
- Completed Tasks
- Completion Rate

Card spec:
- height: `96px`
- padding: `16px`
- border radius: `12px`
- value large, label small

#### Section B: Project Summary List
A list or card grid of projects showing:
- Project Name
- Customer
- Owner
- Status
- Progress bar
- Task count
- Due Date

Recommended layout:
- 2-column card grid on wide screen
- 1-column on smaller desktop

#### Section C: Upcoming / Risk Section
A smaller section below or right side for:
- overdue tasks
- tasks due today
- blocked projects
- recent updates

### Clean UI rule
Overview should not show every task in full detail.  
It should summarize, not overwhelm.

---

## 8.2 List View

### Goal
Show multiple projects, each with visible tasks and grouped progress.

### Structure
Projects should appear as collapsible sections.

Each project block contains:
- Project header
- task groups by status
- task rows inside each group

### Project Block
- full width card
- white background
- border radius `14px`
- padding `16px`
- gap between project blocks `16px`

### Project Header
Should show:
- Project Name
- quick summary of task count
- project status
- expand/collapse action
- optional 3-dot menu

Height:
- around `52px`

### Group Header
For task groups like To Do / In Progress / Completed
- smaller chip-style label
- count number
- subtle divider below

### Task Row
Recommended columns:
- Name
- Assignee
- Due Date
- Priority
- Progress

Recommended row height:
- `44px`

Recommended width distribution:
- Name: `40%`
- Assignee: `16%`
- Due Date: `14%`
- Priority: `12%`
- Progress: `18%`

### UX notes
- collapsed by default for very large project lists
- sticky header row when scrolling long project content
- overdue due dates should turn red
- allow inline editing for status, assignee, priority, due date

---

## 8.3 Board View

### Goal
Let users move tasks visually across workflow stages.

### Board Structure
Columns = status groups

Recommended default columns:
- To Do
- In Progress
- On Hold
- Waiting Review
- Completed

### Column Style
- fixed width: `300px` to `320px`
- min height: full viewport content area
- rounded background with very light tint
- gap between columns: `16px`

### Task Card Style
Each card should contain:
- Task Name
- Assignee avatar / initials
- Due Date
- Priority
- Customer or project name if needed

Card spec:
- min height: `88px`
- padding: `12px`
- radius: `12px`
- white background
- border: `1px solid #E5E7EB`

### Interaction
- drag and drop between columns
- update status automatically after drop
- smooth hover and lift effect
- show clear drop zone while dragging

### Clean UI rule
Do not overload cards with too many fields.  
Board cards should show only the most useful information.

---

## 8.4 Gantt View

### Goal
Show project and task timing in a clear timeline format.

### Layout
Split into 2 panels:

#### Left Panel
Tree structure:
- Project
- Task under project

Width:
- `320px` to `360px`

#### Right Panel
Timeline area:
- horizontally scrollable
- supports Day / Week / Month zoom

### Timeline Design
- project row height: `44px`
- task row height: `40px`
- clear grid lines
- current day marked with colored vertical line
- weekends slightly tinted
- task bars use status-based color or one neutral color with status tag

### Gantt Bars
Should support:
- drag left/right to reschedule
- resize to adjust duration
- show start and due date on hover
- show task name beside or inside the bar

### Clean UI rule
Keep the left data tree simple.  
Only show name and maybe status icon, not too many columns in the gantt sidebar.

---

## 8.5 Table View

### Goal
Show dense task data in one structured spreadsheet-like view.

### Recommended Columns
- Task Name
- Project
- Customer
- Assignee
- Owner
- Status
- Priority
- Start Date
- Due Date
- Progress
- Updated At

### Table Style
- white surface
- compact but readable rows
- sticky header
- alternating row hover only, no strong zebra striping
- column resizing allowed

### Recommended row height
- `44px`

### Recommended width hints
- Task Name: `280px`
- Project: `180px`
- Customer: `160px`
- Assignee: `140px`
- Owner: `140px`
- Status: `140px`
- Priority: `110px`
- Start Date: `140px`
- Due Date: `140px`
- Progress: `120px`

### Interaction
- inline edit
- sort by each column
- filter by status / assignee / priority / customer
- search by task or project name

---

## 9. Create / Edit Flow

## 9.1 Add Project
Use a modal or right-side drawer.

Recommended:
- width `720px`
- 2-column form layout on desktop

### Fields
- Project Name
- Customer
- Owner
- Assignee
- Status
- Priority
- Start Date
- Due Date
- Description

Optional:
- Tags
- Notes
- Attachments

## 9.2 Add Task
Use a right-side drawer for quick creation.

Recommended:
- width `480px` to `520px`

### Fields
- Task Name
- Project
- Status
- Assignee
- Owner
- Customer
- Priority
- Start Date
- Due Date
- Date Time
- Description

Optional:
- Subtasks
- Reminder
- Attachment
- Dependency

### UX behavior
- allow quick create with only required fields
- allow advanced fields by expanding “More details”
- save button should stay fixed at bottom of drawer

---

## 10. Interaction Rules

## 10.1 Search
Global search should search:
- project name
- task name
- customer
- assignee

## 10.2 Filter
Filters should support:
- Status
- Assignee
- Owner
- Customer
- Priority
- Due Date
- Project

## 10.3 Sort
Sort options:
- Due Date
- Priority
- Updated At
- Created At
- Project Name

## 10.4 Quick Actions
For task rows/cards:
- Edit
- Change Status
- Assign User
- Duplicate
- Delete

---

## 11. Component Recommendations

Recommended reusable components:
- TopHeader
- ViewTabs
- KPIStatCard
- ProjectCard
- ProjectAccordion
- StatusChip
- PriorityChip
- ProgressBar
- TaskRow
- TaskCard
- GanttRow
- DataTable
- FilterBar
- SearchInput
- DrawerForm
- EmptyState

---

## 12. Clean UI Rules

To keep the dashboard clean and easy to use:

1. use white space generously
2. show only key fields in each view
3. avoid too many borders and bright colors
4. keep one primary action button visible, such as Add Task
5. use chips and icons to reduce text heaviness
6. collapse secondary details by default
7. keep column names and labels short
8. keep the same status colors across all views
9. avoid full-screen modal overload
10. let users customize visible columns in table/list view

---

## 13. Responsive Behavior

### Desktop
Primary version, full functionality

### Tablet
- keep Overview, List, Table
- Board horizontally scrollable
- Gantt simplified

### Mobile
- focus on Overview and simple List only
- avoid full gantt editing on mobile
- use stacked task cards instead of dense table

---

## 14. Recommended MVP Scope

For version 1, prioritize:

1. Overview
2. List
3. Board
4. Table
5. Add Project / Add Task
6. Search / Filter / Sort
7. Basic Gantt timeline

Advanced features can come later:
- dependencies
- comments
- file attachments
- notifications
- activity log
- role permissions
- automation

---

## 15. Visual Reference Summary

Based on the reference style:
- clean white workspace
- light gray background
- rounded blocks
- simple status chips
- compact top toolbar
- structured views with low visual noise
- clear spacing between project sections
- data-first layout, not decoration-first

This dashboard should feel like a lighter, cleaner, easier version of a project management tool, focused on monitoring and execution.

---

## 16. Virtual Phone Testing Process

This dashboard should also support an end-to-end testing process for Virtual Phone Number projects such as Flash and J&T, so the team can manage execution, evidence, defects, and go-live readiness in one workflow.

### 16.1 End-to-End Flow

```text
Customer / Project Setup
   ->
Preparing Test
   ->
Test Case Assignment
   ->
X Number Binding Ready
   ->
Call Execution
   ->
Call Log Validation
   ->
Passed or Issue Found
   ->
Fixing / Retesting
   ->
Completed / Ready for Production
```

### 16.2 Stage Definitions

| Stage | Purpose | Exit Criteria |
|---|---|---|
| First Discussion | Confirm customer scope, use case, owner, and testing timeline | Scope, owner, and next action are agreed |
| Preparing Test | Prepare test cases, test data, X numbers, and dependencies | Required test cases, numbers, and environment are ready |
| In Testing | Execute planned test scenarios | Test result, evidence, and call behavior are recorded |
| Issue Found | Track failed scenarios or missing dependencies | Issue is assigned with priority and action owner |
| Retesting | Run the same scenario again after a fix | Retest result is updated to pass or fail |
| Passed | Confirm that the scenario meets expected behavior | Expected result, evidence, and log validation are complete |
| Completed | Close the testing cycle for the customer or project | No blocking issues remain and report summary is complete |
| On Hold | Pause work due to dependency, customer delay, or internal blocker | Blocking condition is cleared and the plan is resumed |

### 16.3 Test Execution Cycle

1. Create or confirm the customer project, owner, testing period, and current status.
2. Define the test case list with expected result, scenario owner, and evidence requirement.
3. Assign X numbers to the correct A+B pair and verify binding start time and expiry time.
4. Execute the call scenario and capture actual result, screenshots, call recording, or supporting logs.
5. Validate that the call log is generated correctly, including call status, duration, displayed number, and recording availability if required.
6. If the scenario fails, create an issue immediately and link it back to the related test case.
7. Move the item to retesting after a fix, then update the final result and project readiness summary.

### 16.4 Operational Rules

- A test case should only be marked as `Pass` when expected result, actual behavior, and supporting evidence are all complete.
- A failed test case should always create or link to an issue so the team can trace root cause and retest status.
- A blocked test case should stay visible on the testing board until the missing dependency is resolved.
- X number usage should always show the current customer, A number, B number, binding status, start time, and expiry time.
- Call log validation should cover success and failure cases, not only successful calls.
- Go-live readiness should be based on test progress, open issue severity, retest result, and the latest report summary.

### 16.5 Required Dashboard Support

The dashboard should make this process visible across the main modules:

- `Overview`: total test cases, passed, failed, pending, active X numbers, call success rate, and open issues.
- `Customer Detail`: testing stage, owner, technical PIC, business PIC, priority, and next action.
- `Test Case Management`: scenario tracking, expected result, actual result, evidence, remark, and linked issue.
- `X Number Management`: active bindings, expiry status, reuse status, and number availability.
- `Call Log Monitoring`: call records, duration, status, recording link, and log completeness.
- `Issue Tracker`: issue type, impact, priority, owner, solution, and retest result.
- `Testing Board`: `Not Started`, `In Testing`, `Issue Found`, `Fixing`, `Retesting`, `Passed`, and `Blocked`.
- `Report Summary`: testing summary, key progress, key issues, business impact, next step, and go-live readiness.

### 16.6 Readiness Questions

Before moving a customer from testing to production, the dashboard should help the team answer:

- Are all planned test cases executed and clearly marked as pass, fail, blocked, or need retest?
- Are all active X numbers mapped correctly and behaving as expected for the assigned A+B pair?
- Are call logs complete enough to verify routing, duration, call status, and evidence?
- Which issues are still open, and which ones are severe enough to block production?
- Has every fixed issue been retested and recorded in the final report?

---

## 17. Final Design Statement

The dashboard should help users understand:
- what projects exist
- what tasks are inside each project
- who owns what
- what is in progress
- what is overdue
- what needs attention next
- which tests have passed or failed
- which issues still block go-live readiness

The visual style should stay minimal and operational, so users can work fast without feeling overwhelmed.

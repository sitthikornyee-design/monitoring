# design.md

## Project Monitoring Dashboard Design Structure

> Reference direction: layout and information structure inspired by the provided CRM dashboard screenshot
> Scope of this document: **layout, page structure, UI regions, navigation structure, content hierarchy, and display patterns only**
> Excluded: backend logic, database schema, API, permission logic, and detailed business workflow

---

## 1. Design Goal

เว็บไซต์นี้ควรถูกออกแบบให้เป็น **Project Monitoring Dashboard / CRM Workspace** ที่เน้น 3 อย่างหลัก

1. เห็นภาพรวมของ project ได้เร็ว
2. เข้าไปจัดการรายละเอียดของแต่ละ project ได้ง่าย
3. สลับมุมมองการดูข้อมูลได้หลายแบบโดยยังใช้โครงสร้างเดียวกัน

แนวทางภาพรวมของ layout ควรเป็นแบบ **workspace dashboard** เหมือนเครื่องมือจัดการงานสมัยใหม่ คือมี sidebar ทางซ้าย, header ด้านบน, content area กลาง, และ content หลักในรูปแบบ table-first layout

---

## 2. Overall Layout Structure

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Global Top Bar                                                             │
├───────────────┬─────────────────────────────────────────────────────────────┤
│ Left Sidebar  │ Main Workspace Header                                      │
│               ├─────────────────────────────────────────────────────────────┤
│               │ View Tabs + Toolbar                                         │
│               ├─────────────────────────────────────────────────────────────┤
│               │ Main Content Area                                           │
│               │ - Grouped Table / List / Board / Gantt                      │
│               │ - Inline Add Row                                            │
│               │ - Section Grouping                                           │
│               │ - Scrollable Data Region                                    │
│               ├─────────────────────────────────────────────────────────────┤
│               │ Optional Floating Utilities / Support                       │
└───────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 3. Page-Level Layout Breakdown

### 3.1 Global Top Bar
แถบบนสุดใช้สำหรับข้อมูลระดับระบบ และ utility actions

**Purpose**
- แสดง system announcement หรือ notice
- แสดง account-related utility
- ใช้เป็น global utility strip ที่อยู่เหนือ workspace ทั้งหมด

**Recommended elements**
- System notice / announcement text
- Action links เช่น resend, edit setting, help
- Utility icons ด้านขวา เช่น notification, settings, search, profile

**Design notes**
- ความสูงต่ำกว่าหลักของ header
- สีพื้นหลังควรต่างจาก content area ชัดเจน
- ไม่ควรมีข้อมูลหนาแน่นเกินไป

---

### 3.2 Left Sidebar
Sidebar เป็น navigation หลักของระบบ

**Purpose**
- พาผู้ใช้ไปยัง module ต่าง ๆ
- แสดง workspace context
- ทำให้ระบบดูเป็น software platform มากกว่า single-page dashboard

**Recommended sidebar structure**

```text
Sidebar
- Workspace / Product switcher
- Main menu section
  - Dashboard
  - Projects
  - Clients
  - Activities
  - Reports
- Secondary tools section
  - Automations
  - AI tools / assistant
  - Templates
- Favorites / quick access
- Workspace selector
- Bottom utility links
```

**Layout rules**
- Sidebar fixed ทางซ้าย
- มี section header แยกกลุ่มเมนู
- Active menu ต้องมี visual highlight
- รองรับ collapse ได้ในอนาคต
- ความกว้างควรคงที่

**Visual behavior**
- รายการที่ active ใช้ background tint หรือ left accent bar
- Icon + label ทุกเมนู
- Section spacing ชัดเจน

---

### 3.3 Main Workspace Header
ส่วนหัวของหน้าหลักใน content area

**Purpose**
- บอกว่าผู้ใช้กำลังอยู่ในหน้าอะไร
- แสดง context ของ board / project space / workspace ปัจจุบัน
- รวม quick actions ระดับหน้า

**Recommended elements**
- Page title เช่น `Client Projects`
- Dropdown หรือ switcher สำหรับเปลี่ยน dataset / board / workspace
- Page-level actions ด้านขวา เช่น integrate, automate, invite, more

**Structure**

```text
Workspace Header
- Left
  - Page title
  - Context dropdown
- Right
  - Helper tools
  - Integration actions
  - Invite / share
  - More menu
```

**Design notes**
- วางเหนือ tabs และ toolbar
- ใช้ spacing โปร่ง อ่านง่าย
- title ต้องเด่นที่สุดใน page content area

---

### 3.4 View Tabs Row
แถวสำหรับสลับมุมมองข้อมูล

**Purpose**
- ให้ user สลับการดูข้อมูลจาก dataset เดิมไปเป็นคนละ view
- เหมาะกับ project data ที่ต้องดูทั้ง table, board, gantt

**Recommended tabs**
- Main Table
- Board
- Gantt
- Calendar
- Activity Log
- Files

**Design notes**
- ใช้ tab bar ใต้ workspace header
- Active tab มี underline หรือ color emphasis
- ควรมีปุ่ม `+` สำหรับเพิ่ม custom view ในอนาคต

---

### 3.5 Action Toolbar
แถวเครื่องมือสำหรับจัดการข้อมูลในมุมมองปัจจุบัน

**Purpose**
- สร้าง project ใหม่
- search / filter / group / sort ข้อมูล
- เป็น control layer ของ table หรือ view ปัจจุบัน

**Recommended elements**
- Primary button `New Project`
- Search input
- Person / Owner filter
- General filter
- Group by
- Sort
- More menu

**Structure**

```text
Action Toolbar
- Left
  - Primary CTA button
  - Search
  - Quick filters
- Right
  - View settings
  - More actions
```

**Design notes**
- Toolbar ต้อง sticky ได้ถ้าข้อมูลยาว
- ปุ่มสำคัญควรอยู่ซ้ายและเห็นง่าย
- filter และ search ต้องอยู่เหนือ table โดยตรง

---

## 4. Main Content Structure

Main content ของ reference นี้เป็น **grouped table layout** ซึ่งเหมาะมากสำหรับ project monitoring

### 4.1 Grouped Section Layout
ข้อมูลถูกแบ่งเป็น group เช่น
- New Projects
- Completed
- Delayed
- On Hold

**Purpose**
- แยก project ตามสถานะใหญ่
- ช่วยให้ user scan งานได้เร็ว
- ทำให้ table ไม่ดูเป็นก้อนเดียว

**Recommended structure**

```text
Main Content
- Group Section
  - Group Header
  - Table Header
  - Table Rows
  - Add Row
- Group Section
  - Group Header
  - Table Header
  - Table Rows
  - Add Row
```

**Group header should include**
- Group title
- Collapse / expand icon
- Optional count badge
- Optional color accent per group

---

### 4.2 Table-First Data Layout
ในหน้า reference ตัว content หลักเป็น table ที่มีหลาย column

**Recommended columns for your project dashboard**
- Project
- Owner
- Priority
- Timeline
- Status
- Contact
- Client / Account
- Action Count
- Progress
- Remark

**Important layout rule**
- Table ต้องเป็น core view ของหน้า
- แถวหนึ่งควรแทน 1 project หรือ 1 action ตาม view ที่เลือก
- คอลัมน์สำคัญต้องอยู่ซ้าย
- ข้อมูลที่เป็น status ใช้ badge / pill / chip

---

### 4.3 Inline Add Row
ใต้แต่ละ group ควรมีแถวสำหรับเพิ่มข้อมูลใหม่ทันที

**Purpose**
- ช่วยให้เพิ่ม project ได้เร็ว
- ลด friction ในการใช้งาน

**Pattern**
- `+ Add project`
- `+ Add action`

**Design notes**
- แสดงเป็น row สุดท้ายของแต่ละ group
- ใช้ text button style
- เมื่อกดควรเปิด inline form หรือ modal

---

## 5. Recommended Page Regions in Detail

### Region A: Sidebar Navigation
โครงสร้างแนะนำ

```text
- Logo / Product Name
- Main Navigation
  - Dashboard
  - Projects
  - Tasks
  - Clients
  - Reports
- Tool Section
  - Automations
  - AI Assistant
  - Workflows
- Workspace Section
  - Current Workspace
  - Other Spaces
- Favorites / Shortcuts
```

### Region B: Workspace Header
โครงสร้างแนะนำ

```text
- Page Title
- Optional dropdown selector
- Page tools
- User actions
```

### Region C: View Tabs
โครงสร้างแนะนำ

```text
- Table
- Board
- Gantt
- Calendar
- Logs
```

### Region D: Toolbar
โครงสร้างแนะนำ

```text
- New Project button
- Search
- Owner filter
- Status filter
- Group by
- More
```

### Region E: Grouped Data Area
โครงสร้างแนะนำ

```text
- Group Header
- Table Header
- Data Rows
- Add Row
```

### Region F: Floating Utility
อาจมีปุ่มหรือ widget ลอย เช่น
- Support
- AI help
- Quick create

---

## 6. Layout Hierarchy Recommendation

```text
Page
├─ GlobalTopBar
├─ AppShell
│  ├─ Sidebar
│  └─ MainPanel
│     ├─ WorkspaceHeader
│     ├─ ViewTabs
│     ├─ ActionToolbar
│     ├─ ContentViewport
│     │  ├─ GroupSection
│     │  │  ├─ GroupHeader
│     │  │  ├─ DataTableHeader
│     │  │  ├─ DataRows
│     │  │  └─ AddRowButton
│     │  └─ GroupSection
│     └─ FloatingUtility
```

---

## 7. Screen Behavior and Layout Rules

### 7.1 Fixed vs Scrollable Areas
**Fixed**
- Top bar
- Sidebar
- Main page header
- Toolbar (optional sticky)

**Scrollable**
- Main data area
- Table rows
- Group sections

### 7.2 Horizontal Scroll
เพราะ table มีหลาย column จึงควรออกแบบให้รองรับ horizontal scroll โดยไม่ทำให้ layout พัง

**Recommendation**
- Table region เป็น scroll container
- Sidebar และ page header ไม่ควรเลื่อนตามแนวนอน

### 7.3 Responsive Behavior
สำหรับ desktop-first system แบบนี้ ควร prioritize desktop ก่อน

**Desktop**
- แสดง full sidebar
- แสดง full toolbar
- แสดงหลาย column ได้

**Tablet**
- Sidebar ยุบได้
- Toolbar บางส่วนซ่อนใน dropdown
- Table บาง column collapse ได้

**Mobile**
- ไม่ต้องเป็น priority สำหรับ version แรก
- ถ้าทำ later phase แนะนำเปลี่ยนเป็น card list แทน wide table

---

## 8. Information Architecture Recommendation

สำหรับเว็บของคุณ สามารถจัดโครงสร้างหน้าแบบนี้

```text
Main App
- Dashboard
- Projects
  - Main Table View
  - Board View
  - Gantt View
  - Project Detail
- Clients
- Activities
- Reports
- Settings
```

### Recommended primary navigation for your case
- Dashboard
- Projects
- Actions
- Clients
- Activity Log
- Reports

---

## 9. Table Structure Recommendation

### 9.1 Standard Project Table Header
```text
| Select | Project | Owner | Priority | Timeline | Status | Contact | Client | Progress | Remark |
```

### 9.2 Row Behavior
แต่ละ row ควร support
- row click เพื่อเข้า detail page
- quick edit บาง field ได้
- status update ได้จาก cell
- expand row เพื่อดู action ย่อยได้ในอนาคต

### 9.3 Group Example
```text
New Projects
- Project A
- Project B
- + Add Project

In Progress
- Project C
- Project D
- + Add Project

Completed
- Project E
- + Add Project
```

---

## 10. Layout Style Direction

แม้เอกสารนี้จะไม่ลงรายละเอียดเรื่อง visual design มาก แต่ layout นี้ควรใช้ style direction แบบนี้

### Keywords
- clean
- structured
- SaaS-like
- data-first
- professional
- modern workspace

### Visual characteristics
- พื้นหลังรวมค่อนข้างสว่าง
- card / panel ขอบมนเล็กน้อย
- เส้นแบ่ง section ชัด
- spacing โปร่ง
- table เป็นพระเอกของหน้า
- ใช้สีเพื่อบอกสถานะ ไม่ใช่ตกแต่งเกินจำเป็น

---

## 11. Suggested Layout Modules for Engineer

### Core layout modules
- `GlobalTopBar`
- `Sidebar`
- `WorkspaceHeader`
- `ViewTabs`
- `ActionToolbar`
- `GroupedTableSection`
- `DataTable`
- `FloatingUtilityButton`

### Optional reusable layout modules
- `PageShell`
- `ContentContainer`
- `StickyToolbar`
- `ScrollableTableArea`

---

## 12. Example Layout Blueprint for Your Website

```text
Project Monitoring Dashboard

Top Bar
- system notice
- notification
- settings
- profile

Left Sidebar
- Dashboard
- Projects
- Actions
- Clients
- Reports
- Activity Log

Main Area
- Title: Client Projects
- Tabs: Main Table / Board / Gantt
- Toolbar: New Project / Search / Owner / Filter / Group By
- Group 1: New Projects
  - rows
  - add row
- Group 2: Completed
  - rows
  - add row
- Floating support/help button
```

---

## 13. Scope Boundary of This Design File

เอกสารนี้ตั้งใจโฟกัสเฉพาะ
- layout structure
- navigation structure
- page hierarchy
- content regions
- display behavior
- table grouping structure

เอกสารนี้ยังไม่ครอบคลุม
- data model logic
- business rules
- backend structure
- API design
- database schema
- authentication flow

---

## 14. Final Recommendation

ถ้าจะอิงจาก reference นี้สำหรับเว็บของคุณ ควรใช้หลักคิดนี้

1. ใช้ **left sidebar + top workspace header** เป็น framework หลักของทั้งระบบ
2. ใช้ **grouped table layout** เป็น main view เริ่มต้น
3. ใช้ **tabs** สำหรับสลับ view เช่น table, board, gantt
4. ใช้ **toolbar เหนือ content** สำหรับ create, search, filter, group
5. ใช้ **group section** เพื่อแยก status ให้อ่านง่าย
6. วางระบบทั้งหมดให้รู้สึกเป็น **workspace software** มากกว่าเว็บทั่ว ๆ ไป

---

## 15. Quick Summary for Build Direction

**Reference Layout Type**
- CRM workspace dashboard

**Primary Pattern**
- Fixed sidebar
- Workspace header
- Tabbed views
- Action toolbar
- Grouped data table

**Best fit for your project**
- project monitoring
- task tracking
- CRM-like account view
- multiple data visualization under one workspace


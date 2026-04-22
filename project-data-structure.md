# Project Data Structure and Logic Design

## 1. Objective
เอกสารนี้ใช้เพื่อกำหนดโครงสร้างข้อมูลและ logic สำหรับระบบ Project Management บนเว็บไซต์ โดยระบบต้องรองรับการสร้างโปรเจกต์ ติดตามความคืบหน้า บันทึกปัญหา และแสดงผลข้อมูลเดียวกันได้หลายรูปแบบ เช่น List, Board, Calendar, Gantt และ Table

---

## 2. Core Concept
แต่ละ Project จะประกอบด้วย 2 ส่วนหลัก

1. **Main Project Information**  
   ข้อมูลหลักของโปรเจกต์
2. **Project Update / Process Log**  
   ข้อมูลย่อยสำหรับบันทึกความคืบหน้า ปัญหา หมายเหตุ หรือ process ต่าง ๆ ภายใต้โปรเจกต์นั้น

แนวคิดหลักคือ
- 1 Project มีข้อมูลหลัก 1 ชุด
- 1 Project สามารถมีข้อมูลย่อยได้หลายรายการ
- ทุก View ต้องดึงข้อมูลจากฐานข้อมูลชุดเดียวกัน

---

## 3. Data Model Overview

### 3.1 Main Entity
- **Project** = ข้อมูลหลักของโปรเจกต์

### 3.2 Child Entity
- **Project Update** = ข้อมูลย่อยที่ผูกกับ Project

### Relationship
- 1 Project : Many Project Updates

---

## 4. Main Project Information Structure

ข้อมูลหลักของแต่ละ Project ควรมี field ดังนี้

| Field Name | Type | Description |
|---|---|---|
| project_id | UUID / ID | รหัสประจำโปรเจกต์ |
| project_name | String | ชื่อโปรเจกต์ |
| status | Enum / String | สถานะปัจจุบันของโปรเจกต์ |
| assignee | User / String | ผู้รับผิดชอบงานหลัก |
| owner | User / String | เจ้าของโปรเจกต์ |
| priority | Enum / String | ระดับความสำคัญ เช่น Low, Medium, High, Urgent |
| customer | String / Reference | ชื่อลูกค้าหรือ account ที่เกี่ยวข้อง |
| start_date | Date | วันที่เริ่มต้นโปรเจกต์ |
| due_date | Date | วันที่ครบกำหนด |
| created_at | DateTime | วันที่สร้างรายการ |
| updated_at | DateTime | วันที่แก้ไขล่าสุด |

### Optional Fields ที่แนะนำเพิ่ม

| Field Name | Type | Description |
|---|---|---|
| description | Text | รายละเอียดสรุปของโปรเจกต์ |
| progress_percent | Number | เปอร์เซ็นต์ความคืบหน้า |
| tags | Array | ป้ายกำกับ เช่น urgent, testing, client follow-up |
| department | String | ฝ่ายที่รับผิดชอบ |
| project_type | String | ประเภทของโปรเจกต์ |

---

## 5. Project Update / Process Log Structure

Project หนึ่งสามารถมี Update Log ได้หลายรายการ เพื่อใช้บันทึก process ระหว่างทำงาน

| Field Name | Type | Description |
|---|---|---|
| update_id | UUID / ID | รหัสของ update log |
| project_id | UUID / ID | ใช้เชื่อมกับ project หลัก |
| update_title | String | หัวข้อของ update |
| update_type | Enum / String | ประเภท เช่น Progress, Issue, Note, Risk, Follow-up |
| description | Text | รายละเอียดของ update |
| related_status | String | สถานะที่เกี่ยวข้อง ณ เวลานั้น |
| created_by | User / String | ผู้สร้าง update |
| created_at | DateTime | วันที่และเวลาที่บันทึก |
| attachment_url | String | ไฟล์แนบหรือ link ที่เกี่ยวข้อง |

### ตัวอย่าง Update Type
- Progress
- Issue
- Note
- Risk
- Delay
- Follow-up
- Decision

---

## 6. Suggested Database Structure

### Table 1: projects
```text
projects
- project_id (PK)
- project_name
- status
- assignee
- owner
- priority
- customer
- start_date
- due_date
- description
- progress_percent
- created_at
- updated_at
```

### Table 2: project_updates
```text
project_updates
- update_id (PK)
- project_id (FK -> projects.project_id)
- update_title
- update_type
- description
- related_status
- created_by
- created_at
- attachment_url
```

---

## 7. Data Rules

### 7.1 Project Rules
- ทุก Project ต้องมี `project_id`
- ทุก Project ต้องมี field หลักอย่างน้อย: `project_name`, `status`, `assignee`, `owner`, `priority`, `customer`, `start_date`, `due_date`
- เมื่อมีการแก้ไขข้อมูลหลัก ต้องอัปเดต `updated_at`

### 7.2 Update Log Rules
- ทุก Update Log ต้องผูกกับ `project_id`
- 1 Project สามารถมีหลาย Update Log ได้
- Update Log ใช้เก็บ history ของความคืบหน้าและปัญหา ไม่ควรเขียนทับข้อมูลเดิม

---

## 8. Visualization Logic

ข้อมูลชุดเดียวกันต้องสามารถแสดงผลได้ 5 รูปแบบ

### 8.1 List View
ใช้ดูรายการโปรเจกต์ทั้งหมดแบบลิสต์
- แสดงข้อมูลหลักของ Project
- กดเข้าไปดูรายละเอียดและ update log ได้

### 8.2 Board View
ใช้แสดงแบบ Kanban ตาม Status
- แบ่ง column ตาม status
- แต่ละ card แสดง project_name, assignee, priority, due_date
- เมื่อเปิด card ต้องเห็น update log ทั้งหมด

### 8.3 Calendar View
ใช้แสดงตามวันที่
- ใช้ start_date และ due_date เป็นตัวอ้างอิง
- เมื่อคลิก event ต้องเห็นข้อมูลหลักและข้อมูลย่อยของ project

### 8.4 Gantt View
ใช้ดู timeline ของโปรเจกต์
- แสดงช่วงเวลาเริ่มต้นถึงสิ้นสุด
- ใช้ start_date และ due_date
- เมื่อคลิกแถบของโปรเจกต์ ต้องดูรายละเอียดได้

### 8.5 Table View
ใช้ดูข้อมูลแบบละเอียด
- รองรับ sort, filter, search
- ควรมี row expand เพื่อดู update log ของแต่ละ project

---

## 9. UX Logic

### Create Project
เมื่อผู้ใช้สร้าง Project ใหม่
1. กรอกข้อมูลหลักของโปรเจกต์
2. ระบบสร้าง `project_id`
3. ระบบบันทึกลงตาราง `projects`
4. ผู้ใช้สามารถเพิ่ม update log หลังจากสร้าง project ได้ทันที

### Add Project Update
เมื่อผู้ใช้เพิ่ม update ภายใต้ project
1. เลือก project ที่ต้องการ
2. กรอกข้อมูล update เช่น title, type, description
3. ระบบบันทึกลง `project_updates`
4. update นี้ต้องแสดงในหน้ารายละเอียด project ทุก view

### Edit Project
- แก้ไขได้เฉพาะข้อมูลหลักของ project
- ต้อง update `updated_at`
- ไม่ควรลบ history ของ update log โดยไม่จำเป็น

---

## 10. Recommended Filters and Search

ระบบควรรองรับการ filter และ search อย่างน้อยดังนี้
- Status
- Assignee
- Owner
- Priority
- Customer
- Start Date
- Due Date
- Update Type

---

## 11. Example Hierarchy

```text
Project A
├── Main Information
│   ├── Status: In Progress
│   ├── Assignee: Mark
│   ├── Owner: Admin
│   ├── Priority: High
│   ├── Customer: ABC Company
│   ├── Start Date: 2026-04-21
│   └── Due Date: 2026-04-30
│
├── Update 1.1
│   ├── Type: Progress
│   ├── Title: Initial discussion completed
│   └── Description: Client confirmed testing scope
│
├── Update 1.2
│   ├── Type: Issue
│   ├── Title: Delay in data submission
│   └── Description: Waiting for customer response
│
└── Update 1.3
    ├── Type: Follow-up
    ├── Title: Follow up with engineer
    └── Description: Confirm API integration timeline
```

---

## 12. Summary for Engineer

Please design the system based on the following structure:

- One **Project** contains one set of **main project information**
- One **Project** can contain multiple **Project Update / Process Log** records
- All views must use the same source of truth
- Data must be visualized in:
  - List
  - Board
  - Calendar
  - Gantt
  - Table
- Every view must support both:
  - Main project fields
  - Related child update records

The system should be structured in a scalable way so more child sections can be added later, such as:
- 1.1 Update Log
- 1.2 Task List
- 1.3 Attachments
- 1.4 Comments
- 1.5 Activity History

---

## 13. Future Expansion Suggestion
ในอนาคตสามารถขยาย child modules ใต้ project ได้อีก เช่น

- **Tasks** สำหรับแยกงานย่อยในโปรเจกต์
- **Attachments** สำหรับไฟล์แนบ
- **Comments** สำหรับการคุยกันภายในทีม
- **Activity History** สำหรับเก็บประวัติการเปลี่ยนแปลง
- **Risk Tracker** สำหรับติดตามความเสี่ยง

เพื่อให้ระบบรองรับการทำงานจริงได้ละเอียดมากขึ้น

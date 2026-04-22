# Monitoring Website Data Structure and Logic Design

## 1. Objective

เอกสารนี้จัดโครงสร้างข้อมูลของ Monitoring Website ใหม่ โดยอิงจากแนวคิดใน `project-data-structure.md` เพื่อให้ระบบติดตามงานทั้งหมดใช้โครงสร้างกลางเดียวกัน ไม่ว่าจะเป็นงานประเภท Virtual Phone, One-Click Login, Customer Pipeline หรือ Business Support

เป้าหมายคือให้ทุกงานถูกจัดเก็บเป็นรูปแบบเดียวกัน สามารถติดตามความคืบหน้า บันทึกปัญหา บันทึกการตัดสินใจ และแสดงผลผ่านหลายมุมมอง เช่น Dashboard, List, Board, Calendar, Gantt และ Table โดยอ้างอิงจากข้อมูลชุดเดียวกัน

---

## 2. Core Concept

แต่ละรายการในระบบจะถูกมองเป็น 1 `Project` หรือ 1 monitoring record ที่ประกอบด้วย 2 ส่วนหลัก

1. `Main Project Information`
   ข้อมูลหลักของโปรเจกต์หรืองาน เช่น ชื่อลูกค้า ผู้รับผิดชอบ สถานะ ประเภทงาน วันที่เริ่ม และกำหนดส่ง
2. `Project Update / Process Log`
   ข้อมูลย่อยที่ใช้เก็บ timeline การทำงาน ความคืบหน้า ปัญหา ความเสี่ยง ข้อสรุป การติดตามผล และ feedback

แนวคิดหลักของระบบคือ

- 1 Project มีข้อมูลหลัก 1 ชุด
- 1 Project สามารถมี update log ได้หลายรายการ
- ทุก view ต้องใช้ข้อมูลจาก source of truth ชุดเดียวกัน
- ความแตกต่างของแต่ละ module จะถูกจัดการผ่าน `project_type` และ field เฉพาะทาง ไม่ใช่แยกโครงสร้างหลักคนละแบบ

---

## 3. Business Scope and Project Types

ระบบนี้รองรับงานหลัก 4 ประเภท โดยใช้ `project_type` เป็นตัวแยกบริบทธุรกิจ

| Project Type | ใช้สำหรับ | ตัวอย่างข้อมูลเฉพาะ |
|---|---|---|
| `virtual_phone` | ติดตามโปรเจกต์ Virtual Phone และการจัดการ X Number | service type, x number, test readiness |
| `one_click_login` | ติดตาม integration และ testing ของ One-Click Login | platform, environment, SDK/API version |
| `customer_pipeline` | ติดตามโอกาสทางธุรกิจตั้งแต่ lead ถึง won/lost | opportunity value, probability, pipeline stage |
| `business_support` | ติดตาม support case, incident และการแก้ไขปัญหา | severity, SLA, workaround, final result |

การออกแบบแบบนี้ทำให้ Dashboard, Table และ Report สามารถรวมข้อมูลทุกประเภทเข้าด้วยกันได้ง่าย และยังสามารถ filter ตาม `project_type` เมื่อต้องการดูแบบเฉพาะ module

---

## 4. Data Model Overview

### 4.1 Main Entity

- `Project` = ข้อมูลหลักของงานที่ทีมต้องติดตาม

### 4.2 Child Entity

- `Project Update` = บันทึกย่อยที่ผูกกับ Project

### Relationship

- 1 Project : Many Project Updates

### Future Child Modules

ในอนาคตสามารถขยาย child modules ใต้ Project ได้เพิ่มเติม เช่น

- Number Assignment
- Test Cases
- Attachments
- Comments
- Activity History
- Risk Tracker

---

## 5. Main Project Information Structure

ข้อมูลหลักของแต่ละ Project ควรมี field กลางที่ใช้ร่วมกันทุก module ดังนี้

### 5.1 Core Fields

| Field Name | Type | Description |
|---|---|---|
| `project_id` | UUID / ID | รหัสประจำ project |
| `project_name` | String | ชื่อโปรเจกต์หรือชื่อรายการติดตาม |
| `project_type` | Enum / String | ประเภทงาน เช่น `virtual_phone`, `one_click_login`, `customer_pipeline`, `business_support` |
| `status` | Enum / String | สถานะงานระดับภาพรวม เช่น Not Started, In Progress, Blocked, Complete, On Hold |
| `stage` | Enum / String | ขั้นตอนของงาน ณ เวลานั้น เช่น Internal Testing, UAT, Negotiation, Investigating |
| `assignee` | User / String | ผู้รับผิดชอบงานหลัก |
| `owner` | User / String | เจ้าของรายการหรือเจ้าของ account |
| `priority` | Enum / String | ระดับความสำคัญ เช่น Low, Medium, High, Urgent |
| `customer` | String / Reference | ชื่อลูกค้าหรือ account ที่เกี่ยวข้อง |
| `product` | String | สินค้าหรือบริการหลักที่เกี่ยวข้อง |
| `start_date` | Date | วันที่เริ่มต้น |
| `due_date` | Date | วันที่ครบกำหนดหลัก |
| `created_at` | DateTime | วันที่สร้างรายการ |
| `updated_at` | DateTime | วันที่แก้ไขข้อมูลหลักล่าสุด |

### 5.2 Recommended Optional Fields

| Field Name | Type | Description |
|---|---|---|
| `description` | Text | สรุป scope หรือภาพรวมของงาน |
| `progress_percent` | Number | เปอร์เซ็นต์ความคืบหน้า |
| `next_action` | Text | ขั้นตอนถัดไปที่ต้องทำ |
| `blocker` | Text | ปัญหาหลักหรือสิ่งที่ทำให้งานติด |
| `customer_contact` | String | ผู้ติดต่อฝั่งลูกค้า |
| `business_owner` | String | ผู้ดูแลงานฝั่ง business |
| `sales_owner` | String | ผู้ดูแลโอกาสหรือ pipeline |
| `technical_owner` | String | ผู้ดูแลด้านเทคนิค |
| `external_partner` | String | คู่ค้าหรือ operator ที่เกี่ยวข้อง |
| `department` | String | หน่วยงานภายในที่รับผิดชอบ |
| `tags` | Array / Text | ป้ายกำกับ เช่น urgent, testing, launch-ready |
| `target_go_live_date` | Date | วันที่คาดว่าจะ go-live |

### 5.3 Module-Specific Optional Fields

Field ต่อไปนี้ใช้เฉพาะบาง `project_type` ตามบริบทของงาน

| Project Type | Additional Fields |
|---|---|
| `virtual_phone` | `service_type`, `x_number_total`, `x_number_range`, `assigned_number_owner`, `testing_stage`, `overall_readiness` |
| `one_click_login` | `app_name`, `platform_type`, `api_sdk_version`, `environment`, `integration_status`, `launch_recommendation` |
| `customer_pipeline` | `industry`, `opportunity_value`, `probability`, `last_contact_date`, `key_blocker`, `fit_level` |
| `business_support` | `ticket_id`, `severity`, `responsible_team`, `reported_by`, `sla_target_date`, `workaround`, `final_result` |

หมายเหตุ:

- หากต้องการเริ่มแบบ MVP สามารถเก็บ field เฉพาะทางเป็น optional columns ในตารางหลักได้ก่อน
- หากข้อมูลเชิงลึกเพิ่มมากขึ้นในอนาคต ค่อยแยก child tables ตาม module โดยยังผูกกับ `project_id` เดิม

---

## 6. Project Update / Process Log Structure

Project หนึ่งสามารถมี update log ได้หลายรายการ เพื่อเก็บ history ของการทำงานโดยไม่เขียนทับข้อมูลเดิม

| Field Name | Type | Description |
|---|---|---|
| `update_id` | UUID / ID | รหัสของ update log |
| `project_id` | UUID / ID | ใช้เชื่อมกับ project หลัก |
| `update_title` | String | หัวข้อสั้นของ update |
| `update_type` | Enum / String | ประเภทของ update |
| `description` | Text | รายละเอียดของ update |
| `related_status` | String | สถานะหรือ stage ที่เกี่ยวข้อง ณ เวลานั้น |
| `created_by` | User / String | ผู้บันทึกข้อมูล |
| `created_at` | DateTime | วันที่และเวลาที่บันทึก |
| `attachment_url` | String | ไฟล์แนบหรือลิงก์ที่เกี่ยวข้อง |

### Suggested Update Types

- Progress
- Issue
- Note
- Risk
- Delay
- Follow-up
- Decision
- Testing Result
- Customer Feedback
- Support Response

### Update Usage Examples

- Virtual Phone: บันทึกการ assign หมายเลข, test progress, issue และ readiness
- One-Click Login: บันทึกผล integration, failed cases, customer feedback และ go-live decision
- Customer Pipeline: บันทึก meeting summary, commercial update, negotiation note และ next action
- Business Support: บันทึก investigation, workaround, fix update, retest และ closure note

---

## 7. Suggested Database Structure

### Table 1: `projects`

```text
projects
- project_id (PK)
- project_name
- project_type
- status
- stage
- assignee
- owner
- priority
- customer
- product
- start_date
- due_date
- description
- progress_percent
- next_action
- blocker
- customer_contact
- business_owner
- sales_owner
- technical_owner
- external_partner
- department
- tags
- target_go_live_date
- service_type
- x_number_total
- x_number_range
- assigned_number_owner
- testing_stage
- overall_readiness
- app_name
- platform_type
- api_sdk_version
- environment
- integration_status
- launch_recommendation
- industry
- opportunity_value
- probability
- last_contact_date
- key_blocker
- fit_level
- ticket_id
- severity
- responsible_team
- reported_by
- sla_target_date
- workaround
- final_result
- created_at
- updated_at
```

### Table 2: `project_updates`

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

### Scalability Note

หากระบบเติบโตและข้อมูลเฉพาะทางเริ่มมีจำนวนมาก สามารถปรับเป็นโครงสร้างแบบนี้ได้โดยยังยึด `projects` เป็นแกนหลัก

- `projects`
- `project_updates`
- `project_number_assignments`
- `project_test_cases`
- `project_support_actions`
- `project_attachments`

---

## 8. Data Rules

### 8.1 Project Rules

- ทุก Project ต้องมี `project_id`
- ทุก Project ต้องมีอย่างน้อย `project_name`, `project_type`, `status`, `assignee`, `owner`, `priority`, `customer`, `start_date`, `due_date`
- เมื่อมีการแก้ไขข้อมูลหลัก ต้องอัปเดต `updated_at`
- `status` ใช้บอกสภาพรวมของงาน
- `stage` ใช้บอกขั้นตอนเชิง process หรือ workflow
- `start_date` และ `due_date` ต้องถูกใช้เป็นฐานข้อมูลสำหรับ Calendar และ Gantt view

### 8.2 Update Log Rules

- ทุก Update Log ต้องผูกกับ `project_id`
- 1 Project สามารถมีหลาย Update Log ได้
- Update Log ใช้เก็บ history ไม่ควรลบหรือเขียนทับโดยไม่จำเป็น
- Latest update ที่แสดงใน card, dashboard และ detail page ควรดึงจาก update log ล่าสุด

### 8.3 Module-Specific Validation Rules

- `virtual_phone` ควรมีข้อมูล `service_type` และข้อมูลหมายเลขเมื่อเกี่ยวข้อง
- `one_click_login` ควรมี `platform_type`, `environment` และข้อมูล integration
- `customer_pipeline` ควรมี `stage`, `probability` และ `next_action`
- `business_support` ควรมี `severity`, `responsible_team` และ `sla_target_date`

---

## 9. Visualization Logic

ข้อมูลชุดเดียวกันต้องสามารถแสดงผลได้หลายรูปแบบ โดยทุก view ใช้ `projects` และ `project_updates` เป็น source of truth ร่วมกัน

### 9.1 Dashboard

ใช้แสดงภาพรวมของระบบ เช่น

- Total customers
- Active projects
- Projects by project type
- Projects by stage
- Open issues
- Critical issues
- Tickets by status
- Pipeline value
- Recent updates

### 9.2 List View

ใช้ดูรายการ Project ทั้งหมดแบบลิสต์

- แสดงข้อมูลหลักของ Project
- กดเข้าไปดูรายละเอียดและ update log ได้

### 9.3 Board View

ใช้แสดงแบบ Kanban

- ค่า default ควรแบ่งตาม `status`
- บาง module สามารถสลับไปแบ่งตาม `stage` ได้ เช่น pipeline stages
- แต่ละ card ควรแสดง `project_name`, `customer`, `assignee`, `priority`, `due_date`, latest update

### 9.4 Calendar View

ใช้แสดงตามวันที่

- ใช้ `start_date`, `due_date` และ `target_go_live_date`
- เมื่อคลิก event ต้องเห็นข้อมูลหลักและ update log ล่าสุด

### 9.5 Gantt View

ใช้ดู timeline ของ Project

- แสดงช่วงเวลาเริ่มต้นถึงกำหนดส่ง
- ใช้ `start_date` และ `due_date`
- เมื่อคลิกแถบของ project ต้องเปิดดูรายละเอียดได้

### 9.6 Table View

ใช้ดูข้อมูลแบบละเอียด

- รองรับ sort, filter, search
- ควรมี row expand หรือ detail panel เพื่อดู update logs
- เหมาะสำหรับ export และ reporting

### 9.7 Detail View

หน้ารายละเอียดของแต่ละ Project ควรประกอบด้วย

- Main project information
- Timeline ของ project updates
- ข้อมูลเฉพาะทางของ module นั้น
- Next action, blocker, owner, due date
- เอกสารหรือ link ที่เกี่ยวข้องถ้ามี

---

## 10. UX Logic

### Create Project

เมื่อผู้ใช้สร้าง Project ใหม่

1. กรอกข้อมูลหลักของ Project
2. เลือก `project_type`
3. ระบบสร้าง `project_id`
4. ระบบบันทึกลงตาราง `projects`
5. ผู้ใช้สามารถเพิ่ม update log ได้ทันทีหลังจากสร้างรายการ

### Add Project Update

เมื่อผู้ใช้เพิ่ม update ภายใต้ Project

1. เลือก project ที่ต้องการ
2. กรอกข้อมูล update เช่น title, type, description
3. ระบบบันทึกลง `project_updates`
4. update นี้ต้องแสดงใน detail page และทุก view ที่ต้องใช้ latest activity

### Edit Project

- แก้ไขได้เฉพาะข้อมูลหลักของ project
- ต้อง update `updated_at`
- ไม่ควรลบ history ของ update log โดยไม่จำเป็น

### Alerts and Notifications

ระบบควรรองรับ alert อย่างน้อยดังนี้

- New issue created
- Critical issue created
- Project delayed
- Target go-live date approaching
- SLA overdue
- Testing stage not updated for too long
- X number allocation running low

---

## 11. Recommended Filters and Search

ระบบควรรองรับการ filter และ search อย่างน้อยดังนี้

- Project Type
- Status
- Stage
- Assignee
- Owner
- Priority
- Customer
- Product
- Start Date
- Due Date
- Severity
- Update Type

---

## 12. Dashboard KPIs and Reports

### 12.1 Recommended Dashboard KPIs

- Total customers
- Active projects
- Projects by project type
- Projects in testing
- Projects in UAT
- Live projects
- Open issues
- Critical issues
- Average issue resolution time
- Tickets by status
- Pipeline value
- Opportunities by stage
- Projects delayed vs on track

### 12.2 Report Types

- Virtual Phone project summary
- One-Click Login project summary
- Open issues summary
- Business support case summary
- Customer pipeline summary
- Monthly progress report

### 12.3 Export Options

- PDF
- Excel
- CSV

---

## 13. Roles and Access Control

### Suggested Roles

- Admin
- Business / Sales
- Project Manager / BD Owner
- Technical Team
- Viewer / Management

### Permission Examples

- Admin: full access
- Business / Sales: pipeline, customer info, project updates
- Project Manager / BD Owner: manage project details, follow-ups, reporting
- Technical Team: testing, issues, support updates
- Viewer / Management: read-only dashboard and reports

---

## 14. Example Hierarchy

```text
Project: ABC Virtual Phone Rollout
├── Main Information
│   ├── Project Type: virtual_phone
│   ├── Status: In Progress
│   ├── Stage: Customer Testing / UAT
│   ├── Assignee: Project Coordinator
│   ├── Owner: BD Owner
│   ├── Priority: High
│   ├── Customer: ABC Company
│   ├── Product: Virtual Phone
│   ├── Start Date: 2026-04-21
│   └── Due Date: 2026-04-30
│
├── Update 1
│   ├── Type: Progress
│   ├── Title: Internal testing completed
│   └── Description: Internal test cases passed and customer UAT started
│
├── Update 2
│   ├── Type: Issue
│   ├── Title: Delay in customer data confirmation
│   └── Description: Waiting for final number mapping from customer
│
└── Update 3
    ├── Type: Follow-up
    ├── Title: Confirm go-live checklist
    └── Description: Follow up with technical owner and customer contact
```

---

## 15. MVP Scope

สำหรับเวอร์ชันแรก ควรโฟกัสฟังก์ชันหลักดังนี้

- Project master record
- Project update / process log
- Dashboard summary
- Virtual Phone tracking
- One-Click Login tracking
- Customer pipeline tracking
- Business support tracking
- List, Board, Calendar, Gantt, Table views
- Search and filter
- Basic reports

---

## 16. Future Expansion

เมื่อระบบเริ่มนิ่ง สามารถขยายเพิ่มเติมได้ เช่น

- Number assignment child table
- Detailed testing case tracker
- SLA timer and overdue alerts
- Auto-generated weekly reports
- Issue trend analytics
- File attachment support
- Activity log / audit trail
- Role-based approval workflow
- Customer health scoring
- Integration with email or chat notifications

---

## 17. Product Vision

Monitoring Website ควรเป็น single source of truth ของทีมสำหรับการติดตาม project progress, issue management, customer pipeline และ operational visibility ในระบบเดียว

การใช้โครงสร้างแบบ `Project` + `Project Update / Process Log` จะช่วยให้ระบบขยายต่อได้ง่าย ลดความซ้ำซ้อนของข้อมูล และทำให้ทุกทีมเห็นข้อมูลชุดเดียวกันอย่างชัดเจนในทุกมุมมอง

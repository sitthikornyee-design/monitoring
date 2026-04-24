# Virtual Phone Number Testing Dashboard

## 1. Purpose

This dashboard is designed to monitor Virtual Phone Number testing for two customers: **Flash** and **J&T**.

The main goal is to track testing progress, manage X number usage, monitor call logs, identify issues, and summarize testing readiness before moving to production.

---

## 2. Dashboard Overview

The dashboard should provide a clear summary of the testing status across all customers.

### Key Metrics

- Total Customers
- Total Test Cases
- Passed Test Cases
- Failed Test Cases
- Pending Test Cases
- Active X Numbers
- Call Success Rate
- Open Issues

### Customer Summary

Each customer should be shown with the following information:

| Field | Description |
|---|---|
| Customer | Customer name, such as Flash or J&T |
| Service | Virtual Phone Number |
| Testing Stage | Current testing phase |
| Progress | Overall testing progress percentage |
| Success Rate | Percentage of successful calls |
| Open Issues | Number of unresolved issues |
| Owner | Person responsible for the project |
| Next Action | Next step required |

---

## 3. Main Website Pages

The website should include the following pages:

1. **Overview Dashboard**  
   Shows the overall testing performance for Flash and J&T.

2. **Customer List**  
   Displays all customers currently testing the Virtual Phone Number service.

3. **Customer Detail**  
   Shows detailed testing information for each customer.

4. **X Number Management**  
   Tracks which virtual numbers are assigned, active, expired, or available.

5. **Test Case Management**  
   Manages all test scenarios, expected results, actual results, and testing status.

6. **Call Log Monitoring**  
   Displays call records, call status, duration, and log completeness.

7. **Issue Tracker**  
   Tracks all problems found during testing and their resolution status.

8. **Testing Board**  
   Uses a Kanban-style board to monitor testing progress.

9. **Report Summary**  
   Summarizes testing results, key issues, next steps, and go-live readiness.

---

## 4. Dashboard Logic

The main data flow should be structured as follows:

```text
Customer
   ↓
Project / POC
   ↓
Test Case
   ↓
X Number Binding
   ↓
Call Log
   ↓
Issue
   ↓
Report
```

Each customer can have multiple projects or POCs.  
Each project can have multiple test cases.  
Each test case may use one or more X numbers.  
Each X number can generate multiple call logs.  
If a test case fails, an issue should be created and tracked.

---

## 5. Customer Detail Structure

Each customer page should include basic project information.

| Field | Description |
|---|---|
| Customer Name | Flash or J&T |
| Service Type | Virtual Phone Number |
| Model | AXB |
| Testing Period | Start date and end date |
| Owner | Internal project owner |
| Technical PIC | Technical person in charge |
| Business PIC | Business person in charge |
| Current Status | Current testing status |
| Priority | Project priority |
| Next Action | Required next step |

---

## 6. X Number Management

This section is used to monitor virtual number binding and usage.

### Required Fields

| Field | Description |
|---|---|
| X Number | Virtual phone number |
| Customer | Customer using this X number |
| A Number | Caller number |
| B Number | Receiver number |
| Binding Status | Current binding status |
| Start Time | Binding start time |
| Expiry Time | Binding expiry time |
| Current Status | Available, Active, Expired, or Error |

### X Number Logic

- One X number can only bind to one unique A+B pair at the same time.
- If the same A number needs to contact multiple B numbers at the same time, each pair needs a different X number.
- After unbinding, the X number can be reused for another unique A+B pair.
- The dashboard should clearly show whether each X number is available, active, expired, or has an error.

---

## 7. Test Case Management

This section is used to track all testing scenarios.

### Required Fields

| Field | Description |
|---|---|
| Test Case ID | Unique ID for each test case |
| Customer | Related customer |
| Scenario | Testing scenario |
| Expected Result | What should happen |
| Actual Result | What actually happened |
| Status | Test result status |
| Issue | Related issue, if any |
| Owner | Person responsible |
| Evidence | Screenshot, call log, or recording |
| Remark | Additional notes |

### Test Case Categories

| Category | Description |
|---|---|
| Basic Call Flow | Test whether A can call B through X successfully |
| Caller Restriction | Test whether only the correct A number can use X |
| Receiver Restriction | Test whether X connects only to the correct B number |
| Wrong Number Test | Test whether unauthorized numbers are blocked |
| Binding Test | Test whether A+B pair binds correctly with X |
| Reuse Test | Test whether X can be reused after unbinding |
| Auto-Unbind Test | Test whether X expires automatically after the set time |
| Call Log Test | Test whether call records are generated correctly |
| Concurrent Test | Test multiple pairs calling at the same time |
| Edge Case Test | Test missed calls, callbacks, voicemail, and failed calls |

---

## 8. Call Log Monitoring

This section is used to verify actual call results.

### Required Fields

| Field | Description |
|---|---|
| Call ID | Unique call record ID |
| Customer | Related customer |
| A Number | Caller number |
| X Number | Virtual phone number |
| B Number | Receiver number |
| Call Time | Time of the call |
| Duration | Call duration |
| Call Status | Success, Failed, Missed, or Busy |
| Recording | Recording file or link, if available |
| Log Status | Complete, Missing, or Delayed |

### Items to Monitor

- Whether the call connects correctly
- Whether the displayed number is correct
- Whether the call log is generated immediately
- Whether the call duration is correct
- Whether the call status is correct
- Whether recording is available, if required
- Whether successful and unsuccessful calls are separated clearly

---

## 9. Issue Tracker

This section is used to manage problems found during testing.

### Required Fields

| Field | Description |
|---|---|
| Issue ID | Unique issue ID |
| Customer | Related customer |
| Issue Type | Type of issue |
| Description | Issue details |
| Impact | Business or technical impact |
| Priority | Critical, High, Medium, or Low |
| Status | Open, In Progress, Fixed, Retesting, or Closed |
| Owner | Person responsible |
| Solution | Fix or proposed solution |
| Retest Result | Result after retesting |

### Issue Types

| Type | Example |
|---|---|
| Binding Issue | X number binds to the wrong A+B pair |
| Call Routing Issue | Call connects to the wrong receiver |
| Call Log Issue | Call log is missing or delayed |
| Recording Issue | Recording is not available |
| Auto-Unbind Issue | X number does not expire correctly |
| Display Issue | Wrong number is shown |
| System Stability Issue | Service fails during multiple calls |

---

## 10. Testing Board

The testing board should use a Kanban-style layout.

### Suggested Columns

| Column | Description |
|---|---|
| Not Started | Test case has not started |
| In Testing | Test case is currently being tested |
| Issue Found | Problem has been found |
| Fixing | Technical team is fixing the issue |
| Retesting | Test case is being tested again after the fix |
| Passed | Test case passed successfully |
| Blocked | Test case cannot continue due to dependency |

---

## 11. Status Options

### Project Status

```text
Not Started
First Discussion
Preparing Test
In Testing
Issue Found
Retesting
Passed
Completed
On Hold
```

### Test Case Status

```text
Pending
In Progress
Pass
Fail
Blocked
Need Retest
```

### X Number Status

```text
Available
Active
Expired
Error
```

### Issue Priority

```text
Critical
High
Medium
Low
```

### Issue Status

```text
Open
In Progress
Fixed
Retesting
Closed
```

---

## 12. Report Summary Page

The report page should summarize the testing result for internal updates or client discussions.

### Report Sections

| Section | Description |
|---|---|
| Testing Summary | Overall testing progress |
| Key Progress | What has been completed |
| Key Issues | Main issues found during testing |
| Business Impact | How the issues affect the customer use case |
| Next Step | What needs to be fixed or retested |
| Go-Live Readiness | Whether the service is ready for production |

---

## 13. Recommended Layout

### Top Section

Show key metrics, including total test cases, passed cases, failed cases, active X numbers, success rate, and open issues.

### Middle Section

Show customer comparison between Flash and J&T.

### Lower Section

Show recent issues, failed test cases, and latest call logs.

### Sidebar Menu

The sidebar should include:

```text
Overview
Customers
Test Cases
X Numbers
Call Logs
Issues
Testing Board
Reports
Settings
```

---

## 14. Core Data Structure

### Customer

```text
customer_id
customer_name
contact_person
service_type
testing_status
```

### Project

```text
project_id
customer_id
project_name
start_date
due_date
owner
priority
status
```

### Test Case

```text
test_case_id
project_id
scenario
expected_result
actual_result
status
evidence
remark
```

### X Number

```text
x_number_id
project_id
x_number
a_number
b_number
binding_status
start_time
expiry_time
```

### Call Log

```text
call_id
project_id
test_case_id
a_number
x_number
b_number
call_time
duration
call_status
recording_url
```

### Issue

```text
issue_id
project_id
test_case_id
issue_type
description
priority
status
owner
solution
```

---

## 15. Final Objective

The dashboard should help the team clearly answer these questions:

- Which customer is currently testing?
- What stage is each customer in?
- Which test cases have passed or failed?
- Which X numbers are currently active?
- Are call logs generated correctly?
- What issues are still open?
- What needs to be fixed before go-live?
- Is the customer ready to move from testing to production?

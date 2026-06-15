# DB Object Migration Plan

Last updated: 2026-06-15

## Purpose

This document defines the next database-focused implementation batch for SmartTutor Platform:

- increase use of SQL Server `PROCEDURE`, `VIEW`, and selected `FUNCTION`
- keep business flow aligned with the center-managed model in `AGENTS.md`
- avoid marketplace-style workflow objects
- keep Python service logic focused on API validation, authorization, and response mapping

This plan is intended to be implementation-ready for a follow-up coding chat.

## Source Context

- Canonical schema source: `sql/schema.sql`
- Current DB implementation snapshot: `docs/database_implementation.md`
- Current verified system status: `docs/current_status.md`
- Business rules and normalization constraints: `AGENTS.md`, `docs/database_rules.md`

## Current Verified SQL Server Object Inventory

The current local SQL Server database and `sql/schema.sql` are aligned on these custom DB objects:

### Views

- `VW_STUDY_CLASS_DETAIL`
- `VW_INVOICE_DETAIL`
- `VW_PAYMENT_DETAIL`

### Function

- `FN_INVOICE_REMAINING_AMOUNT`

### Procedures

- `SP_CREATE_TUITION_PAYMENT`

### Trigger

- `TRG_TUITION_PAYMENT_RECALC_INVOICE`

## Architectural Direction

The intended split is:

- `PROCEDURE` for multi-step business commands that must stay transactional
- `VIEW` for normalized read models reused by list/detail/report endpoints
- `FUNCTION` for reusable realtime financial or summary calculations
- `TRIGGER` only for narrow data-consistency side effects that should always happen after DML

The intended split is not:

- trigger-driven hidden workflow
- marketplace-style tutor acceptance or bidding flow
- pushing all API validation into SQL Server and removing service-level user-facing validation

## Objects To Add Or Refactor

## 1. `SP_ASSIGN_TUTOR_TO_REQUEST`

### Why

Current assignment creation is still orchestrated in Python service logic across multiple repository calls. This is a strong candidate for a single transactional command in SQL Server.

### Input

- `@request_id BIGINT`
- `@tutor_id BIGINT`
- `@staff_id BIGINT`
- `@notes NVARCHAR(500) = NULL`

### Output

Return the created assignment row, at minimum:

- `assignment_id`
- `request_id`
- `tutor_id`
- `staff_id`
- `status`
- `assigned_at`
- `notes`

### Business Rules

- learning request must exist
- learning request must not be canceled
- learning request must not already have an active `ASSIGNED` assignment
- tutor must exist and be `ACTIVE`
- tutor must have capability for the request subject
- if success:
  - insert `TUTOR_ASSIGNMENT`
  - update `LEARNING_REQUEST.status = 'ASSIGNED'`

### Transaction Boundary

One explicit transaction:

- lock/check request state
- validate tutor/capability
- insert assignment
- update request status
- commit once all steps succeed

### Backend Impact

- `POST /assignments`
- repository adds `call_assign_tutor_to_request(...)`
- service removes multi-step write orchestration and keeps API-facing validation/authorization

## 2. `SP_CREATE_CLASS_FROM_ASSIGNMENT`

### Why

Class creation is a business command, not simple table CRUD. It depends on assignment validity and the one-assignment-one-class rule.

### Input

- `@assignment_id BIGINT`
- `@staff_id BIGINT`
- `@start_date DATE`
- `@end_date DATE = NULL`
- `@hourly_rate DECIMAL(10,2)`
- `@sessions_planned INT = NULL`
- `@notes NVARCHAR(500) = NULL`

### Output

Return the created class row, at minimum:

- `class_id`
- `assignment_id`
- `status`
- `start_date`
- `end_date`
- `hourly_rate`
- `sessions_planned`
- `notes`

### Business Rules

- assignment must exist
- assignment must have status `ASSIGNED`
- assignment must not already own another class
- `hourly_rate > 0`
- `end_date >= start_date` when `end_date` is provided
- insert `STUDY_CLASS` with normalized structure only

### Transaction Boundary

One explicit transaction for:

- assignment state check
- duplicate class check
- class insert

### Backend Impact

- `POST /classes`
- repository adds `call_create_class_from_assignment(...)`
- service stops doing multi-step class creation writes directly

## 3. `SP_CREATE_INVOICE_FOR_PERIOD`

### Why

`TUITION_INVOICE` is a period snapshot, so invoice creation should become a dedicated DB command rather than plain insert CRUD.

### Input

- `@class_id BIGINT`
- `@period_start DATE`
- `@period_end DATE`
- `@due_date DATE`
- `@staff_id BIGINT`
- `@notes NVARCHAR(500) = NULL`

### Output

Return the created invoice row, at minimum:

- `invoice_id`
- `class_id`
- `period_start`
- `period_end`
- `due_date`
- `amount_due`
- `amount_paid`
- `status`
- `notes`

### Business Rules

- class must exist
- `period_end >= period_start`
- no duplicate invoice snapshot for the same class and period
- invoice `amount_due` must be computed as a snapshot using the agreed project rule
- new invoice starts with `amount_paid = 0`
- new invoice normally starts as `UNPAID`

### Open Rule To Lock Before Coding

`amount_due` calculation must be finalized before implementation:

- option A: sum completed lesson sessions in the period
- option B: sum planned sessions in the period
- option C: use explicit amount passed from service

Current project direction suggests option A for consistency with the existing auto-invoice branch.

### Transaction Boundary

One explicit transaction for:

- class check
- duplicate period check
- snapshot calculation
- invoice insert

### Backend Impact

- `POST /invoices`
- repository adds `call_create_invoice_for_period(...)`
- service stops inserting invoices directly

## 4. `VW_LEARNING_REQUEST_DETAIL`

### Why

Learning request reads still repeat normalized joins in repository SQL. This should become one stable read model.

### Shape

One row per learning request with:

- request fields
- student display fields
- subject display fields
- created-by / reviewed-by staff display fields if available
- active or latest assignment context
- assigned tutor display fields if available

### Business Rules

- must not create duplicate rows because of assignment history
- must expose only one assignment context per request for list/detail APIs
- should prefer active `ASSIGNED` assignment, otherwise latest assignment if needed

### Backend Impact

- `GET /learning-requests`
- `GET /learning-requests/{id}`

## 5. `VW_LESSON_SESSION_DETAIL`

### Why

Session reads should use a normalized read model instead of reassembling tutor/student/subject display metadata repeatedly.

### Shape

One row per lesson session with:

- session fields
- class fields needed for display
- tutor display fields
- student display fields
- subject display fields
- optional schedule linkage fields

### Business Rules

- joins must follow the normalized path:
  - `LESSON_SESSION`
  - `STUDY_CLASS`
  - `TUTOR_ASSIGNMENT`
  - `LEARNING_REQUEST`
  - `TUTOR`, `STUDENT`, `SUBJECT`
- must not assume denormalized direct `student_id`, `tutor_id`, or `subject_id` on `STUDY_CLASS`

### Backend Impact

- `GET /sessions`
- `GET /sessions/{id}`

## 6. `FN_CLASS_TUITION_SUMMARY`

### Why

The project rule says `/classes/{id}/tuition-summary` should be realtime and may differ from invoice snapshots. This is a good fit for a reusable SQL function.

### Input

- `@class_id BIGINT`

### Output

Table-valued result with:

- `class_id`
- `total_invoiced`
- `total_paid_success`
- `total_remaining`
- `unpaid_invoice_count`
- `overdue_invoice_count`

### Business Rules

- count only payment rows with status `SUCCESS`
- summary must be realtime
- summary may differ from old invoice snapshots between billing periods

### Backend Impact

- `GET /classes/{id}/tuition-summary`

## 7. `VW_INVOICE_DETAIL` Refactor

### Why

The view already exists, but invoice repository reads should fully standardize on it instead of maintaining parallel join SQL shapes.

### Backend Impact

- `GET /invoices`
- `GET /invoices/{id}`
- report or finance export queries later

## Trigger Policy

## Keep Existing Trigger

- keep `TRG_TUITION_PAYMENT_RECALC_INVOICE`
- it is narrow, deterministic, and aligned with finance consistency

## Do Not Add Triggers For These Flows

- assignment insert -> request status update
- assignment create -> class auto-create
- session complete -> invoice auto-create
- schedule insert -> session auto-generate

Reason:

- these are primary business workflow commands
- they should stay explicit and reviewable in procedures or service orchestration
- hiding them in triggers would make debugging and error handling worse

## Delivery Strategy

## Phase 1 - Read Model Foundation

Deliver:

- `VW_LEARNING_REQUEST_DETAIL`
- `VW_LESSON_SESSION_DETAIL`
- `FN_CLASS_TUITION_SUMMARY`
- invoice reads refactored to `VW_INVOICE_DETAIL`

Validation:

- direct `sqlcmd` select checks
- backend compile
- list/detail endpoint smoke checks

## Phase 2 - Assignment Procedure

Deliver:

- `SP_ASSIGN_TUTOR_TO_REQUEST`
- repository/service integration for `POST /assignments`

Validation:

- direct `EXEC` checks
- HTTP smoke:
  - valid assignment
  - duplicate assignment rejection
  - missing capability rejection

## Phase 3 - Class Procedure

Deliver:

- `SP_CREATE_CLASS_FROM_ASSIGNMENT`
- repository/service integration for `POST /classes`

Validation:

- direct `EXEC` checks
- HTTP smoke:
  - valid class creation
  - duplicate class rejection
  - wrong assignment status rejection

## Phase 4 - Invoice Procedure

Deliver:

- `SP_CREATE_INVOICE_FOR_PERIOD`
- repository/service integration for `POST /invoices`

Validation:

- direct `EXEC` checks
- HTTP smoke:
  - valid invoice create
  - duplicate period rejection
  - snapshot amount verification

## Phase 5 - Regression And Documentation

Deliver:

- full end-to-end flow rerun
- updated docs
- exact verification evidence

Validation:

- `sql/schema.sql` reset
- sample reseed
- auth-aware HTTP smoke test
- added focused finance and flow-negative tests

## SQL Script Management Plan

All new DB objects must be stored in repository SQL files, not created manually in SSMS only.

Recommended approach:

1. update `sql/schema.sql` so full rebuild contains the final object definitions
2. optionally add one incremental script for non-reset local DB upgrade, for example:
   - `sql/migrations/20260615_db_object_migration_phase1.sql`

For object definitions, use:

- `CREATE OR ALTER PROCEDURE`
- `CREATE OR ALTER VIEW`
- `CREATE OR ALTER FUNCTION`

This keeps scripts rerunnable and environment-safe.

## Repository And Service Refactor Map

| DB Object | Repository Change | Service Change | Endpoint |
| --- | --- | --- | --- |
| `SP_ASSIGN_TUTOR_TO_REQUEST` | add procedure execution helper | remove multi-step assignment write orchestration | `POST /assignments` |
| `SP_CREATE_CLASS_FROM_ASSIGNMENT` | add procedure execution helper | remove direct class insert orchestration | `POST /classes` |
| `SP_CREATE_INVOICE_FOR_PERIOD` | add procedure execution helper | remove direct invoice insert orchestration | `POST /invoices` |
| `VW_LEARNING_REQUEST_DETAIL` | switch request list/detail queries | keep response mapping compatibility | `GET /learning-requests*` |
| `VW_LESSON_SESSION_DETAIL` | switch session list/detail queries | keep response mapping compatibility | `GET /sessions*` |
| `FN_CLASS_TUITION_SUMMARY` | replace aggregate SQL call with function select | keep access-control and response formatting | `GET /classes/{id}/tuition-summary` |
| `VW_INVOICE_DETAIL` | standardize invoice list/detail queries | keep finance access logic | `GET /invoices*` |

## Preconditions Before Coding

These decisions should be treated as locked before implementation starts:

1. invoice snapshot amount source
2. whether request detail view exposes only active assignment or active/latest fallback
3. whether session detail view needs schedule display fields immediately or in a later batch

## Recommended Next Chat Prompt

Use the following as the starting prompt for the next coding chat:

```text
Read AGENTS.md, docs/current_status.md, docs/database_implementation.md, and docs/db_object_migration_plan.md.
Implement Phase 1 of the DB object migration plan:
- add VW_LEARNING_REQUEST_DETAIL
- add VW_LESSON_SESSION_DETAIL
- add FN_CLASS_TUITION_SUMMARY
- refactor invoice reads to use VW_INVOICE_DETAIL consistently
Then run compile checks, update docs/current_status.md, and append docs/agent_worklog.md.
```

# Current Status

## Last Updated

- 2026-06-14

## Source Of Truth

- Database schema source of truth: `sql/schema.sql`
- Backend/frontend contract reference: `docs/api_contract.md`
- Exact completion table: `docs/completion_matrix.md`

## Verified Backend Status

- `GET /` exists in `backend/app/main.py`
- `GET /health` exists in `backend/app/main.py`
- Backend compile passes with:

```powershell
uv run python -m compileall backend/app
```

- SQL Server connection has been verified from the local backend environment.
- Real HTTP CRUD smoke test passes with:

```powershell
cd backend
uv run python tests/http_crud_smoke.py --base-url http://127.0.0.1:8000 --staff-email staff1@smarttutor.local --staff-password staff123
```

- The smoke script now verifies real auth scopes instead of calling protected endpoints anonymously:
  - logs in as demo `staff` for staff-only CRUD
  - registers and logs in a fresh `student` for self-owned learning-request flow

- The following groups were verified through real HTTP requests, not just code audit:
  - auth register/login
  - subjects
  - students
  - tutors
  - tutor capabilities
  - tutor availability
  - learning requests
  - assignments
  - classes
  - schedules
  - sessions
  - invoices
  - payments
- Payment insert works against SQL Server even with the `TUITION_PAYMENT` trigger enabled.
- `POST /payments` can use either `invoice_id` or `class_id`.
- When `POST /payments` uses `class_id` without `invoice_id`, the service now auto-creates a period invoice snapshot when needed:
  - invoice status starts as `UNPAID`
  - payment payload `status` remains a payment status and is no longer reused as invoice status
  - snapshot totals count only `COMPLETED` sessions within `period_start` and `period_end`
  - successful payments still run through remaining-balance validation before insert
- Backend status docs no longer rely on the old unauthenticated smoke-script assumption for protected routes.
- Overpayment is rejected with:

```json
{
  "detail": "Payment amount exceeds invoice remaining amount"
}
```

- `DELETE /students/{id}` soft-deactivates student to `INACTIVE`
- `DELETE /tutors/{id}` soft-deactivates tutor to `INACTIVE`
- `DELETE /subjects/{id}` soft-deactivates subject to `INACTIVE`
- `DELETE /learning-requests/{id}` cancels request to `CANCELED`
- `PATCH /assignments/{id}/cancel` exists and `DELETE /assignments/{id}` remains as cancel compatibility
- `DELETE /classes/{id}` cancels class to `CANCELED`
- `DELETE /schedules/{id}` now deactivates schedule to `INACTIVE`
- `DELETE /sessions/{id}` now cancels session to `CANCELED`
- `DELETE /invoices/{id}` now cancels invoice to `CANCELED`
- `DELETE /payments/{id}` now cancels payment to `CANCELED`
- Invalid `teaching_mode` is now validated in service logic for:
  - learning requests: `ONLINE`, `OFFLINE`, `BOTH`
  - tutor availability: `ONLINE`, `OFFLINE`, `BOTH`
  - classes: `ONLINE`, `OFFLINE`
- Service-layer validation now rejects common create/update constraint failures before SQL Server for:
  - profile/master statuses for students, tutors, and subjects
  - duplicate subject name + level
  - tutor experience and capability years experience
  - tutor availability day/time/status
  - learning request status and non-negative expected fee
  - assignment status and staff id existence on update
  - class tuition and start/end date windows
  - schedule day/time/effective date/status
  - session status, positive session number, paired start/end time, and schedule/class mismatch
  - invoice period, completed session count, non-negative money values, and paid amount not exceeding due
  - payment positive amount and valid payment status
- Update semantics now preserve explicit client intent for fields sent as `null`:
  - shared repository updates no longer skip `None` values, so nullable columns can be cleared through update payloads
  - `updated_at` is touched automatically for shared update paths when at least one model field is applied
  - direct service transitions such as soft-delete/cancel/status patch now touch `updated_at` before commit
- SQL raw repository migration Step 1 has started on auth/account/profile lookup paths:
  - `data_repository.py` now has shared raw SQL helpers for `fetch_one`, `fetch_all`, and `execute`
  - auth account lookup now uses raw SQL repository functions for `USER_ACCOUNT`
  - actor/profile lookup by `account_id` now uses raw SQL repository functions for `STUDENT`, `TUTOR`, and `STAFF`
  - `backend/app/core/auth.py` no longer uses direct `db.query(...)` for current-actor resolution
  - `business_service.authenticate()` no longer uses direct `db.query(...)` for role profile resolution
  - this step is compile-verified; broader master-data CRUD is still ORM-backed pending later migration steps
- SQL raw repository migration Step 2 is complete for student and subject CRUD:
  - `get_students`, `get_student`, `create_student`, `update_student`, and `deactivate_student` now use parameterized raw SQL
  - `get_subjects`, `get_subject`, `get_subject_by_name_level`, `create_subject`, `update_subject`, and `deactivate_subject` now use parameterized raw SQL
  - repository updates use a whitelisted `update_by_id` helper instead of request-driven table or column names
  - student and subject service update/deactivate flows now call explicit repository SQL functions instead of mutating returned objects
  - this step is compile/search verified; tutor profile and downstream business flows remain pending later migration steps
- SQL raw repository migration Step 3 is complete for tutor profile paths:
  - tutor list/detail/create/update/deactivate now use parameterized raw SQL
  - tutor read helpers attach capability and subject dot-access objects for existing response compatibility
  - tutor capability list/create/update/delete now use parameterized raw SQL
  - tutor availability list/detail/create/update/delete now use parameterized raw SQL
  - tutor service update/deactivate, capability update, subject rebuild, and availability update/delete flows now use explicit repository SQL functions instead of ORM mutation or `db.flush()`
  - this step is compile/search verified; learning request, assignment, class, schedule, session, invoice, payment, and dashboard paths remain pending later migration steps
- SQL raw repository migration Step 4 is complete for learning request CRUD:
  - `get_learning_requests`, `get_learning_request`, `create_learning_request`, `update_learning_request`, and `cancel_learning_request` now use parameterized raw SQL
  - learning request read helpers attach student and subject dot-access objects for existing response compatibility
  - learning request update/cancel service flows now call explicit repository SQL functions instead of mutating returned objects
  - this step is compile/search verified; assignment-driven request status transitions remain pending the assignment migration step
- SQL raw repository migration Step 5 is complete for assignment CRUD and assignment/request transitions:
  - `get_assignments`, `get_assignment`, `create_assignment`, `update_assignment`, and `cancel_assignment` now use parameterized raw SQL
  - assignment read helpers attach a lightweight `study_class` object when an assignment already has a class, preserving existing class-creation/cancel checks
  - create assignment now updates the linked learning request to `ASSIGNED` through explicit SQL
  - update/cancel assignment now returns the linked learning request to `PENDING` through explicit SQL when the assignment is canceled
  - assignment service flows no longer mutate assignment/request objects directly
  - this step is compile/search verified; class, schedule, session, invoice, payment, and dashboard paths remain pending later migration steps
- SQL raw repository migration Step 6 is complete for class read/write and class tuition aggregates:
  - `get_classes` and `get_class` now read from `VW_STUDY_CLASS_DETAIL`
  - class read helpers attach raw SQL schedule display and next scheduled lesson fields for existing frontend response compatibility
  - `create_class`, `update_class`, and `cancel_class` now use parameterized raw SQL
  - `class_to_response` and class access checks now support view-backed flat class rows
  - class-id payment auto-invoice snapshot and `/classes/{id}/tuition-summary` now use raw SQL aggregates instead of `study_class.sessions` / `study_class.invoices`
  - this step is compile/search verified; schedule, session, invoice, payment, and dashboard paths remain pending later migration steps
- SQL raw repository migration Step 7 is complete for class schedule CRUD and schedule filters:
  - `get_schedules` now uses parameterized raw SQL with normalized joins through `STUDY_CLASS`, `TUTOR_ASSIGNMENT`, and `LEARNING_REQUEST`
  - `get_schedule` and `create_schedule` now use parameterized raw SQL against `CLASS_SCHEDULE`
  - `update_schedule` and `deactivate_schedule` now use whitelisted explicit SQL updates
  - schedule service update/delete flows no longer mutate returned schedule objects directly
  - this step is compile/search verified; session, invoice, payment, and dashboard paths remain pending later migration steps

## Verified Business Flow Status

The following flow has direct real-HTTP smoke-test evidence on the local SQL Server-backed backend:

- register account: PASS
- login account: PASS
- create learning request: PASS
- assign tutor: PASS
- create class from `assignment_id`: PASS
- create schedule: PASS
- create session: PASS
- mark session `COMPLETED`: PASS
- create invoice: PASS
- create payment: PASS
- create payment by `class_id` with auto-created invoice snapshot: compile-covered in smoke script, pending live rerun
- reject overpayment with `400`: PASS
- class response includes student/tutor/subject display data: PASS

See `docs/completion_matrix.md` for the exact evidence summary.

## Verified Frontend Status

- Frontend build passes with:

```powershell
cd frontend
npm run build
```

- `frontend/src/services/api.js` exists and is the shared API client.
- Fake login/testing controls were removed from `frontend/src/components/Header.jsx`.
- `frontend/src/contexts/AuthContext.jsx` no longer exposes the old `fakeLogin` path.
- Real API is the primary source for:
  - login/register
  - dashboard summary
  - students
  - tutors
  - classes
  - learning requests
  - subjects
  - assignments
  - schedules
  - sessions
  - invoices/payments via `FinancePage`
- First-class API-backed pages now exist in `frontend/src/pages` for:
  - `SubjectsPage.jsx`
  - `AssignmentsPage.jsx`
  - `SchedulesPage.jsx`
  - `SessionsPage.jsx`
  - `FinancePage.jsx`
- Students, tutors, learning requests, subjects, schedules, and classes all have wired create/edit forms in the current UI.
- `LearningRequestsPage.jsx` now allows staff to open the edit form correctly instead of showing a dead "Sửa" action.
- `FinancePage.jsx` now blocks tutor access in the UI before triggering invoice/payment API calls that are staff-or-student only.

## Exact Frontend Gaps

- No backend-connected detail drilldown/modal exists yet for:
  - class detail beyond the main list row
  - invoice detail
  - payment detail
- Assignments page supports create and cancel, but does not yet expose reassignment/update UI.
- Sessions page supports create, cancel, and quick status updates, but does not yet expose a full edit form for existing sessions.
- Finance page supports create and cancel flows, but does not yet expose invoice/payment update forms.
- Frontend actor guards still rely mainly on local auth state plus backend enforcement; there is no dedicated route-protection layer yet.

## Seed Status

- `sql/minimal_seed.sql`
  - covers auth/basic entity smoke setup
  - includes learning request, assignment, and class
  - does not cover the full invoice/payment/session demo chain

- `sql/sample_data.sql`
  - covers the main demo chain:
    - learning request
    - assignment
    - class
    - schedule
    - session
    - invoice
    - payment
  - must be executed with UTF-8 input on Windows `sqlcmd`:

```powershell
powershell -ExecutionPolicy Bypass -File .\sql\reset_demo_utf8.ps1 -Seed sample
```

  - root cause of the previous Vietnamese corruption was `sqlcmd` importing the UTF-8 file without `-f 65001`

## SQL Query Status

- `sql/query_examples.sql` exists
- included query groups:
  - dashboard summary
  - normalized class list
  - tutor workload
  - realtime tuition summary
  - invoice/payment status
  - revenue by month

## Next Concrete Batch

- verify the newly added staff finance/assignment/schedule/session screens against live backend requests, not just build/code audit
- rerun the auth-aware CRUD smoke test against the active local backend and refresh evidence text if any endpoint behavior changed
- continue SQL raw repository migration with lesson session CRUD, status updates, and session filters after the schedule raw SQL step
- rerun the auth-aware CRUD smoke test to verify the new class-id payment auto-invoice branch against SQL Server triggers
- add focused negative HTTP tests for the service-layer validation paths added in this batch
- add focused HTTP coverage for explicit nullable-field clearing and `updated_at` movement on update/cancel paths
- add missing detail/update UX for assignments, sessions, invoices, and payments where the backend already supports it
- consider adding route-level protection so invalid actor routes are blocked before render
- keep `docs/completion_matrix.md` as the exact PASS/PARTIAL/FAIL source for future batches

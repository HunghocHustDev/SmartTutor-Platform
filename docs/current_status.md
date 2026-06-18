# Current Status

## Last Updated

- 2026-06-18

## Source Of Truth

- Database schema source of truth: `sql/schema.sql`
- Backend/frontend contract reference: `docs/api_contract.md`
- Exact completion table: `docs/completion_matrix.md`
- DB object migration roadmap for the next batch: `docs/db_object_migration_plan.md`

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
- SQL raw repository migration Step 8 is complete for lesson session CRUD, status updates, and session filters:
  - `get_sessions` now uses parameterized raw SQL with normalized joins through `STUDY_CLASS`, `TUTOR_ASSIGNMENT`, and `LEARNING_REQUEST`
  - `get_session` and `create_session` now use parameterized raw SQL against `LESSON_SESSION`
  - `update_session` and `cancel_session` now use whitelisted explicit SQL updates
  - session status patch can still clear `content_note` when the field is explicitly sent as `null`
  - `session_to_response` now supports raw SQL flat `class_label` rows while keeping the previous relationship fallback
  - this step is compile/search verified; invoice, payment, and dashboard paths remain pending later migration steps
- SQL raw repository migration Step 9 is complete for invoice CRUD, list/detail reads, and class-period lookup:
  - `get_invoices`, `get_invoice`, and `get_invoice_by_class_period` now use parameterized raw SQL with normalized joins through `STUDY_CLASS`, `TUTOR_ASSIGNMENT`, and `LEARNING_REQUEST`
  - `create_invoice` now uses parameterized raw SQL against `TUITION_INVOICE`
  - `update_invoice` and `cancel_invoice` now use whitelisted explicit SQL updates
  - invoice read helpers attach minimal class/request context so existing payment validation can still resolve the invoice class student before the payment migration step
  - invoice service update/delete flows no longer mutate returned invoice objects directly
  - this step is compile/search verified; payment and dashboard paths remain pending later migration steps
- SQL raw repository migration Step 10 is complete for payment CRUD/list/detail and dashboard summary:
  - `sql/schema.sql` now defines `VW_PAYMENT_DETAIL`, `VW_INVOICE_DETAIL`, `FN_INVOICE_REMAINING_AMOUNT`, and `SP_CREATE_TUITION_PAYMENT`
  - `get_payments` and `get_payment` now read from `VW_PAYMENT_DETAIL`
  - `create_payment` now calls `SP_CREATE_TUITION_PAYMENT` while preserving service-layer overpayment validation before insert
  - `update_payment` and `cancel_payment` now use whitelisted explicit SQL updates and continue to rely on the existing payment trigger for invoice recalculation
  - payment read helpers attach minimal nested invoice context so access control and remaining-amount validation keep working during the final cleanup stage
  - `/dashboard/summary` now uses one raw SQL aggregate statement instead of multiple ORM count queries
  - this step is live-verified on SQL Server after rerunning `sql/schema.sql`, reseeding sample data, and rerunning the auth-aware smoke test
- DB Object Migration Plan Phase 1 is now implemented and compile-verified:
  - `sql/schema.sql` now defines `VW_LEARNING_REQUEST_DETAIL`, `VW_LESSON_SESSION_DETAIL`, and `FN_CLASS_TUITION_SUMMARY`
  - learning request list/detail reads now use `VW_LEARNING_REQUEST_DETAIL`
  - lesson session list/detail reads now use `VW_LESSON_SESSION_DETAIL`
  - `/classes/{id}/tuition-summary` now reads from `FN_CLASS_TUITION_SUMMARY`
  - invoice list/detail/class-period reads now standardize on `VW_INVOICE_DETAIL`
  - learning request detail view exposes one assignment context per request, preferring active `ASSIGNED` rows and otherwise falling back to the latest assignment
  - this batch is compile-verified; direct `sqlcmd` object validation and live HTTP reruns are still pending
- DB Object Migration Plan Phase 2 is now implemented and compile-verified:
  - `sql/schema.sql` now defines `SP_ASSIGN_TUTOR_TO_REQUEST`
  - `POST /assignments` now calls the procedure through repository helper `call_assign_tutor_to_request(...)`
  - assignment creation still keeps service-layer validation and authorization checks, but the transactional insert + request-status transition now runs inside SQL Server
  - update/cancel assignment flows remain on the existing explicit SQL path for this phase
  - this batch is compile-verified; direct `EXEC` validation and live HTTP reruns are still pending
- DB Object Migration Plan Phase 3 is now implemented and compile-verified:
  - `sql/schema.sql` now defines `SP_CREATE_CLASS_FROM_ASSIGNMENT`
  - `POST /classes` now calls the procedure through repository helper `call_create_class_from_assignment(...)`
  - class creation still keeps service-layer validation and normalization checks, but the transactional assignment-state check + class insert now runs inside SQL Server
  - the procedure follows the current repo schema by accepting `class_code`, `tuition_fee_per_session`, `teaching_mode`, `location`, `start_date`, `end_date`, and `status`
  - class update/cancel flows remain on the existing explicit SQL path for this phase
  - this batch is compile-verified; direct `EXEC` validation and live HTTP reruns are still pending
- DB Object Migration Plan Phase 4 is now implemented and compile-verified:
  - `sql/schema.sql` now defines `SP_CREATE_INVOICE_FOR_PERIOD`
  - `POST /invoices` now calls the procedure through repository helper `call_create_invoice_for_period(...)`
  - invoice creation still keeps service-layer class lookup, period validation, duplicate-period guard, and status validation
  - the procedure follows the current repo schema by accepting `class_id`, `period_start`, and `period_end`, then computing `completed_sessions`, `tuition_fee_per_session`, `amount_due`, `amount_paid = 0`, and `status = 'UNPAID'`
  - invoice create payload snapshot fields remain accepted for compatibility, but the persisted snapshot is now computed from SQL Server using `COMPLETED` sessions in the requested period
  - invoice update/cancel flows remain on the existing explicit SQL path for this phase
  - this batch is compile-verified; direct `EXEC` validation and live HTTP reruns are still pending
- Live verification is now complete for DB object migration Phases 1-4:
  - reran `sql/schema.sql` successfully against SQL Server
  - reseeded `sql/sample_data.sql` successfully after schema reset
  - direct `EXEC` checks passed for:
    - `SP_ASSIGN_TUTOR_TO_REQUEST`
    - `SP_CREATE_CLASS_FROM_ASSIGNMENT`
    - `SP_CREATE_INVOICE_FOR_PERIOD`
  - invalid `EXEC` cases now return clean SQL errors without leaving the session in a doomed transaction state
  - auth-aware HTTP smoke test passes end to end after the Phase 2-4 procedure migrations
- Procedure error paths are now hardened for live SQL usage:
  - `SP_ASSIGN_TUTOR_TO_REQUEST`, `SP_CREATE_CLASS_FROM_ASSIGNMENT`, `SP_CREATE_INVOICE_FOR_PERIOD`, and `SP_CREATE_TUITION_PAYMENT` now wrap transactional bodies in `TRY/CATCH`
  - failed procedure executions explicitly `ROLLBACK` before rethrowing
  - this prevents follow-up commands in the same SQL session from failing with transaction state errors after one invalid procedure call
- Final raw-SQL cleanup is complete for repository/service runtime access patterns:
  - `create_user`, `get_staff`, and `create_staff` no longer use ORM `db.add`, `db.flush`, or `db.query`
  - `backend/app/repositories/data_repository.py` and `backend/app/services/business_service.py` now return no matches for `db.query`, `db.add`, `db.delete`, `db.refresh`, or `db.flush`
  - `backend/app/repositories/data_repository.py` and `backend/app/services/business_service.py` now return no matches for `joinedload` or `.options(`
- Live verification after the final SQL-object batch now confirms:
  - `sql/schema.sql` executes cleanly against SQL Server when `SET ANSI_NULLS ON` and `SET QUOTED_IDENTIFIER ON` are enabled before filtered-index creation
  - `sql/sample_data.sql` seeds successfully after schema reset
  - auth-aware smoke test passes end to end after the payment procedure/view/function migration
- Live verification after the `demo3` backend refactor now confirms:
  - local backend startup succeeds with `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000`
  - `GET /health` returns `{"status":"ok"}`
  - auth-aware smoke test still passes end to end after the service and router decomposition work
- Repository-layer decomposition has now been completed on branch `demo3` and is live-verified:
  - the previous monolithic `backend/app/repositories/data_repository.py` has been split by bounded context into:
    - `repository_common.py`
    - `account_repository.py`
    - `student_repository.py`
    - `tutor_repository.py`
    - `request_repository.py`
    - `class_repository.py`
    - `finance_repository.py`
    - `dashboard_repository.py`
  - `data_repository.py` now acts as a compatibility facade that re-exports the existing repository surface for current services and auth code
  - compile verification passes and the auth-aware HTTP smoke test still passes after the repository split on `demo3`
- Backend service-layer refactor for branch `demo3` is compile-verified:
  - the previous monolithic `backend/app/services/business_service.py` has been split by role into:
    - `auth_service.py`
    - `student_service.py`
    - `tutor_service.py`
    - `subject_service.py`
    - `request_flow_service.py`
    - `class_flow_service.py`
    - `finance_service.py`
    - `dashboard_service.py`
    - shared helpers in `common.py`
  - `business_service.py` now acts as a compatibility facade that re-exports the existing service surface for current routers and auth code
  - this refactor has now been rerun through local backend startup and the auth-aware HTTP smoke test on `demo3`
- Backend router decomposition has continued on branch `demo3` and is compile-verified:
  - `backend/app/routers/tutors.py` now acts as a small aggregate router
  - tutor endpoints were split into:
    - `tutor_profiles.py`
    - `tutor_capabilities.py`
    - `tutor_availabilities.py`
    - shared tutor access guard in `tutor_router_support.py`
  - `backend/app/routers/students.py` now acts as a small aggregate router
  - student endpoints were split into:
    - `student_profiles.py`
    - `student_relations.py`
    - shared student access guard in `student_router_support.py`
  - endpoint paths and current `main.py` router includes were preserved
  - this router refactor has now been rerun through local backend startup and the auth-aware HTTP smoke test on `demo3`
- Backend router decomposition has expanded further on branch `demo3` and remains compile-verified:
  - `backend/app/routers/learning_requests.py` now acts as an aggregate router
  - learning-request routes were split into:
    - `learning_request_profiles.py`
    - shared request/assignment helper logic in `learning_request_router_support.py`
  - `backend/app/routers/assignments.py` now acts as an aggregate router
  - assignment routes were split into:
    - `assignment_routes.py`
    - shared staff-id payload normalization reused from `learning_request_router_support.py`
  - `backend/app/routers/classes.py` now acts as an aggregate router
  - class routes were split into:
    - `class_profiles.py`
    - `class_finance.py`
    - shared class/schedule/session actor-filter helpers in `class_router_support.py`
  - `backend/app/routers/schedules.py` now acts as an aggregate router over `schedule_routes.py`
  - `backend/app/routers/sessions.py` now acts as an aggregate router over `session_routes.py`
  - endpoint paths and current `main.py` router includes were preserved
  - live verification on `demo3` exposed and fixed two FastAPI bootstrap regressions that compile alone did not catch:
    - aggregate router files had `APIRouter` used before import after the split
    - aggregate routers cannot include child routers with empty-path operations unless the child router itself carries the resource `prefix`
  - after fixing those bootstrap issues, local backend startup and the auth-aware HTTP smoke test both pass on `demo3`
- Tutor suggestion API is now implemented:
  - `GET /learning-requests/{id}/suggested-tutors` returns ranked tutor candidates for staff
  - scoring factors: experience (x10), area match (+20), schedule availability match (+15)
  - filters: tutor is ACTIVE, has capability for subject, has <10 active classes, no existing active assignment for this request
  - implemented in repository (`get_candidate_tutors_for_request`), service (`suggest_tutors_for_request`), router, and schema layers
  - frontend integration: "Gợi ý gia sư" button on LearningRequestsPage for staff, opens modal with ranked tutor suggestions
- Auto-generate sessions from fixed schedules is now implemented:
  - `POST /sessions/generate-from-schedules` (staff only) accepts `{ class_id, range_start?, range_end? }` and returns `{ class_id, created_count, created_session_ids, skipped_existing, range_start, range_end }`
  - `POST /sessions/preview-from-schedules` (staff only) returns the planned session rows without inserting them
  - service helper `_build_session_plan` iterates over `ACTIVE` `CLASS_SCHEDULE` rows, respects `effective_from`/`effective_to`, skips existing `(lesson_date, start_time)` pairs, and starts `session_number` from `MAX(existing) + 1`
  - when no `range_start`/`range_end` is provided, the service falls back to `STUDY_CLASS.start_date`/`end_date`
- Realtime tuition summary and overpayment protection are now confirmed end to end:
  - `GET /classes/{id}/tuition-summary` continues to read from `FN_CLASS_TUITION_SUMMARY` so paid/remaining totals always reflect current `SUCCESS` payments, not invoice snapshots
  - `POST /payments` already validates remaining amount in `finance_service.create_payment` before insert and returns `400 Payment amount exceeds invoice remaining amount`
  - `PUT /payments/{id}` validates remaining amount on transitions that promote or update a `SUCCESS` payment
- Suggested-tutors capability matching is now subject-name aware (defense in depth):
  - `get_candidate_tutors_for_request` in `backend/app/repositories/request_repository.py` now expands the capability filter through a small `EquivalentSubjects` CTE that matches the request subject against any other `SUBJECT` row with the same effective `subject_name` + `grade_level`, even when one row stores them as `name='Tiếng Anh' + grade_level='Lớp 11'` and another stores them as `name='Tiếng Anh Lớp 11' + grade_level=NULL`
  - this fixes a real bug found while testing learning request #25 against tutors created through the UI: the request used the seed-data subject id (9) while the tutor capability was stored against the UI-created subject id (20), so the candidate set came back empty even though three tutors teach that subject
  - the CTE only matches rows with `status <> 'INACTIVE'`, and still respects the existing `t.status = 'ACTIVE'`, `<10 active classes`, and `NOT EXISTS active assignment` filters
  - note: the request #25 candidate set can still be empty if every tutor who matches by subject also has an active class assigned; in the demo data all three English-11 tutors do, so the result stays empty by design even after the fix
- Suggested-tutors response decoding is now safe for `SimpleNamespace` rows:
  - `suggest_tutors_for_request` in `backend/app/services/request_flow_service.py` no longer assumes `row._mapping` exists
  - the previous branch `dict(row._mapping) if hasattr(row, "_mapping") else dict(row)` raised `TypeError: 'types.SimpleNamespace' object is not iterable` once the candidate CTE returned real rows, because `to_obj(...)` wraps raw mapping rows in `SimpleNamespace`
  - the new branch reads `row.__dict__` for `SimpleNamespace` rows and still falls back to `dict(row._mapping)` for raw mapping rows
  - this bug only surfaces after at least one tutor passes the candidate filter, so it stayed hidden while the demo data had no free English-11 tutors
- Suggested-tutors live demo seed is now available for learning request #25:
  - `sql/seed_test_request_25.sql` adds two `USER_ACCOUNT` rows (901, 902), two `TUTOR` rows (`Lê Minh Anh`, `Phạm Quốc Đạt`), capability for subject_id=9 (`Tiếng Anh Lớp 11`), and one OFFLINE availability row each on day_of_week=2 (T3) 18:30-20:30, matching the request preferences
  - both tutors are ACTIVE, have 0 active classes, and have no existing `TUTOR_ASSIGNMENT`, so they pass the candidate filter and now show up on `GET /learning-requests/25/suggested-tutors`
  - tutor #902 ranks first (score 100, 8 years experience), tutor #901 ranks second (score 90, 5 years experience, exact area match)
  - the script requires `SET QUOTED_IDENTIFIER ON; SET ANSI_NULLS ON;` at the top because the `SUBJECT` table has a filtered index that rejects mismatched `SET` options
  - to undo: `DELETE FROM USER_ACCOUNT WHERE account_id IN (901, 902)` cascades through `TUTOR.account_id` and the related `TUTOR_CAPABILITY` / `TUTOR_AVAILABILITY` rows
- Assignments page now always shows the "Phân công" action bar when a request is selected (even before choosing a tutor):
  - old behavior: the assignment form was wrapped in `{selectedTutorId && ...}` so the green "Phân công" button only appeared after a tutor was pre-selected (either by "Gợi ý" or by manual radio click)
  - this made the button invisible to new users who browsed the request list but hadn't yet clicked "Gợi ý"
  - the form area now uses `{selectedRequestId && ...}` as the outer gate, so it renders as soon as any request is selected
  - inside the form, the button is disabled (`disabled={saving || !selectedTutorId}`) until a tutor is chosen, and a hint text guides the user to either pick from the list or click "Gợi ý gia sư"
  - "Hủy chọn" button is now conditional too (only shown when a tutor is selected)
- FinancePage invoice form now auto-fills fields when a class is selected:
  - `handleClassSelect` calls `GET /classes/{id}/tuition-summary` and `GET /classes/{id}/invoice-period` in parallel on class change
  - `period_start`, `period_end` are auto-populated from `invoice-period` (default = tháng hiện tại, ngày 1 → ngày cuối tháng)
  - `completed_sessions`, `tuition_fee_per_session`, and `amount_due` are auto-populated from the tuition summary
  - a summary card renders below the class selector showing real-time buổi/phí/tổng/nợ plus the suggested kỳ range
  - `amount_due` defaults to `total_fee` from the summary (buổi × phí/buổi)
  - `finance_service.create_invoice` was fixed to persist the payload values instead of delegating to `SP_CREATE_INVOICE_FOR_PERIOD` (which computed everything from SQL and ignored client input)
  - invoice table now shows an extra "Buổi & Phí" column (sessions count + fee/buổi) and a "Còn nợ" row (amount_due - amount_paid)
  - `frontend/src/services/api.js` exports `getClassTuitionSummary(classId)` and `getClassInvoicePeriod(classId)` for the frontend
  - new backend endpoint `GET /classes/{id}/invoice-period` (in `class_finance.py`) returns `{ period_start, period_end, completed_sessions }` — period defaults to the current month, and is computed purely from server-side date logic (no DB scan needed)

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
- create payment by `class_id` with auto-created invoice snapshot: PASS
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
- `SessionsPage.jsx` now exposes an auto-generate panel for staff:
  - select class, optional date range, preview planned sessions, confirm create
  - buttons only render for `canCreate` (staff)
  - reuses existing `listSessions` after confirm so the table refreshes without a manual reload
- `SessionsPage.jsx` now uses an internal modal (textarea) for the `COMPLETED` action instead of `window.prompt`, and the form fields now have proper Vietnamese labels.
- `SchedulesPage.jsx` form fields now have proper Vietnamese labels and a context banner shows which class is being edited before submit.
- `TutorProfilePage.jsx` now renders a weekly availability grid below the availability list so tutors/staff can see the tutor's free slots at a glance.

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

- rerun direct SQL Server validation for DB Object Migration Plan Phase 1:
  - execute `sql/schema.sql`
  - run focused `SELECT` checks against `VW_LEARNING_REQUEST_DETAIL`, `VW_LESSON_SESSION_DETAIL`, `VW_INVOICE_DETAIL`, and `FN_CLASS_TUITION_SUMMARY`
  - rerun the auth-aware HTTP smoke test
- if the backend decomposition continues on `demo3`, keep the next batch scoped to one layer at a time:
  - routers by domain, or
  - repository split by bounded context
  - preserve the current API contract while shrinking module size
- if router decomposition continues on `demo3`, the next safe targets are:
  - `invoices` + `payments`
  - shared auth/dashboard helpers only if they genuinely grow
  - keep aggregate router files thin and avoid changing URL structure
- if further backend cleanup continues on `demo3`, prefer non-structural follow-up work next:
  - add startup/import smoke coverage
  - add focused negative HTTP tests
  - reduce duplicated SQL snippets inside the new repository modules only when covered by tests
- add one lightweight backend startup/import smoke check to local verification so FastAPI router-bootstrap regressions are caught earlier than full HTTP testing
- add focused negative HTTP tests for the newer procedure-backed flows:
  - assignment procedure invalid tutor capability / non-pending request
  - class procedure duplicate class / invalid assignment state
  - invoice procedure duplicate period / missing class
- consider tightening the invoice create API contract so client-supplied snapshot fields are clearly deprecated if the frontend no longer needs to send them
- refresh `docs/completion_matrix.md` with explicit evidence notes for the Phase 1-4 live verification batch
- keep `TRG_TUITION_PAYMENT_RECALC_INVOICE` as the finance consistency trigger and avoid adding hidden-workflow triggers
- verify the newer frontend screens against live backend requests, not just build/code audit
- add focused negative HTTP tests for the service-layer validation paths added in this batch
- add focused HTTP coverage for explicit nullable-field clearing and `updated_at` movement on update/cancel paths
- add missing detail/update UX for assignments, sessions, invoices, and payments where the backend already supports it
- consider adding route-level protection so invalid actor routes are blocked before render
- FinancePage UX hardening pass completed in 2026-06-18 batch:
  - new shared component `frontend/src/components/StatusBadge.jsx` renders invoice / payment / class status as a colored pill using existing label maps
  - new shared component `frontend/src/components/ConfirmDialog.jsx` replaces `window.confirm` for cancel flows (ESC, backdrop click, focus-on-cancel, danger variant, loading state)
  - `frontend/src/utils/formatting.js` now exports `paymentStatusLabel`, `PAYMENT_METHOD_LABELS`, and `PAYMENT_METHOD_KEYS` (`BANK_TRANSFER`, `CASH`, `MOMO`, `VNPAY`) so the frontend can localize without changing the free-form backend string
  - tutor-role error banner is now plain Vietnamese (no mojibake)
  - invoice form: per-field errors with end > start check, realtime duplicate-period detection (yellow banner + disabled submit), auto-recomputed `amount_due = sessions × fee` until the user manually overrides
  - invoice form: removed the `status` selector — new invoices always start as `UNPAID` because the `TUITION_PAYMENT` trigger and service layer own the status transitions
  - payment form: per-field errors, auto-default `amount_paid = remaining`, helper text under the input (`Tối đa: ...` or `Vượt còn nợ X đ`), disabled submit while `paymentInvalid`
  - payment form: invoice dropdown shows ` (đã đủ)` or ` (còn nợ ...)` and disables fully-settled options; payment method dropdown renders Vietnamese labels (`Chuyển khoản`, `Tiền mặt`, `Ví MoMo`, `VNPay`)
  - both invoice and payment tables now support search (id, class code, status, period dates, note), sortable column headers (`#` / `Kỳ` / `Phải thu` / `Trạng thái` for invoices; `#` / `Số tiền` / `Phương thức` / `Trạng thái` for payments), and a count badge on each tab
  - opening the invoice form closes the payment form and vice versa, with per-form error/state reset
  - cancel-invoice and cancel-payment buttons use `<ConfirmDialog>` with `danger` styling instead of `window.confirm`
  - after a successful payment, the invoice form (if still open for the same class) refreshes both `/classes/{id}/tuition-summary` and `/classes/{id}/invoice-period` so the realtime summary card stays in sync
- keep `docs/database_implementation.md` and `docs/completion_matrix.md` aligned with future live verification batches
- keep `docs/completion_matrix.md` as the exact PASS/PARTIAL/FAIL source for future batches


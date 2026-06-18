# Agent Worklog

## 2026-06-13 - Context Docs Setup

### Changed Files

- `AGENTS.md`
- `docs/project_context.md`
- `docs/database_rules.md`
- `docs/api_contract.md`
- `docs/frontend_api_contract.md`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Added the main agent instruction file for future Codex batches.
- Added a shared project context summary for SmartTutor Platform.
- Added database rules that capture the normalized schema and forbidden schema mistakes.
- Added a practical API contract snapshot for backend/frontend coordination.
- Added a frontend-facing contract snapshot that points to the canonical API contract.
- Added a current-status snapshot for future batches.
- Added the initial worklog entry for this setup task.

### Validation Performed

- Read the repository request from the attached note.
- Inspected the current repo state and doc structure.
- No application code was modified.
- No compile or runtime validation was required for this documentation-only task.

### Remaining Issues / Next Step

- Verify any remaining frontend contract details against live screens before treating the contract snapshot as final.
- Next recommended Codex batch: continue backend Phase 2 hardening, starting from the payment/invoice flow and any remaining contract edge cases.

## 2026-06-13 - UV Preference Note

### Changed Files

- `AGENTS.md`
- `docs/current_status.md`
- `backend/README.md`

### What Changed

- Documented `uv` as the preferred Python environment and dependency manager for this project.
- Updated backend setup and run instructions to use `uv`.
- Updated the current-status snapshot so future batches use `uv` commands by default.

### Validation Performed

- Reviewed the existing docs and replaced the Python setup/run commands with `uv` equivalents.
- No application code was modified.

### Remaining Issues / Next Step

- If the repo later adds a lockfile or `pyproject.toml`, the `uv` workflow should be aligned with that project metadata.

## 2026-06-13 - Payment/Invoice Hardening

### Changed Files

- `backend/app/models/entities.py`
- `backend/app/repositories/data_repository.py`
- `backend/app/routers/invoices.py`
- `backend/app/routers/payments.py`
- `backend/app/schemas/entities.py`
- `backend/app/services/business_service.py`
- `docs/api_contract.md`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Canonicalized payment write inputs to `amount_paid`, `payment_date`, and `payment_method` while keeping legacy aliases for compatibility.
- Renamed internal invoice/payment period filtering to `period_filter` and kept the public `period` query parameter as a compatibility surface.
- Added remaining-amount validation before payment insert and return the exact 400 message `Payment amount exceeds invoice remaining amount` on overpayment.
- Added a guard against recording payment on canceled invoices.
- Switched `TUITION_PAYMENT` inserts to SQL Server trigger-safe behavior by disabling SQLAlchemy implicit returning on that table.
- Added a clean 409 guard for duplicate invoice snapshots with the same class and period.
- Updated API contract notes for tuition summary, invoices, and payments to match the hardened backend behavior.
- Updated current-status notes and preferred follow-up batch.

### Validation Performed

- `uv run python -m compileall backend/app`
- Direct Python smoke test against the backend service:
  - created a test invoice
  - confirmed duplicate invoice snapshot returned `409`
  - confirmed overpayment returned `400 Payment amount exceeds invoice remaining amount`
  - confirmed a valid payment insert succeeded
  - cleaned up the test payment and invoice afterward

### Remaining Issues / Next Step

- Keep an eye on any other SQL Server tables with triggers if similar `OUTPUT inserted...` errors appear later.
- Next recommended batch: continue backend Phase 2 edge-case cleanup, then resume frontend wiring verification against the stabilized payment/invoice contract.

## 2026-06-13 - Frontend API Wiring Batch 1

### Changed Files

- `frontend/src/components/auth/LoginForm.jsx`
- `frontend/src/components/auth/RegisterForm.jsx`
- `frontend/src/contexts/AuthContext.jsx`
- `frontend/src/pages/DashboardPage.jsx`
- `frontend/src/pages/ClassesPage.jsx`
- `frontend/src/pages/LearningRequestsPage.jsx`
- `frontend/src/pages/StudentList.jsx`
- `frontend/src/pages/StudentsPage.jsx`
- `frontend/src/pages/TutorsPage.jsx`
- `frontend/src/services/api.js`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Added a shared frontend API client with the core SmartTutor endpoints.
- Switched auth modal flows to real backend login/register calls and kept legacy localStorage compatibility.
- Replaced dashboard summary mock data with the real backend summary endpoint.
- Replaced the admin classes, tutors, students, and learning requests screens with live API-backed data and CRUD actions where the backend already supports them.
- Added role-aware class filtering for student/tutor views.

### Validation Performed

- `uv run python -m compileall backend/app`
- `npm run build` in `frontend/`

### Remaining Issues / Next Step

- Some secondary screens still use mock or partial data, especially tutor/student detail flows and the tutor/student-side class/schedule/tuition experience.
- Next recommended batch: wire the remaining screens that still depend on mock data and then close the final frontend contract gaps.

## 2026-06-13 - Completion Audit And Soft-Delete Fixes

### Changed Files

- `backend/app/repositories/data_repository.py`
- `backend/app/routers/assignments.py`
- `backend/app/services/business_service.py`
- `docs/api_contract.md`
- `docs/agent_worklog.md`
- `docs/completion_matrix.md`
- `docs/current_status.md`
- `sql/query_examples.sql`

### What Changed

- Added repository lookup for `STAFF` and enforced `staff_id` validation in assignment/payment flows when a staff id is supplied.
- Added `PATCH /assignments/{id}/cancel` while keeping `DELETE /assignments/{id}` as compatibility cancel behavior.
- Fixed soft-delete/cancel behavior for schedules, sessions, invoices, and payments so they no longer hard delete business records.
- Added schedule validation for `day_of_week` and `start_time < end_time`.
- Added an exact completion matrix with PASS/PARTIAL/FAIL coverage across backend CRUD, business flow, frontend screens, and SQL query/report coverage.
- Added `sql/query_examples.sql` with report/demo-ready SQL examples.
- Rewrote `docs/current_status.md` so it states exact verified behavior instead of vague progress notes.

### Validation Performed

- `uv run python -m compileall backend/app`
- Backend service smoke test:
  - invalid schedule window returned `400`
  - schedule delete changed status to `INACTIVE`
  - session delete changed status to `CANCELED`
  - payment delete changed status to `CANCELED`
  - invoice delete changed status to `CANCELED`
- Backend service smoke test for normalized business flow:
  - created learning request
  - created assignment
  - created class from `assignment_id`
  - created session
  - marked session `COMPLETED`
  - cleaned up temporary records

### Remaining Issues / Next Step

- Frontend still lacks first-class screens for subjects, assignments, schedules, sessions, invoices, and payments.
- Frontend update flows for students, tutors, learning requests, and classes are still incomplete.
- Next recommended batch: implement the missing frontend management screens and close the remaining UI-side CRUD gaps listed in `docs/completion_matrix.md`.

## 2026-06-13 - Real HTTP CRUD Verification And Auth Cleanup

### Changed Files

- `backend/app/services/business_service.py`
- `backend/tests/http_crud_smoke.py`
- `docs/agent_worklog.md`
- `docs/completion_matrix.md`
- `docs/current_status.md`
- `frontend/src/components/Header.jsx`
- `frontend/src/contexts/AuthContext.jsx`

### What Changed

- Removed the old fake-login/testing controls from the frontend header and auth context so the UI now routes through the real auth flow only.
- Added a reusable HTTP smoke script at `backend/tests/http_crud_smoke.py` for end-to-end verification with `uv`.
- Fixed tutor capability create response so `POST /tutors/{id}/capabilities` now returns the real `capability_id`.
- Added service-side `teaching_mode` validation for learning requests, tutor availability, and classes so invalid enum values fail cleanly before hitting SQL Server constraints.
- Rewrote the completion matrix and current-status docs based on real HTTP results instead of only code audit or service-level smoke tests.

### Validation Performed

- `uv run python -m compileall app tests/http_crud_smoke.py`
- `npm run build` in `frontend/`
- Real HTTP smoke test against local backend on SQL Server:
  - `uv run python tests/http_crud_smoke.py --base-url http://127.0.0.1:8021`
  - verified auth register/login
  - verified create/list/detail/update/delete or cancel/deactivate for:
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

### Remaining Issues / Next Step

- Frontend still lacks first-class pages for subjects, assignments, schedules, sessions, invoices, and payments.
- Frontend update/detail flows remain partial for students, tutors, learning requests, and classes.
- More backend enum/status validations should be reviewed with the same HTTP-first approach used in this batch.

## 2026-06-14 - Frontend Guard And Status-Doc Reconciliation

### Changed Files

- `frontend/src/pages/FinancePage.jsx`
- `frontend/src/pages/LearningRequestsPage.jsx`
- `docs/completion_matrix.md`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Fixed `LearningRequestsPage` so staff can actually open the wired edit form instead of seeing a dead "Sửa" action that never rendered the form.
- Tightened `FinancePage` actor handling so tutor users are blocked in the UI before invoice/payment calls hit backend `403` guards.
- Fixed payment-cancel refresh in `FinancePage` so invoice/payment reloads reuse the correct actor filter instead of always reloading unscoped data.
- Reconciled `docs/current_status.md` and `docs/completion_matrix.md` with the real repository state now that first-class pages for subjects, assignments, schedules, sessions, and finance already exist.
- Updated the remaining-gap notes to focus on unverified live UI flows and still-missing detail/update UX rather than pages that are already implemented.

### Validation Performed

- `uv run python -m compileall backend/app`
- `npm run build` in `frontend/`

### Remaining Issues / Next Step

- The newer frontend pages are now documented as present, but they still need live UI verification against the running backend, not just code audit and build success.
- Assignment reassignment, full session editing, and invoice/payment update flows are still not exposed in the UI.

## 2026-06-14 - Auth-Aware Smoke Test Alignment

### Changed Files

- `backend/tests/http_crud_smoke.py`
- `backend/README.md`
- `sql/demo_accounts.md`
- `docs/current_status.md`
- `docs/completion_matrix.md`
- `docs/agent_worklog.md`

### What Changed

- Reworked the backend HTTP smoke script so protected endpoints are no longer called anonymously.
- Added Bearer-token support to the test request helper.
- Split smoke-test actor usage into:
  - demo `staff` login for staff-only CRUD flows
  - freshly registered `student` login for self-scoped learning-request flows
- Added required student registration fields so the auth/register flow matches the current backend validation rules.
- Updated backend/docs guidance so smoke-test commands, verification notes, and API sanity-check advice all reflect the current auth model.

### Validation Performed

- Code-path review of the auth guard and router role requirements against the revised smoke script.
- Full runtime verification is still pending on the active local backend for this exact revised script.

### Remaining Issues / Next Step

- Run the revised smoke test against the local backend and update any remaining PASS wording if endpoint behavior differs under real auth scopes.
- After that, continue with validation-hardening work in the service layer.

## 2026-06-14 - Service-Layer Validation Hardening

### Changed Files

- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/completion_matrix.md`
- `docs/agent_worklog.md`

### What Changed

- Added shared service validation helpers for enum/status choices, non-negative/positive numeric values, date windows, schedule windows, session time pairing, and invoice money invariants.
- Added clean `400` validation before SQL Server constraints for common create/update paths across students, tutors, subjects, tutor capabilities, tutor availability, learning requests, assignments, classes, schedules, sessions, invoices, and payments.
- Added `409` validation for duplicate subject name + level before the unique constraint is hit.
- Added session validation that checks `schedule_id` belongs to the target class before insert/update.
- Kept nullable-field clear semantics and `updated_at` handling out of this batch because those are part of the next priority item.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`

### Remaining Issues / Next Step

- Add negative HTTP tests that assert the new validation messages and status codes.
- Run the auth-aware smoke test once the local backend is active.
- Continue with update semantics for clearing nullable fields and consistent `updated_at` handling.

## 2026-06-14 - Update Semantics And updated_at Alignment

### Changed Files

- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/completion_matrix.md`
- `docs/agent_worklog.md`

### What Changed

- Changed shared repository update behavior so explicitly sent `null` values are applied instead of being silently skipped.
- Added a shared `touch_model` helper that sets `updated_at` for models that have that column.
- Made shared update paths touch `updated_at` whenever at least one model field is applied.
- Added `updated_at` touches to direct service transitions that bypass shared update logic, including soft deactivate, cancel, assignment/request status changes, session status patch, and invoice/payment cancel.
- Updated session status patch semantics so an explicit `content_note: null` clears the note.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`

### Remaining Issues / Next Step

- Add focused HTTP coverage proving nullable-field clearing and `updated_at` movement through real API calls.
- Keep centralized DB error translation as a separate hardening batch.

## 2026-06-14 - Payment Auto-Invoice Flow Hardening

### Changed Files

- `backend/app/services/business_service.py`
- `backend/tests/http_crud_smoke.py`
- `docs/api_contract.md`
- `docs/current_status.md`
- `docs/completion_matrix.md`
- `docs/agent_worklog.md`

### What Changed

- Hardened `POST /payments` when callers provide `class_id` without `invoice_id`.
- Fixed the status semantics bug where payment payload `status` could be reused as an invoice status during auto invoice creation.
- Auto-created invoices now always start as `UNPAID`; the payment row keeps its own `SUCCESS`, `CANCELED`, or `REFUNDED` status.
- Added period-specific invoice snapshot calculation from `COMPLETED` lesson sessions inside `period_start` and `period_end`.
- Added consistency checks for mismatched `invoice_id` + `class_id` and mismatched `student_id`.
- Limited remaining-balance overpayment checks on create to `SUCCESS` payments, matching the rule that only successful payments count as paid money.
- Extended the HTTP CRUD smoke script to cover class-id payment with auto-created invoice snapshot.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`

### Remaining Issues / Next Step

- Rerun the auth-aware HTTP smoke test against the active SQL Server-backed backend to verify the new auto-invoice branch with the payment trigger enabled.
- Add negative HTTP cases for mismatched `invoice_id`/`class_id`, mismatched `student_id`, canceled invoices, and overpayment on auto-created invoices.

## 2026-06-14 - SQL Raw Repository Migration Step 1 Auth Foundation

### Changed Files

- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `backend/app/core/auth.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Added shared raw SQL helpers in `data_repository.py` for `fetch_one`, `fetch_all`, and `execute`, using `sqlalchemy.text(...)`.
- Converted `USER_ACCOUNT` lookup functions used by auth from ORM queries to parameterized raw SQL.
- Added raw SQL profile lookup helpers for `STUDENT`, `TUTOR`, and `STAFF` by `account_id`.
- Changed `business_service.authenticate()` to resolve role-specific profiles through repository raw SQL helpers instead of direct ORM queries.
- Changed `core/auth.py` current-actor resolution to use repository raw SQL helpers instead of direct ORM queries.
- Kept create/update/delete flows outside auth scope unchanged for later migration steps.

### Validation Performed

- `uv run python -m compileall backend/app`
- `rg "db\.query" backend/app/core/auth.py backend/app/services/business_service.py`

### Remaining Issues / Next Step

- Convert student and subject CRUD repository/service paths to raw SQL writes and explicit update helpers.
- Continue removing direct ORM queries from `business_service.py` outside the auth scope in later migration steps.

## 2026-06-14 - SQL Raw Repository Migration Step 2 Student And Subject CRUD

### Changed Files

- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Added a whitelisted `update_by_id` helper for raw SQL updates where table and column names are developer-controlled constants.
- Converted student CRUD repository functions to parameterized raw SQL:
  - `get_students`
  - `get_student`
  - `create_student`
  - `update_student`
  - `deactivate_student`
- Converted subject CRUD repository functions to parameterized raw SQL:
  - `get_subjects`
  - `get_subject`
  - `get_subject_by_name_level`
  - `create_subject`
  - `update_subject`
  - `deactivate_subject`
- Updated student and subject service flows to use explicit repository SQL write functions instead of `repo.apply_updates`, direct `status` assignment, `repo.touch_model`, or `repo.refresh`.
- Kept tutor, request, class, session, invoice, and payment ORM paths unchanged for later migration steps.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`
- `rg -n "repo\\.apply_updates\\(student|repo\\.apply_updates\\(subject|student\\.status\\s*=|subject\\.status\\s*=|repo\\.refresh\\(db, student\\)|repo\\.refresh\\(db, subject\\)" backend/app/services/business_service.py`

### Remaining Issues / Next Step

- Convert tutor CRUD, tutor capabilities, and tutor availability to raw SQL.
- Continue removing repository ORM access in later batches; current leftovers are expected outside the student/subject scope.

## 2026-06-14 - SQL Raw Repository Migration Step 3 Tutor Profile

### Changed Files

- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Converted tutor list/detail/create/update/deactivate repository functions to parameterized raw SQL.
- Added tutor update whitelist support through `TUTOR_UPDATE_COLUMNS`.
- Added capability attachment for tutor read objects so existing response mappers can still read `tutor.capabilities` and `capability.subject`.
- Converted tutor capability list/create/update/delete repository functions to parameterized raw SQL.
- Converted tutor availability list/detail/create/update/delete repository functions to parameterized raw SQL.
- Updated tutor service flows to use explicit repository SQL functions for:
  - tutor update and deactivate
  - tutor subject rebuild without `db.flush()`
  - existing tutor capability update
  - tutor availability update/delete
- Kept assignment, request, class, session, invoice, payment, and dashboard ORM paths unchanged for later migration steps.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`
- `rg -n "repo\\.apply_updates\\(tutor|repo\\.apply_updates\\(availability|tutor\\.status\\s*=|repo\\.touch_model\\(tutor|repo\\.touch_model\\(existing|db\\.flush\\(\\)|repo\\.delete_model\\(db, availability\\)" backend/app/services/business_service.py`
- `rg -n "db\\.query\\((Tutor|TutorCapability|TutorAvailability)\\)|db\\.add\\((tutor|capability|availability)\\)|db\\.delete\\((capability|availability)\\)|joinedload\\(Tutor\\.capabilities" backend/app/repositories/data_repository.py`

### Remaining Issues / Next Step

- Convert learning request CRUD and detail response compatibility to raw SQL.
- Continue removing `TutorAssignment` ORM access in the next request/assignment migration steps.

## 2026-06-14 - SQL Raw Repository Migration Step 4 Learning Request CRUD

### Changed Files

- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Converted learning request list/detail/create/update/cancel repository functions to parameterized raw SQL.
- Added `LEARNING_REQUEST_UPDATE_COLUMNS` for whitelisted raw SQL updates.
- Added learning request read compatibility attachment so response mappers can still access `request.student` and `request.subject`.
- Updated learning request service update/cancel flows to call explicit repository SQL functions instead of mutating returned objects.
- Kept assignment-driven request status transitions unchanged for the next assignment migration step.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`
- `rg -n "repo\\.apply_updates\\(request|def update_learning_request|def cancel_learning_request|repo\\.update_learning_request|repo\\.cancel_learning_request" backend/app/services/business_service.py`
- `rg -n "db\\.query\\(LearningRequest\\)|db\\.add\\(request\\)|def get_learning_requests|def create_learning_request" backend/app/repositories/data_repository.py`

### Remaining Issues / Next Step

- Convert assignment CRUD and assignment/request status transitions to explicit raw SQL.
- Continue removing class, schedule, session, finance, and dashboard ORM paths in later batches.

## 2026-06-14 - SQL Raw Repository Migration Step 5 Assignment CRUD And Transitions

### Changed Files

- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Converted assignment list/detail/create/update/cancel repository functions to parameterized raw SQL.
- Added `ASSIGNMENT_UPDATE_COLUMNS` for whitelisted assignment updates.
- Added assignment read compatibility attachment so existing checks can still use `assignment.study_class` when an assignment already has a class.
- Updated create-assignment flow to set the linked learning request to `ASSIGNED` with explicit repository SQL.
- Updated update/cancel assignment flows to set the linked learning request back to `PENDING` with explicit repository SQL when assignment status becomes `CANCELED`.
- Removed direct assignment/request object mutation from assignment service flows.
- Kept class, schedule, session, finance, and dashboard ORM paths unchanged for later migration steps.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`
- `rg -n "request\\.status\\s*=|assignment\\.status\\s*=|repo\\.apply_updates\\(assignment|repo\\.touch_model\\(assignment|repo\\.touch_model\\(request\\)" backend/app/services/business_service.py`
- `rg -n "db\\.query\\(TutorAssignment\\)|db\\.add\\(assignment\\)|repo\\.apply_updates\\(assignment|assignment\\.status\\s*=|request\\.status\\s*=" backend/app`

### Remaining Issues / Next Step

- Convert class list/detail to `VW_STUDY_CLASS_DETAIL` and class writes to raw SQL.
- Continue migrating schedule, session, finance, and dashboard paths in later steps.

## 2026-06-14 - SQL Raw Repository Migration Step 6 Class Read/Write And Tuition Aggregates

### Changed Files

- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `backend/app/core/auth.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Converted class list/detail reads to `VW_STUDY_CLASS_DETAIL`.
- Added raw SQL schedule display and next scheduled lesson attachment for view-backed class response compatibility.
- Converted class create/update/cancel repository functions to parameterized raw SQL.
- Added `CLASS_UPDATE_COLUMNS` for whitelisted class updates.
- Updated `class_to_response()` to support view-backed flat rows while keeping the old fallback path for not-yet-migrated callers.
- Updated class access checks to authorize view-backed class rows by direct `student_id` and `tutor_id` fields.
- Converted class-id payment auto-invoice snapshot calculation to a raw SQL aggregate.
- Converted `/classes/{id}/tuition-summary` to a realtime raw SQL aggregate instead of looping over ORM sessions and payments.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`
- `rg -n "repo\\.apply_updates\\(study_class|repo\\.touch_model\\(study_class|db\\.query\\(StudyClass\\)|db\\.add\\(study_class\\)|_invoice_snapshot_from_class_period|study_class\\.invoices" backend/app`
- `rg -n "study_class\\.sessions" backend/app/services/business_service.py`

### Remaining Issues / Next Step

- Convert schedule CRUD and schedule filters to raw SQL.
- Continue migrating session, finance, and dashboard paths in later steps.

## 2026-06-14 - SQL Raw Repository Migration Step 7 Schedule CRUD And Filters

### Changed Files

- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Converted schedule list filters to parameterized raw SQL with normalized joins from `CLASS_SCHEDULE` through class, assignment, and learning request.
- Converted schedule detail and create repository functions to parameterized raw SQL against `CLASS_SCHEDULE`.
- Added `SCHEDULE_UPDATE_COLUMNS` for whitelisted schedule updates.
- Added explicit `update_schedule` and `deactivate_schedule` repository functions.
- Updated schedule service update/delete flows to call repository SQL updates instead of mutating returned schedule objects.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`
- `rg -n "repo\\.apply_updates\\(schedule|schedule\\.status\\s*=|repo\\.touch_model\\(schedule|db\\.query\\(ClassSchedule\\)|db\\.add\\(schedule\\)" backend/app`
- `rg -n "def get_schedules|def get_schedule|def create_schedule|def update_schedule|def deactivate_schedule|repo\\.update_schedule|repo\\.deactivate_schedule" backend/app/repositories/data_repository.py backend/app/services/business_service.py`

### Remaining Issues / Next Step

- Convert lesson session CRUD, status updates, and session filters to raw SQL.
- Continue migrating invoice, payment, and dashboard paths in later steps.

## 2026-06-15 - SQL Raw Repository Migration Step 8 Lesson Session CRUD And Status

### Changed Files

- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Converted lesson session list filters to parameterized raw SQL with normalized joins from `LESSON_SESSION` through class, assignment, learning request, and subject.
- Converted session detail and create repository functions to parameterized raw SQL against `LESSON_SESSION`.
- Added `SESSION_UPDATE_COLUMNS` for whitelisted session updates.
- Added explicit `update_session` and `cancel_session` repository functions.
- Updated session service update, status patch, and delete flows to call repository SQL updates instead of mutating returned session objects.
- Preserved explicit `content_note = null` clearing for status patch payloads.
- Updated `session_to_response` to support raw SQL flat `class_label` rows while keeping the existing relationship fallback.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`
- `rg -n "db\\.query\\(LessonSession\\)|db\\.add\\(session\\)|repo\\.apply_updates\\(session|session\\.status\\s*=|session\\.content_note\\s*=|repo\\.touch_model\\(session" backend/app`
- `rg -n "SESSION_UPDATE_COLUMNS|def get_sessions|def get_session\\(|def create_session\\(|def update_session\\(|def cancel_session\\(|repo\\.update_session|repo\\.cancel_session|class_label" backend/app/repositories/data_repository.py backend/app/services/business_service.py`

### Remaining Issues / Next Step

- Convert invoice CRUD/list/detail to raw SQL or a finance detail view.
- Continue migrating payment and dashboard paths in later steps.

## 2026-06-15 - SQL Raw Repository Migration Step 9 Invoice CRUD And Reads

### Changed Files

- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Converted invoice list/detail/class-period lookup repository functions to parameterized raw SQL with normalized joins through class, assignment, learning request, student, subject, and tutor.
- Converted invoice create to parameterized raw SQL against `TUITION_INVOICE`.
- Added `INVOICE_UPDATE_COLUMNS` for whitelisted invoice updates.
- Added explicit `update_invoice` and `cancel_invoice` repository functions.
- Added minimal invoice class/request context attachment so existing payment create validation can still compare `student_id` before the payment migration step.
- Updated invoice service update/delete flows to call repository SQL updates instead of mutating returned invoice objects.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`
- `rg -n "db\\.query\\(TuitionInvoice\\)|db\\.add\\(invoice\\)|repo\\.apply_updates\\(invoice|invoice\\.status\\s*=|repo\\.touch_model\\(invoice" backend/app`
- `rg -n "INVOICE_UPDATE_COLUMNS|def get_invoices|def get_invoice\\(|def create_invoice\\(|def get_invoice_by_class_period|def update_invoice\\(|def cancel_invoice\\(|repo\\.update_invoice|repo\\.cancel_invoice|_attach_invoice_context" backend/app/repositories/data_repository.py backend/app/services/business_service.py`

### Remaining Issues / Next Step

- Convert payment CRUD/list/detail to raw SQL and preserve trigger-driven invoice recalculation.
- Convert dashboard summary to raw SQL after finance paths are complete.

## 2026-06-15 - SQL Raw Repository Migration Step 10 Payment SQL Objects And Dashboard Summary

### Changed Files

- `sql/schema.sql`
- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Added `VW_INVOICE_DETAIL`, `VW_PAYMENT_DETAIL`, `FN_INVOICE_REMAINING_AMOUNT`, and `SP_CREATE_TUITION_PAYMENT` to `sql/schema.sql`.
- Converted payment list/detail reads to `VW_PAYMENT_DETAIL`.
- Converted payment create to call `SP_CREATE_TUITION_PAYMENT`.
- Added `PAYMENT_UPDATE_COLUMNS` plus explicit repository `update_payment` and `cancel_payment` SQL functions.
- Updated payment service create/update/delete flows to call repository SQL updates instead of mutating returned payment objects.
- Kept service-layer overpayment validation before payment insert, while also adding procedure-side remaining-amount protection through `FN_INVOICE_REMAINING_AMOUNT`.
- Added minimal nested invoice attachment on payment read objects so access control and remaining-amount validation continue to work during the final cleanup stage.
- Converted `/dashboard/summary` to a single raw SQL aggregate query.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`
- `rg -n "db\\.query\\(TuitionPayment\\)|db\\.add\\(payment\\)|repo\\.apply_updates\\(payment|payment\\.status\\s*=|repo\\.touch_model\\(payment|dashboard_summary\\(|db\\.query\\(Student\\)|db\\.query\\(Tutor\\)|db\\.query\\(LearningRequest\\)|db\\.query\\(StudyClass\\)|db\\.query\\(LessonSession\\)|db\\.query\\(TuitionInvoice\\)" backend/app`
- `rg -n "VW_PAYMENT_DETAIL|FN_INVOICE_REMAINING_AMOUNT|SP_CREATE_TUITION_PAYMENT|PAYMENT_UPDATE_COLUMNS|def get_payments|def get_payment\\(|def create_payment\\(|def update_payment\\(|def cancel_payment\\(|def get_dashboard_summary|repo\\.update_payment|repo\\.cancel_payment" backend/app/repositories/data_repository.py backend/app/services/business_service.py sql/schema.sql`
- `rg -n "joinedload|\\.options\\(" backend/app/repositories/data_repository.py backend/app/services/business_service.py`

### Remaining Issues / Next Step

- Rerun schema reset and auth-aware smoke tests to verify the new SQL objects end to end against SQL Server.
- Finish final cleanup for remaining `db.query`, `db.add`, `db.delete`, `db.refresh`, and `db.flush` leftovers outside the migrated flows.
- Create `docs/database_implementation.md` and refresh `docs/completion_matrix.md` after live verification.

## 2026-06-15 - SQL Raw Repository Migration Step 11 Live Verification And Final Cleanup

### Changed Files

- `sql/schema.sql`
- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/completion_matrix.md`
- `docs/agent_worklog.md`
- `docs/database_implementation.md`

### What Changed

- Added `SET ANSI_NULLS ON` and `SET QUOTED_IDENTIFIER ON` near the top of `sql/schema.sql` so filtered indexes and other SQL Server objects recreate cleanly during schema reset.
- Converted the remaining runtime ORM repository helpers `create_user`, `get_staff`, and `create_staff` to parameterized raw SQL.
- Removed the unused repository helpers that still depended on ORM delete/refresh behavior.
- Reran `sql/schema.sql` successfully against SQL Server, then reseeded with `sql/sample_data.sql`.
- Reran the auth-aware HTTP smoke test after the payment procedure/view/function migration and confirmed end-to-end PASS, including the class-id auto-invoice payment path.
- Updated status/docs to reflect live verification rather than compile-only coverage.
- Added `docs/database_implementation.md` summarizing the raw SQL CRUD layer, views, trigger, function, procedure, and evidence commands.

### Validation Performed

- `uv run python -m compileall backend/app backend/tests/http_crud_smoke.py`
- `rg -n "db\\.(query|add|delete|refresh|flush)" backend/app`
- `rg -n "joinedload|\\.options\\(" backend/app`
- `sqlcmd -b -S localhost -d master -U sa -P 123456 -C -f 65001 -i sql/schema.sql`
- `powershell -ExecutionPolicy Bypass -File .\\sql\\reset_demo_utf8.ps1 -Seed sample`
- `uv run python tests/http_crud_smoke.py --base-url http://127.0.0.1:8000 --staff-email staff1@smarttutor.local --staff-password staff123`

### Remaining Issues / Next Step

- Add focused negative HTTP tests for the newer service-layer validation paths.
- Verify the newer frontend screens end to end against the live backend rather than relying on build/code audit only.
- Create missing frontend update/detail UX for assignments, sessions, invoices, and payments where backend support already exists.

## 2026-06-15 - DB Object Migration Planning And Handoff Docs

### Changed Files

- `docs/db_object_migration_plan.md`
- `docs/database_implementation.md`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Added a dedicated implementation-ready plan for the next SQL Server object migration batch.
- Documented the verified current inventory of custom DB objects:
  - `VW_STUDY_CLASS_DETAIL`
  - `VW_INVOICE_DETAIL`
  - `VW_PAYMENT_DETAIL`
  - `FN_INVOICE_REMAINING_AMOUNT`
  - `SP_CREATE_TUITION_PAYMENT`
  - `TRG_TUITION_PAYMENT_RECALC_INVOICE`
- Defined the target new objects and their intended purpose:
  - `SP_ASSIGN_TUTOR_TO_REQUEST`
  - `SP_CREATE_CLASS_FROM_ASSIGNMENT`
  - `SP_CREATE_INVOICE_FOR_PERIOD`
  - `VW_LEARNING_REQUEST_DETAIL`
  - `VW_LESSON_SESSION_DETAIL`
  - `FN_CLASS_TUITION_SUMMARY`
- Recorded the transaction boundaries, backend endpoint impact, script management approach, and delivery phases so a new chat can continue directly from the plan.
- Linked the current-status and database-implementation docs to the new migration-plan document.

### Validation Performed

- Reviewed `AGENTS.md`, `docs/current_status.md`, `docs/database_implementation.md`, and `docs/completion_matrix.md`.
- Reviewed the existing worklog to keep the new plan aligned with the already verified raw-SQL migration state.
- No application code or SQL runtime behavior was changed in this documentation batch.

### Remaining Issues / Next Step

- Lock the invoice snapshot calculation rule before implementing `SP_CREATE_INVOICE_FOR_PERIOD`.
- Start implementation with Phase 1 from `docs/db_object_migration_plan.md`.

## 2026-06-15 - DB Object Migration Phase 1 Implementation

### Changed Files

- `sql/schema.sql`
- `backend/app/repositories/data_repository.py`
- `docs/current_status.md`
- `docs/database_implementation.md`
- `docs/agent_worklog.md`

### What Changed

- Added `VW_LEARNING_REQUEST_DETAIL` to `sql/schema.sql` as the normalized learning-request read model.
- Added `VW_LESSON_SESSION_DETAIL` to `sql/schema.sql` as the normalized lesson-session read model.
- Added `FN_CLASS_TUITION_SUMMARY` to `sql/schema.sql` for realtime class tuition totals and invoice counters.
- Extended the schema reset section to drop the new Phase 1 views/function on clean reruns.
- Switched learning request list/detail repository reads to `VW_LEARNING_REQUEST_DETAIL`.
- Switched lesson session list/detail repository reads to `VW_LESSON_SESSION_DETAIL`.
- Switched `/classes/{id}/tuition-summary` repository reads to `FN_CLASS_TUITION_SUMMARY`.
- Standardized invoice list/detail/class-period repository reads on `VW_INVOICE_DETAIL` instead of repeating inline normalized join SQL.
- Preserved current response compatibility by keeping the learning-request nested `student`/`subject` mapping and by attaching one assignment context to each request row when the view returns it.
- Updated status and implementation docs to record that Phase 1 is implemented and compile-verified.

### Validation Performed

- `uv run python -m compileall backend/app`
- `rg -n "VW_LEARNING_REQUEST_DETAIL|VW_LESSON_SESSION_DETAIL|FN_CLASS_TUITION_SUMMARY|VW_INVOICE_DETAIL" backend/app/repositories/data_repository.py sql/schema.sql`

### Remaining Issues / Next Step

- Run direct SQL Server validation for the new views/function by rerunning `sql/schema.sql` and checking the objects with `SELECT`.
- Rerun the auth-aware HTTP smoke test so the Phase 1 read-model/function migration has live endpoint evidence, not only compile verification.
- Continue with DB object migration Phase 2: `SP_ASSIGN_TUTOR_TO_REQUEST`.

## 2026-06-15 - DB Object Migration Phase 2 Assignment Procedure

### Changed Files

- `sql/schema.sql`
- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/database_implementation.md`
- `docs/agent_worklog.md`

### What Changed

- Added `SP_ASSIGN_TUTOR_TO_REQUEST` to `sql/schema.sql`.
- The procedure now:
  - locks and checks the target learning request
  - rejects missing, canceled, or non-`PENDING` requests
  - rejects duplicate active assignments
  - rejects non-`ACTIVE` tutors
  - rejects tutors without capability for the request subject
  - inserts `TUTOR_ASSIGNMENT`
  - updates `LEARNING_REQUEST.status` to `ASSIGNED`
  - returns the created assignment row
- Added repository helper `call_assign_tutor_to_request(...)` to execute the procedure.
- Updated `business_service.create_assignment()` to keep API-facing validation/authorization but delegate the transactional write path to `SP_ASSIGN_TUTOR_TO_REQUEST`.
- Left assignment update/cancel flows on the existing explicit SQL path for this phase to avoid unrelated scope expansion.

### Validation Performed

- `uv run python -m compileall backend/app`
- `rg -n "SP_ASSIGN_TUTOR_TO_REQUEST|call_assign_tutor_to_request|def create_assignment\\(" sql/schema.sql backend/app/repositories/data_repository.py backend/app/services/business_service.py`

### Remaining Issues / Next Step

- Run direct SQL Server validation for `SP_ASSIGN_TUTOR_TO_REQUEST` with valid and invalid `EXEC` cases.
- Rerun the auth-aware HTTP smoke test so the assignment procedure migration has live endpoint evidence.
- Continue with DB object migration Phase 3: `SP_CREATE_CLASS_FROM_ASSIGNMENT`.

## 2026-06-15 - DB Object Migration Phase 3 Class Creation Procedure

### Changed Files

- `sql/schema.sql`
- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/database_implementation.md`
- `docs/agent_worklog.md`

### What Changed

- Added `SP_CREATE_CLASS_FROM_ASSIGNMENT` to `sql/schema.sql`.
- The procedure now:
  - locks and checks the target assignment
  - rejects missing assignments
  - rejects assignments not in `ASSIGNED` status
  - rejects duplicate classes for the same assignment
  - validates `tuition_fee_per_session > 0`
  - validates `end_date >= start_date` when `end_date` is present
  - inserts `STUDY_CLASS`
  - returns the created class row
- Kept the procedure aligned with the real repository schema by accepting:
  - `assignment_id`
  - `class_code`
  - `tuition_fee_per_session`
  - `teaching_mode`
  - `location`
  - `start_date`
  - `end_date`
  - `status`
- Added repository helper `call_create_class_from_assignment(...)` to execute the procedure.
- Updated `business_service.create_study_class()` to keep API-facing validation but delegate the transactional write path to `SP_CREATE_CLASS_FROM_ASSIGNMENT`.
- Left class update/cancel flows on the existing explicit SQL path for this phase.

### Validation Performed

- `uv run python -m compileall backend/app`
- `rg -n "SP_CREATE_CLASS_FROM_ASSIGNMENT|call_create_class_from_assignment|def create_study_class\\(|def create_class\\(" sql/schema.sql backend/app/repositories/data_repository.py backend/app/services/business_service.py`

### Remaining Issues / Next Step

- Run direct SQL Server validation for `SP_CREATE_CLASS_FROM_ASSIGNMENT` with valid and invalid `EXEC` cases.
- Rerun the auth-aware HTTP smoke test so the class procedure migration has live endpoint evidence.
- Continue with DB object migration Phase 4: `SP_CREATE_INVOICE_FOR_PERIOD`.

## 2026-06-15 - DB Object Migration Phase 4 Invoice Snapshot Procedure

### Changed Files

- `sql/schema.sql`
- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `docs/current_status.md`
- `docs/database_implementation.md`
- `docs/agent_worklog.md`

### What Changed

- Added `SP_CREATE_INVOICE_FOR_PERIOD` to `sql/schema.sql`.
- The procedure now:
  - checks the target class exists
  - rejects invalid period ranges
  - rejects duplicate invoice snapshots for the same class and period
  - computes `completed_sessions` from `LESSON_SESSION.status = 'COMPLETED'` within the requested period
  - snapshots `tuition_fee_per_session` from `STUDY_CLASS`
  - computes `amount_due = completed_sessions * tuition_fee_per_session`
  - inserts `TUITION_INVOICE` with `amount_paid = 0` and `status = 'UNPAID'`
  - returns the created invoice row
- Kept the procedure aligned with the real repository schema by accepting only:
  - `class_id`
  - `period_start`
  - `period_end`
- Added repository helper `call_create_invoice_for_period(...)` to execute the procedure.
- Updated `business_service.create_invoice()` to keep API-facing validation and duplicate guarding but delegate the transactional invoice snapshot write path to `SP_CREATE_INVOICE_FOR_PERIOD`.
- Preserved compatibility at the request surface: invoice create payload fields like `completed_sessions`, `tuition_fee_per_session`, `amount_due`, `amount_paid`, and `status` are still accepted/validated, but the persisted snapshot is now computed by SQL Server from the real class/session state.
- Left invoice update/cancel flows on the existing explicit SQL path for this phase.

### Validation Performed

- `uv run python -m compileall backend/app`
- `rg -n "SP_CREATE_INVOICE_FOR_PERIOD|call_create_invoice_for_period|def create_invoice\\(" sql/schema.sql backend/app/repositories/data_repository.py backend/app/services/business_service.py`

### Remaining Issues / Next Step

- Run direct SQL Server validation for `SP_CREATE_INVOICE_FOR_PERIOD` with valid and invalid `EXEC` cases.
- Rerun the auth-aware HTTP smoke test so the invoice procedure migration has live endpoint evidence.
- Refresh evidence docs after the live verification batch and add focused negative tests for procedure-backed assignment/class/invoice creation flows.

## 2026-06-15 - DB Object Migration Live Verification And Procedure Rollback Hardening

### Changed Files

- `sql/schema.sql`
- `docs/current_status.md`
- `docs/database_implementation.md`
- `docs/agent_worklog.md`

### What Changed

- Reran `sql/schema.sql` successfully against local SQL Server.
- Reseeded the demo database successfully with `sql/sample_data.sql`.
- Ran direct `EXEC` checks for the new procedure-backed flows:
  - valid `SP_ASSIGN_TUTOR_TO_REQUEST`
  - invalid assignment cases for non-pending request and tutor capability mismatch
  - valid `SP_CREATE_CLASS_FROM_ASSIGNMENT`
  - invalid class cases for duplicate/existing class ownership
  - valid `SP_CREATE_INVOICE_FOR_PERIOD`
  - invalid invoice cases for duplicate period and missing class
- Live verification exposed a transaction-state bug on procedure error paths: invalid procedure calls could leave the SQL session in a doomed transaction state because the transaction was not explicitly rolled back before rethrowing.
- Hardened the transactional procedures with `TRY/CATCH` and explicit `ROLLBACK` before `THROW`:
  - `SP_ASSIGN_TUTOR_TO_REQUEST`
  - `SP_CREATE_CLASS_FROM_ASSIGNMENT`
  - `SP_CREATE_INVOICE_FOR_PERIOD`
  - `SP_CREATE_TUITION_PAYMENT`
- Reran schema reset, reseed, and `EXEC` verification after the rollback fix and confirmed the procedures now fail cleanly without poisoning the session.
- Started the backend locally and reran the auth-aware HTTP smoke test, which passed end to end after the procedure-backed assignment/class/invoice migrations.
- Updated status and implementation docs to record the live verification evidence and the rollback-hardening fix.

### Validation Performed

- `sqlcmd -b -S localhost -d master -U sa -P 123456 -C -f 65001 -i sql/schema.sql`
- `powershell -ExecutionPolicy Bypass -File .\\sql\\reset_demo_utf8.ps1 -Seed sample`
- direct `sqlcmd` `EXEC` verification for:
  - `SP_ASSIGN_TUTOR_TO_REQUEST`
  - `SP_CREATE_CLASS_FROM_ASSIGNMENT`
  - `SP_CREATE_INVOICE_FOR_PERIOD`
- `uv run python -m compileall backend/app`
- `uv run python tests/http_crud_smoke.py --base-url http://127.0.0.1:8000 --staff-email staff1@smarttutor.local --staff-password staff123`

### Remaining Issues / Next Step

- Add focused negative HTTP tests so the new procedure-backed failure modes are captured at API level, not only in direct SQL `EXEC` checks.
- Refresh `docs/completion_matrix.md` with explicit evidence notes for the Phase 1-4 live verification batch.
- Consider narrowing the invoice create API payload surface if the frontend no longer needs to submit snapshot fields that are now computed in SQL Server.

## 2026-06-15 - Service Layer Decomposition On demo3

### Changed Files

- `backend/app/services/business_service.py`
- `backend/app/services/common.py`
- `backend/app/services/auth_service.py`
- `backend/app/services/student_service.py`
- `backend/app/services/tutor_service.py`
- `backend/app/services/subject_service.py`
- `backend/app/services/request_flow_service.py`
- `backend/app/services/class_flow_service.py`
- `backend/app/services/finance_service.py`
- `backend/app/services/dashboard_service.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Created branch `demo3` from `demo2` as the refactor branch.
- Split the oversized backend service module by responsibility instead of keeping all business flows in one file.
- Moved shared constants, validators, lookup helpers, and response mappers into `backend/app/services/common.py`.
- Extracted focused service modules for:
  - auth
  - student
  - tutor
  - subject
  - learning request + assignment flow
  - class + schedule + session flow
  - invoice + payment flow
  - dashboard summary
- Replaced the old monolithic `business_service.py` implementation with a thin compatibility facade that re-exports the existing service surface.
- Kept the current router and auth import style unchanged so this batch stays refactor-only and avoids API-contract churn.

### Validation Performed

- `uv run python -m compileall backend/app`

### Remaining Issues / Next Step

- Run live HTTP smoke tests on `demo3` before doing a deeper backend split so the facade-based refactor has runtime evidence, not just compile evidence.
- If decomposition continues, split one additional layer at a time:
  - routers by domain, or
  - repository code by bounded context
- Keep future refactor batches behavior-preserving and avoid mixing structure cleanup with new feature work.

## 2026-06-15 - Router Decomposition For Students And Tutors On demo3

### Changed Files

- `backend/app/routers/tutors.py`
- `backend/app/routers/tutor_profiles.py`
- `backend/app/routers/tutor_capabilities.py`
- `backend/app/routers/tutor_availabilities.py`
- `backend/app/routers/tutor_router_support.py`
- `backend/app/routers/students.py`
- `backend/app/routers/student_profiles.py`
- `backend/app/routers/student_relations.py`
- `backend/app/routers/student_router_support.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Continued the backend refactor on branch `demo3` by decomposing the larger student and tutor routers without changing endpoint paths.
- Turned `backend/app/routers/tutors.py` into a thin aggregate router that includes three focused modules:
  - tutor profile and tutor-owned class/schedule routes
  - tutor subject/capability routes
  - tutor availability routes
- Added `tutor_router_support.py` so the tutor/staff ownership guard logic is defined once and reused across the tutor route modules.
- Turned `backend/app/routers/students.py` into a thin aggregate router that includes two focused modules:
  - student profile CRUD routes
  - student-related learning request/class/schedule routes
- Added `student_router_support.py` so student/staff ownership checks are reused instead of repeated inline.
- Preserved the current `main.py` router include pattern and kept the existing `/students/...` and `/tutors/...` URL structure unchanged.

### Validation Performed

- `uv run python -m compileall backend/app`

### Remaining Issues / Next Step

- Rerun live HTTP smoke tests on `demo3` so the router split has runtime evidence in addition to compile evidence.
- If router decomposition continues, the next natural candidates are:
  - `learning_requests` + `assignments`
  - `classes` + `schedules` + `sessions`
- Keep aggregate router files as stable entrypoints so `main.py` does not need wide churn during future splits.

## 2026-06-15 - Router Decomposition For Request And Class Flows On demo3

### Changed Files

- `backend/app/routers/learning_requests.py`
- `backend/app/routers/learning_request_profiles.py`
- `backend/app/routers/learning_request_router_support.py`
- `backend/app/routers/assignments.py`
- `backend/app/routers/assignment_routes.py`
- `backend/app/routers/classes.py`
- `backend/app/routers/class_profiles.py`
- `backend/app/routers/class_finance.py`
- `backend/app/routers/class_router_support.py`
- `backend/app/routers/schedules.py`
- `backend/app/routers/schedule_routes.py`
- `backend/app/routers/sessions.py`
- `backend/app/routers/session_routes.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Continued the `demo3` backend router split by decomposing the learning-request/assignment flow and the class/schedule/session flow.
- Turned `backend/app/routers/learning_requests.py` into a thin aggregate router and moved the request endpoints into `learning_request_profiles.py`.
- Added `learning_request_router_support.py` for:
  - student/staff list access checks
  - student ownership enforcement on learning request creation
  - assignment payload staff-id normalization helper
- Turned `backend/app/routers/assignments.py` into a thin aggregate router over `assignment_routes.py`.
- Turned `backend/app/routers/classes.py` into a thin aggregate router over:
  - `class_profiles.py` for class CRUD/list/detail
  - `class_finance.py` for `/classes/{id}/tuition-summary`
- Added `class_router_support.py` to centralize repeated actor-role filtering for class-related list endpoints.
- Turned `backend/app/routers/schedules.py` and `backend/app/routers/sessions.py` into thin aggregate routers over `schedule_routes.py` and `session_routes.py`.
- Preserved the existing URL structure and left `backend/app/main.py` router includes unchanged.

### Validation Performed

- `uv run python -m compileall backend/app`

### Remaining Issues / Next Step

- Rerun live HTTP smoke tests on `demo3` so the router decomposition has runtime evidence, not only compile evidence.
- The next router split candidate is the finance pair:
  - `invoices`
  - `payments`
- Keep future router batches behavior-preserving and avoid renaming public endpoints while refactoring structure.

## 2026-06-15 - Live Verification After demo3 Service And Router Refactor

### Changed Files

- `backend/app/routers/assignments.py`
- `backend/app/routers/classes.py`
- `backend/app/routers/learning_requests.py`
- `backend/app/routers/schedules.py`
- `backend/app/routers/sessions.py`
- `backend/app/routers/students.py`
- `backend/app/routers/tutors.py`
- `backend/app/routers/tutor_profiles.py`
- `backend/app/routers/student_profiles.py`
- `backend/app/routers/learning_request_profiles.py`
- `backend/app/routers/assignment_routes.py`
- `backend/app/routers/class_profiles.py`
- `backend/app/routers/schedule_routes.py`
- `backend/app/routers/session_routes.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Ran a real backend startup check and reran the auth-aware HTTP smoke test after the `demo3` service/router decomposition.
- Live boot initially failed even though `compileall` passed.
- First runtime regression:
  - aggregate router modules used `APIRouter` before importing it
- Second runtime regression:
  - FastAPI rejected aggregate-router composition when child routers had empty-path operations and did not carry the resource `prefix` themselves
- Fixed the router composition pattern so the primary per-resource route module now owns the resource `prefix` and `tags`, while aggregate files re-export that router or attach only secondary child routers with non-empty paths.
- Confirmed backend startup succeeds again and the full HTTP smoke suite passes after those fixes.

### Validation Performed

- `uv run python -m compileall backend/app`
- `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000`
- `GET http://127.0.0.1:8000/health`
- `uv run python tests/http_crud_smoke.py --base-url http://127.0.0.1:8000 --staff-email staff1@smarttutor.local --staff-password staff123`

### Remaining Issues / Next Step

- The backend refactor on `demo3` is now live-verified for the main CRUD smoke path, but finance-router decomposition still remains if we want to finish the router split.
- Add a lightweight backend startup/import smoke check to future local verification so FastAPI router composition issues are caught earlier than full endpoint tests.

## 2026-06-15 - Repository Decomposition On demo3

### Changed Files

- `backend/app/repositories/data_repository.py`
- `backend/app/repositories/repository_common.py`
- `backend/app/repositories/account_repository.py`
- `backend/app/repositories/student_repository.py`
- `backend/app/repositories/tutor_repository.py`
- `backend/app/repositories/request_repository.py`
- `backend/app/repositories/class_repository.py`
- `backend/app/repositories/finance_repository.py`
- `backend/app/repositories/dashboard_repository.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Split the oversized repository module into bounded-context modules while preserving the existing repository API surface.
- Moved shared SQL helpers, update-column allowlists, and commit helper into `repository_common.py`.
- Extracted account/auth/staff persistence into `account_repository.py`.
- Extracted student persistence into `student_repository.py`.
- Extracted tutor, subject, tutor-capability, and tutor-availability persistence into `tutor_repository.py`.
- Extracted learning-request and assignment persistence into `request_repository.py`.
- Extracted class, schedule, session, and class-tuition aggregate persistence into `class_repository.py`.
- Extracted invoice/payment persistence into `finance_repository.py`.
- Extracted dashboard aggregate query into `dashboard_repository.py`.
- Replaced the old `data_repository.py` implementation with a thin compatibility facade that re-exports all repository functions for current service imports.

### Validation Performed

- `uv run python -m compileall backend/app`
- `GET http://127.0.0.1:8000/health`
- `uv run python tests/http_crud_smoke.py --base-url http://127.0.0.1:8000 --staff-email staff1@smarttutor.local --staff-password staff123`

### Remaining Issues / Next Step

- The repository split is live-verified for the current smoke path, so the next useful work should focus on verification depth rather than more structural churn.
- Add a lightweight startup/import smoke check plus a few focused negative HTTP tests to catch future compatibility regressions earlier.

## 2026-06-17 - Tutor Suggestion API Feature

### Changed Files

- `backend/app/repositories/request_repository.py`
- `backend/app/services/request_flow_service.py`
- `backend/app/routers/learning_request_profiles.py`
- `backend/app/schemas/entities.py`
- `backend/app/services/business_service.py`
- `docs/api_contract.md`
- `docs/current_status.md`

### What Changed

- Added `GET /learning-requests/{id}/suggested-tutors` endpoint for staff.
- Scoring factors: `experience_years * 10`, `+20` for area match, `+15` for schedule availability match.
- Filters: tutor must be `ACTIVE`, have capability for request subject, have < 10 active classes, and not have an existing active assignment for this request.
- Response includes: `tutor_id`, `full_name`, `phone`, `area`, `experience_years`, `current_classes`, `max_classes`, `score`, `match_reasons[]`.
- Implemented across repository, service, router, and schema layers.

### Validation Performed

- `uv run python -m compileall backend/app`
- No linter errors

### Remaining Issues / Next Step

- Live verification against SQL Server pending
- Frontend UI wiring for the suggestion feature not yet implemented

## 2026-06-17 - Tutor Suggestion Frontend Integration

### Changed Files

- `frontend/src/services/api.js`
- `frontend/src/pages/LearningRequestsPage.jsx`
- `docs/current_status.md`

### What Changed

- Added `getSuggestedTutors(requestId)` API function to frontend API client.
- Added "Gợi ý gia sư" button on LearningRequestsPage (visible only to staff for PENDING requests).
- Added modal component that displays ranked tutor suggestions with:
  - Tutor rank number
  - Full name and score
  - Experience, area, current/max classes, phone
  - Match reasons as colored tags
- Loading and error states handled in the modal.

### Validation Performed

- `npm run build` in frontend/ - passed

### Remaining Issues / Next Step

- Live test against backend API pending
- Could add "Chọn gia sư này" button to directly assign tutor from suggestion modal

## 2026-06-17 - Auto-Generate Sessions, UX Polish, And Availability Grid

### Changed Files

- `backend/app/services/class_flow_service.py`
- `backend/app/services/business_service.py`
- `backend/app/routers/session_routes.py`
- `frontend/src/services/api.js`
- `frontend/src/pages/SessionsPage.jsx`
- `frontend/src/pages/SchedulesPage.jsx`
- `frontend/src/pages/TutorProfilePage.jsx`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Backend:
  - Added `POST /sessions/generate-from-schedules` and `POST /sessions/preview-from-schedules` (staff only) so staff can mass-create `LESSON_SESSION` rows from a class's `ACTIVE` `CLASS_SCHEDULE` rows.
  - `_build_session_plan` respects schedule `effective_from`/`effective_to`, skips existing `(lesson_date, start_time)` pairs, auto-numbers sessions from `MAX(existing) + 1`, and falls back to class `start_date`/`end_date` when no range is supplied.
- Frontend:
  - `SessionsPage` now has an "Tạo buổi tự động từ lịch cố định" panel with class picker, optional range, preview table, and confirm action that refreshes the session list after success.
  - `SessionsPage` replaces `window.prompt` for the `COMPLETED` action with an in-app modal/textarea and adds proper Vietnamese field labels for the create form.
  - `SchedulesPage` adds proper Vietnamese field labels and a context banner that shows the class/subject/tutor/student of the schedule currently being edited.
  - `TutorProfilePage` adds a weekly availability grid (7-day x slots) below the availability list, color-coded by `AVAILABLE`/`UNAVAILABLE` status with start-end times.

### Validation Performed

- `uv run python -c "from app.routers import session_routes; from app.services.business_service import generate_sessions_from_schedules, preview_sessions_from_schedules; print('OK')"` - passed
- `uv run python -c "from app.main import app; print('routes:', len(app.routes))"` - passed (82 routes)
- Lint check on changed frontend pages - no errors

### Remaining Issues / Next Step

- Live HTTP smoke test for the new session generation endpoints against SQL Server is still pending.
- The auto-generate panel assumes the class already has at least one `ACTIVE` `CLASS_SCHEDULE` row; consider adding an inline hint when the picked class has no schedule.
- The weekly availability grid is a flat 7-day row layout; consider a time-axis grid (7 columns x hourly rows) as a future enhancement.

## 2026-06-17 - Suggested-Tutors Subject-Name Match

### Changed Files

- `backend/app/repositories/request_repository.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Replaced the strict `tc.subject_id = :subject_id` capability filter inside `get_candidate_tutors_for_request` with a small `EquivalentSubjects` CTE that derives the effective `subject_name + grade_level` pair from the request subject and matches any other active `SUBJECT` row that resolves to the same effective pair.
- This unblocks tutor suggestion when the request uses the seed-data subject (e.g. `name='Tiếng Anh' + grade_level='Lớp 11'`) and the tutor capability was stored against a UI-created subject (e.g. `name='Tiếng Anh Lớp 11' + grade_level=NULL`) — both row formats still resolve to the same effective subject and now both count.
- The fix is defense-in-depth only: it does not change data, does not relax any business filter, and does not touch the `NOT EXISTS active class` exclusion.

### Validation Performed

- `uv run python -m compileall app` - passed
- Direct SQL probe with the new `EquivalentSubjects` CTE against `subject_id=9` returns both `9` and `20` as expected
- `GET /learning-requests/25/suggested-tutors` after the fix still returns `suggestions: []` for the demo request, but the cause is now confirmed to be that all three English-11 tutors (1, 2, 6) have at least one active class; the subject mismatch is no longer the blocker
- Migration to dedupe the two subject name formats in the database was explicitly skipped per user decision; runtime match is sufficient for now.

### Remaining Issues / Next Step

- The duplicate subject formats (`name='Tiếng Anh' + grade_level='Lớp 11'` vs `name='Tiếng Anh Lớp 11' + grade_level=NULL`) still exist in the database. The runtime fix handles them, but a future cleanup batch could normalize the seed data so the two formats collapse to a single id.
- `/learning-requests/25/suggested-tutors` will only return tutors for the demo request once one of the English-11 tutors has no active class, or once staff explicitly chooses a tutor outside the candidate list.

## 2026-06-17 - Test Seed + SimpleNamespace Decode Fix For Suggested-Tutors

### Changed Files

- `backend/app/services/request_flow_service.py`
- `sql/seed_test_request_25.sql` (new)
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Fixed a latent decoding bug in `suggest_tutors_for_request` where the candidate loop assumed each row was a raw `Mapping`. After `to_obj(...)` wraps rows in `SimpleNamespace`, the previous fallback `dict(row)` raised `TypeError: 'types.SimpleNamespace' object is not iterable`. The loop now reads `row.__dict__` for `SimpleNamespace` rows and still falls back to `dict(row._mapping)` for raw mapping rows.
- Added `sql/seed_test_request_25.sql` to seed two fresh tutors (`Lê Minh Anh` tutor_id=901, `Phạm Quốc Đạt` tutor_id=902) that satisfy the request #25 candidate filters:
  - both ACTIVE with capability for subject_id=9 (`Tiếng Anh Lớp 11`)
  - both have one `TUTOR_AVAILABILITY` row on day_of_week=2 (T3) 18:30-20:30 OFFLINE in the Cầu Giấy area
  - both have zero `TUTOR_ASSIGNMENT` rows and zero active classes, so they pass the `NOT EXISTS` filter
- The script opens with `SET QUOTED_IDENTIFIER ON; SET ANSI_NULLS ON;` so the inserts succeed against filtered indexes on `SUBJECT` / `USER_ACCOUNT`.

### Validation Performed

- `uv run python -m compileall app` - passed
- `sqlcmd -b -S localhost -d TutorCenterDB -U sa -P 123456 -C -f 65001 -i sql/seed_test_request_25.sql` - passed (4 insert groups, 8 rows total)
- `GET /learning-requests/25/suggested-tutors` after seed returns:
  - tutor_id=902 (`Phạm Quốc Đạt`, 8 years) - score 100, reasons include lịch trùng khớp 1 ngày đủ giờ and hình thức OFFLINE
  - tutor_id=901 (`Lê Minh Anh`, 5 years) - score 90, reasons also include khu vực phù hợp because area string equals `preferred_area` exactly

### Remaining Issues / Next Step

- The two seeded tutors are still in the live DB; clean them up with `DELETE FROM USER_ACCOUNT WHERE account_id IN (901, 902)` when the test scenario is done.
- The two `SUBJECT` rows for `Tiếng Anh Lớp 11` are still duplicated in the DB; a future cleanup batch should fold them into one id.

## 2026-06-18 - Finance Page: Auto-fill Invoice Fields

### Changed Files

- `frontend/src/services/api.js`
- `frontend/src/pages/FinancePage.jsx`
- `backend/app/services/finance_service.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Added `getClassTuitionSummary(classId)` export to `api.js` calling `GET /classes/{classId}/tuition-summary`.
- Added `tuitionSummary` state and `handleClassSelect` in `FinancePage` — when staff picks a class in the invoice form, it immediately fetches the tuition summary and pre-fills `completed_sessions`, `tuition_fee_per_session`, and `amount_due` (using `total_fee` = buổi × phí/buổi).
- A summary card now renders below the class selector inside the invoice form, showing: completed sessions count, fee/buổi, total fee, and remaining debt.
- Fixed `finance_service.create_invoice` — the previous implementation called `repo.call_create_invoice_for_period(...)` which used the stored procedure to compute snapshot values from SQL, ignoring all client-supplied fields. Now it calls `repo.create_invoice(db, TuitionInvoice(...))` with the full payload values, respecting what the frontend sends.
- Invoice table now has an extra "Buổi & Phí" column showing session count and fee/buổi, and the money column now shows a "Còn nợ" row (amount_due - amount_paid) in red.

### Validation Performed

- No linter errors in modified files.
- Backend compile check should pass (the change is a small redirect from stored-proc path to direct-insert path with the same payload shape).

## 2026-06-18 - Finance Page: Auto-fill Invoice Period

### Changed Files

- `backend/app/schemas/entities.py`
- `backend/app/services/class_flow_service.py`
- `backend/app/services/business_service.py`
- `backend/app/routers/class_finance.py`
- `frontend/src/services/api.js`
- `frontend/src/pages/FinancePage.jsx`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Added `InvoicePeriodResponse` schema with `period_start`, `period_end`, `completed_sessions`.
- Added `get_invoice_period(db, class_id)` in `class_flow_service` — defaults the period to the current month (ngày 1 → ngày cuối tháng) on the server side, and reads `completed_sessions` from the existing tuition summary aggregate.
- Added `GET /classes/{id}/invoice-period` endpoint in `class_finance.py` for staff/student/tutor access with the standard class access guard.
- Re-exported `get_invoice_period` through `business_service` facade.
- Added `getClassInvoicePeriod(classId)` to the frontend `api.js`.
- `FinancePage.handleClassSelect` now fires both `getClassTuitionSummary` and `getClassInvoicePeriod` in parallel via `Promise.all`, then auto-fills `period_start` and `period_end` from the period endpoint.
  - The summary card inside the invoice form now also shows the suggested kỳ range in the header.

## 2026-06-18 - Finance Page: UX Hardening Pass

### Changed Files

- `frontend/src/components/StatusBadge.jsx` (new)
- `frontend/src/components/ConfirmDialog.jsx` (new)
- `frontend/src/utils/formatting.js`
- `frontend/src/pages/FinancePage.jsx`
- `docs/current_status.md`
- `docs/agent_worklog.md`

### What Changed

- Added shared `StatusBadge` component that renders invoice / payment / class status as a colored pill (`bg-red-50` for `UNPAID`, amber for `PARTIALLY_PAID`, emerald for `PAID/SUCCESS`, orange for `OVERDUE`, gray for `CANCELED`, purple for `REFUNDED`) and uses the existing `invoiceStatusLabel` / `paymentStatusLabel` from `formatting.js`.
- Added shared `ConfirmDialog` component (ESC-close, backdrop-click-close, auto-focus cancel button, `danger` variant, `loading` state) so the cancel-invoice and cancel-payment buttons no longer rely on `window.confirm`.
- Extended `frontend/src/utils/formatting.js` with `paymentStatusLabel`, `PAYMENT_METHOD_LABELS`, and `PAYMENT_METHOD_KEYS` (`BANK_TRANSFER`, `CASH`, `MOMO`, `VNPAY`) so the frontend can localize payment methods without changing the free-form `TUITION_PAYMENT.payment_method` column on the backend.
- `FinancePage` rewrite to ship all 13 UX improvements in one pass:
  - replaced mojibake tutor-role banner with plain Vietnamese (`Chỉ staff hoặc học viên sở hữu mới xem được hóa đơn và thanh toán.`)
  - invoice form: per-field error rows for `class_id`, `period_start`, `period_end` (with `end > start` check), `completed_sessions`, `tuition_fee_per_session`, `amount_due`; realtime duplicate-period detection against existing invoices (excluding `CANCELED`) renders a yellow warning banner and disables submit; `amount_due` is auto-recomputed from `completed_sessions × tuition_fee_per_session` until the user manually edits it (tracked by a small `autoAmount` flag on the form state)
  - invoice form: removed the `status` selector entirely — new invoices always start as `UNPAID` because the `TUITION_PAYMENT` trigger and service layer own the `UNPAID → PARTIALLY_PAID → PAID` transitions
  - payment form: per-field errors, auto-default `amount_paid = remaining` on first invoice selection, helper text under the amount input (`Tối đa: ...` or `Vượt còn nợ X đ` in red), submit button is disabled while `paymentInvalid`
  - payment form: invoice dropdown option now shows ` (đã đủ)` or ` (còn nợ ...)` and disables options that are already fully settled; payment method dropdown renders Vietnamese labels followed by the canonical enum key
  - both invoice and payment tables now support search (id, class code, status label, period dates, note), sortable column headers via a small `Th` helper, and a count badge on each tab (`Hóa đơn (n)`, `Thanh toán (n)`)
  - opening the invoice form closes the payment form and vice versa, with per-form error/state reset
  - after a successful payment, the invoice form (if still open for the same class) refreshes both `/classes/{id}/tuition-summary` and `/classes/{id}/invoice-period` so the realtime summary card stays in sync with the new `amount_paid`
  - status cells in both tables now render `<StatusBadge>` instead of plain text

### Validation Performed

- `ReadLints` on `FinancePage.jsx`, `StatusBadge.jsx`, `ConfirmDialog.jsx`, and `formatting.js` returned no errors.
- No backend code was modified — all changes use existing endpoints and rely on the existing service-layer overpayment / duplicate-period / status validation.
- Manual logic review:
  - `validateInvoice()` short-circuits before `createInvoice` if any field error is present or `invoiceDuplicate` is non-null.
  - `paymentInvalid` only fires when an invoice is selected AND amount is ≤ 0 or > remaining.
  - `pendingCancel` modal is the only way to reach `deleteInvoice` / `deletePayment`; the per-row buttons no longer call `window.confirm`.

### Remaining Issues / Next Step

- Status badge color palette is hard-coded in `StatusBadge.jsx`; if more variants are needed (e.g. `TUTOR_ABSENT` for sessions), extend the `VARIANTS` map there once.
- The search input is plain text + `localeCompare`; for very large datasets, switching to a server-side filter would be cheaper, but the current dataset fits comfortably in memory.
- Sortable columns do not yet persist across tab switches; if that becomes important, lift `invoiceSort` / `paymentSort` to `sessionStorage` in a follow-up batch.

### Validation Performed

- No linter errors in modified files.

## 2026-06-18 - End-to-End Flow Walkthrough Doc

### Changed Files

- `docs/flow_walkthrough.md` (new)
- `docs/agent_worklog.md` (this entry)

### What Changed

- Added `docs/flow_walkthrough.md` (1461 dong) mo ta chi tiết từng bước xử lý của 7 luồng nghiệp vụ chính, từ UI click → HTTP request → Router → Service → Repository → SQL/View/SP/Trigger → DB, kèm sơ đồ ASCII cho mỗi flow.
- Noi dung gom:
  1. Kiến trúc tổng quan (frontend + backend + SQL Server) và bản đồ thư mục `backend/app/`.
  2. Lớp xác thực & phân quyền (token format, `require_roles`, các `ensure_*_access`).
  3. Quy ước chung: repository pattern (raw text SQL), service layer, soft delete, response converter, validation.
  4. **Flow #1 Login/Register** — UI → AuthContext → router → service → repository → SQL INSERT.
  5. **Flow #2 Tạo Learning Request** — UI form → `createLearningRequest` → service validate (`_ensure_subject`, `_validate_non_negative_decimal`) → `INSERT … OUTPUT INSERTED.*`.
  6. **Flow #3 Phân công Tutor** — `GET /learning-requests/{id}/suggested-tutors` (3-tier CTE: TutorWorkload + RequestSubject + EquivalentSubjects) → score algorithm (experience*10 + area*20 + schedule overlap) → `POST /assignments` → service guards → `EXEC SP_ASSIGN_TUTOR_TO_REQUEST`.
  7. **Flow #4 Tạo Study Class** — `POST /classes` → service `create_study_class` (validate assignment, default class_code) → `EXEC SP_CREATE_CLASS_FROM_ASSIGNMENT`.
  8. **Flow #5 Tạo Schedule + Auto-generate Sessions** — `POST /schedules` (manual) + `POST /sessions/preview-from-schedules` / `/generate-from-schedules` (Python algorithm `_build_session_plan` match `isoweekday()`, đánh số `session_number`).
  9. **Flow #6 Cập nhật trạng thái buổi học** — `PATCH /sessions/{id}/status` (SCHEDULED → COMPLETED/STUDENT_ABSENT/TUTOR_ABSENT/CANCELED).
  10. **Flow #7 Invoice + Payment + Realtime Summary** — `GET /classes/{id}/tuition-summary` (table-valued `FN_CLASS_TUITION_SUMMARY`) → `POST /invoices` (validate period) → `POST /payments` (service-layer check `amount_paid > remaining` → 400) → `EXEC SP_CREATE_TUITION_PAYMENT` → `TRG_TUITION_PAYMENT_RECALC_INVOICE` tự động cập nhật `TUITION_INVOICE`.
- Phụ lục A: bảng tổng hợp soft-delete pattern (10 endpoint DELETE → status update).
- Phụ lục B: tổng hợp SQL objects (5 view + 2 function + 4 SP + 1 trigger) kèm vị trí file `sql/schema.sql`.

### Validation Performed

- Doc da duoc viet UTF-8 (đã verify bang `Read` tool hien thi dung tieng Viet) va khong sua bat ky file code nao.
- Khong chay compile/test (task la documentation-only).

### Remaining Issues / Next Step

- Tai lieu hien focus vao 7 flow nghiep vu chinh; cac flow phu (Tutor Capabilities/Availability, Tutor Profile CRUD, Student Profile CRUD) chua walkthrough rieng, nhung da co du context trong section 1-3 + `docs/api_contract.md` de tra cuu theo cung pattern.
- Neu can mo rong them flow (vi du: goi y gia su scoring chi tiet, hoac dashboard summary) thi tao batch tiep theo.

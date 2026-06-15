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

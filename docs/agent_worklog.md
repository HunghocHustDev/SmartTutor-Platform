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

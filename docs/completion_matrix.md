# SmartTutor Platform - Completion Matrix

Last updated: 2026-06-14

This matrix is based on:

- auth-aware real HTTP smoke test via `uv run python tests/http_crud_smoke.py --base-url http://127.0.0.1:8000 --staff-email staff1@smarttutor.local --staff-password staff123`
- direct code audit of `backend/app/*` and `frontend/src/*`
- backend compile check with `uv run python -m compileall backend/app`
- frontend build check with `npm run build`
- SQL Server-backed local backend runtime on 2026-06-14

## Backend CRUD Coverage

| Entity | Create | Read List | Read Detail | Update | Delete/Cancel/Deactivate | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `STUDENT` | `POST /students` | `GET /students` | `GET /students/{id}` | `PUT /students/{id}` | `DELETE /students/{id}` | PASS | HTTP-tested. Delete is soft delete to `INACTIVE`. |
| `TUTOR` | `POST /tutors` | `GET /tutors` | `GET /tutors/{id}` | `PUT /tutors/{id}` | `DELETE /tutors/{id}` | PASS | HTTP-tested. Delete is soft delete to `INACTIVE`. |
| `SUBJECT` | `POST /subjects` | `GET /subjects` | `GET /subjects/{id}` | `PUT /subjects/{id}` | `DELETE /subjects/{id}` | PASS | HTTP-tested. Delete is soft delete to `INACTIVE`. |
| `TUTOR_CAPABILITY` | `POST /tutors/{id}/capabilities` | `GET /tutors/{id}/capabilities` | N/A | N/A | `DELETE /tutors/{id}/capabilities/{capability_id}` | PARTIAL | HTTP-tested create/list/delete pass. No separate detail or update endpoint exists. |
| `TUTOR_AVAILABILITY` | `POST /tutors/{id}/availability` | `GET /tutors/{id}/availability` | N/A | `PUT /tutors/{id}/availability/{availability_id}` | `DELETE /tutors/{id}/availability/{availability_id}` | PARTIAL | HTTP-tested tutor-scoped CRUD pass. No separate detail endpoint exists. |
| `LEARNING_REQUEST` | `POST /learning-requests` | `GET /learning-requests` | `GET /learning-requests/{id}` | `PUT /learning-requests/{id}` | `DELETE /learning-requests/{id}` | PASS | HTTP-tested. Delete is soft cancel to `CANCELED`. |
| `TUTOR_ASSIGNMENT` | `POST /assignments` | `GET /assignments` | `GET /assignments/{id}` | `PUT /assignments/{id}` | `PATCH /assignments/{id}/cancel`, `DELETE /assignments/{id}` | PASS | HTTP-tested. Cancel path verified on `PATCH`; `DELETE` remains compatibility route. |
| `STUDY_CLASS` | `POST /classes` | `GET /classes` | `GET /classes/{id}` | `PUT /classes/{id}` | `DELETE /classes/{id}` | PASS | HTTP-tested. Creation is `assignment_id`-based only. |
| `CLASS_SCHEDULE` | `POST /schedules` | `GET /schedules` | `GET /schedules/{id}` | `PUT /schedules/{id}` | `DELETE /schedules/{id}` | PASS | HTTP-tested. Delete is soft deactivate to `INACTIVE`. |
| `LESSON_SESSION` | `POST /sessions` | `GET /sessions` | `GET /sessions/{id}` | `PUT /sessions/{id}`, `PATCH /sessions/{id}/status` | `DELETE /sessions/{id}` | PASS | HTTP-tested. `PATCH` to `COMPLETED` verified. Delete is soft cancel to `CANCELED`. |
| `TUITION_INVOICE` | `POST /invoices` | `GET /invoices` | `GET /invoices/{id}` | `PUT /invoices/{id}` | `DELETE /invoices/{id}` | PASS | HTTP-tested. Delete is soft cancel to `CANCELED`; duplicate period snapshot still returns `409`. |
| `TUITION_PAYMENT` | `POST /payments` | `GET /payments` | `GET /payments/{id}` | `PUT /payments/{id}` | `DELETE /payments/{id}` | PASS | HTTP-tested for invoice-based payment. Smoke script now also covers class-id payment auto-invoice branch; pending live rerun. Delete is soft cancel to `CANCELED`; overpayment still returns clean `400`. |

## Backend Business Flow Coverage

| Flow Step | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Auth register + login | PASS | HTTP smoke test registered a fresh student, logged in that student, and logged in demo staff successfully | Real `/auth/register` and `/auth/login` both pass on local SQL Server-backed backend. |
| Create learning request | PASS | HTTP smoke test created request `15` | Uses real DB and normalized subject/request fields. |
| Assign tutor | PASS | HTTP smoke test created assignment `7` | Validates pending request and tutor capability. |
| Create class from `assignment_id` | PASS | HTTP smoke test created class `6` | `POST /classes` is assignment-based only. |
| Create schedule | PASS | HTTP smoke test created schedule `2` | Real API flow passed. Schedule validation still exists for bad windows. |
| Create session | PASS | HTTP smoke test created lesson session `4` | Uses `lesson_date` canonical field with alias support. |
| Mark session `COMPLETED` | PASS | HTTP smoke test patched session `4` to `COMPLETED` | `PATCH /sessions/{id}/status` verified. |
| Create invoice | PASS | HTTP smoke test created invoice `6` | Real API flow passed. |
| Create payment | PASS | HTTP smoke test created payment `4` | Uses SQL Server trigger-safe insert behavior. |
| Reject overpayment with `400` | PASS | Earlier payment smoke test returned `400 Payment amount exceeds invoice remaining amount` | Enforced in service logic before insert/update. |
| Create payment by `class_id` and auto-create invoice | PARTIAL | Smoke script now includes this path, compile passes | Needs live rerun against SQL Server to verify trigger-updated invoice status in response. |
| Class list returns student/tutor/subject | PASS | HTTP smoke test verified created class payload contained all three display fields | Data resolved through normalized joins, not direct class FK columns. |

## Frontend Screen Coverage

| Screen | Uses Real API As Primary Source | Still Uses Mock As Primary Source | Create Form Works | Update/Status Action Works | Known Blockers |
| --- | --- | --- | --- | --- | --- |
| Login/Register | YES | NO | YES | N/A | Fake login path in header/auth context removed; still no protected token-based route guard beyond local auth state. |
| Dashboard | YES | NO | N/A | N/A | Only summary card flow is wired. |
| Students | YES | NO | YES | YES | No dedicated detail drilldown yet; current verification is code audit plus successful frontend build. |
| Tutors | YES | NO | YES | YES | No dedicated capability/availability management on the main list yet; current verification is code audit plus successful frontend build. |
| Subjects | YES | NO | YES | YES | First-class page exists; still needs live HTTP-backed UI verification. |
| Learning Requests | YES | NO | YES | YES | Staff edit action now opens the real form; still no route-level guard beyond local auth state. |
| Assignments | YES | NO | YES | PARTIAL | Create and cancel are wired; no reassignment/update form yet. |
| Classes | YES | NO | YES | YES | Detail view is still list-centric rather than a dedicated page/modal. |
| Schedules | YES | NO | YES | YES | First-class page exists; still needs live HTTP-backed UI verification. |
| Sessions | YES | NO | YES | PARTIAL | Create/cancel/quick status updates are wired; no full edit form for existing sessions yet. |
| Invoices | YES | NO | YES | PARTIAL | Managed through `FinancePage`; create/cancel are wired, but no invoice edit form yet. |
| Payments | YES | NO | YES | PARTIAL | Managed through `FinancePage`; create/cancel are wired, but no payment edit form yet. |

## SQL / Report Query Coverage

| Item | Status | Notes |
| --- | --- | --- |
| `sql/query_examples.sql` exists | PASS | Added in this batch. |
| Dashboard summary query | PASS | Included as Query 1. |
| Class list/report query | PASS | Included as Query 2 using `VW_STUDY_CLASS_DETAIL`. |
| Tutor workload query | PASS | Included as Query 3. |
| Realtime tuition summary query | PASS | Included as Query 4. |
| Invoice/payment report query | PASS | Included as Query 5. |
| Revenue by month query | PASS | Included as Query 6. |

## Exact Gaps Remaining

| Area | Status | Exact Gap |
| --- | --- | --- |
| Backend canonical CRUD parity | PARTIAL | `TUTOR_CAPABILITY` and `TUTOR_AVAILABILITY` do not have standalone detail endpoints; they are tutor-scoped only. |
| Frontend screen coverage verification | PARTIAL | The first-class pages now exist, but the newer subjects/assignments/schedules/sessions/finance flows still need live end-to-end UI verification against the running backend. |
| Frontend detail/update parity | PARTIAL | Assignment reassignment, session full-edit, and invoice/payment update flows are still not exposed even though several adjacent create/cancel actions are wired. |
| Backend input validation parity | PARTIAL | Service-layer validation now covers common status, date/time, and numeric constraint cases before SQL Server, and shared updates now support explicit nullable-field clearing with consistent `updated_at` touches. Remaining work: negative HTTP coverage and centralized DB error translation. |

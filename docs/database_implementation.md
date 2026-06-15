# Database Implementation

Last updated: 2026-06-15

## Architecture Summary

The backend uses SQLAlchemy `Session` for connection and transaction management, but the application CRUD layer now uses parameterized raw SQL in `backend/app/repositories/data_repository.py`. The SQL Server schema source of truth remains `sql/schema.sql`.

The normalized business path is unchanged:

```text
LEARNING_REQUEST
-> TUTOR_ASSIGNMENT
-> STUDY_CLASS
-> CLASS_SCHEDULE / LESSON_SESSION / TUITION_INVOICE / TUITION_PAYMENT
```

`STUDY_CLASS` still does not store `student_id`, `tutor_id`, or `subject_id` directly. Class/student/tutor/subject display fields are resolved through normalized joins or display views.

## Raw SQL CRUD Coverage

| Area | Technique | Main File / Object | Endpoint Group |
| --- | --- | --- | --- |
| Auth account/profile lookup | Raw SQL | `backend/app/repositories/data_repository.py` | `/auth/*` |
| Student CRUD | Raw SQL | `backend/app/repositories/data_repository.py` | `/students` |
| Tutor CRUD / capability / availability | Raw SQL | `backend/app/repositories/data_repository.py` | `/tutors*` |
| Subject CRUD | Raw SQL | `backend/app/repositories/data_repository.py` | `/subjects` |
| Learning request CRUD / detail | Raw SQL + view | `backend/app/repositories/data_repository.py`, `VW_LEARNING_REQUEST_DETAIL` | `/learning-requests` |
| Assignment CRUD | Raw SQL | `backend/app/repositories/data_repository.py` | `/assignments` |
| Class CRUD + realtime tuition summary | Raw SQL + view + function | `backend/app/repositories/data_repository.py`, `VW_STUDY_CLASS_DETAIL`, `FN_CLASS_TUITION_SUMMARY` | `/classes*` |
| Schedule CRUD | Raw SQL | `backend/app/repositories/data_repository.py` | `/schedules` |
| Session CRUD / detail | Raw SQL + view | `backend/app/repositories/data_repository.py`, `VW_LESSON_SESSION_DETAIL` | `/sessions` |
| Invoice CRUD / detail | Raw SQL + view | `backend/app/repositories/data_repository.py`, `VW_INVOICE_DETAIL` | `/invoices` |
| Payment CRUD / detail | Raw SQL + view + procedure + function + trigger | `backend/app/repositories/data_repository.py`, `VW_PAYMENT_DETAIL`, `SP_CREATE_TUITION_PAYMENT`, `FN_INVOICE_REMAINING_AMOUNT`, `TRG_TUITION_PAYMENT_RECALC_INVOICE` | `/payments` |
| Dashboard summary | Raw SQL aggregate | `backend/app/repositories/data_repository.py` | `/dashboard/summary` |

## SQL Server Objects

### Views

| View | Purpose | Used By |
| --- | --- | --- |
| `VW_STUDY_CLASS_DETAIL` | Flatten normalized class display data | `/classes`, class access checks, class response mapping |
| `VW_LEARNING_REQUEST_DETAIL` | Flatten learning request read model with one assignment context per request | `/learning-requests` list/detail |
| `VW_LESSON_SESSION_DETAIL` | Flatten lesson session read model with normalized class/student/tutor/subject metadata | `/sessions` list/detail |
| `VW_INVOICE_DETAIL` | Flatten invoice display data with class/student/tutor/subject metadata | invoice reads and reporting |
| `VW_PAYMENT_DETAIL` | Flatten payment display data with invoice/class/student/subject/staff metadata | `/payments` list/detail |

### Trigger

| Object | Purpose | Notes |
| --- | --- | --- |
| `TRG_TUITION_PAYMENT_RECALC_INVOICE` | Recalculate `TUITION_INVOICE.amount_paid` and invoice `status` after payment insert/update/delete | Counts only payments with status `SUCCESS` |

### Function

| Object | Purpose | Notes |
| --- | --- | --- |
| `FN_INVOICE_REMAINING_AMOUNT` | Return `max(amount_due - amount_paid, 0)` for an invoice | Used by payment creation procedure |
| `FN_CLASS_TUITION_SUMMARY` | Return realtime per-class tuition summary totals plus invoice counters | Used by `/classes/{id}/tuition-summary` |

### Procedure

| Object | Purpose | Notes |
| --- | --- | --- |
| `SP_CREATE_TUITION_PAYMENT` | Create payment from `invoice_id` or `class_id`, optionally auto-create a period invoice snapshot, validate canceled invoice and remaining amount, insert payment, rely on trigger for invoice recalc | Used by `POST /payments` |
| `SP_ASSIGN_TUTOR_TO_REQUEST` | Validate request/tutor/capability inside one transaction, insert assignment, update request status to `ASSIGNED`, and return the created assignment row | Used by `POST /assignments` |
| `SP_CREATE_CLASS_FROM_ASSIGNMENT` | Validate assignment state and one-assignment-one-class rule inside one transaction, insert `STUDY_CLASS`, and return the created class row | Used by `POST /classes` |
| `SP_CREATE_INVOICE_FOR_PERIOD` | Validate class/period, reject duplicate snapshots, compute invoice snapshot from completed sessions in the period, insert `TUITION_INVOICE`, and return the created invoice row | Used by `POST /invoices` |

## Verified Inventory Notes

The current custom DB object set now covers finance plus the main read-model foundation for requests, sessions, and classes:

- request/session/class read path:
  - `VW_LEARNING_REQUEST_DETAIL`
  - `VW_LESSON_SESSION_DETAIL`
  - `VW_STUDY_CLASS_DETAIL`
  - `FN_CLASS_TUITION_SUMMARY`
- finance write path:
  - `SP_ASSIGN_TUTOR_TO_REQUEST`
  - `SP_CREATE_TUITION_PAYMENT`
  - `FN_INVOICE_REMAINING_AMOUNT`
  - `TRG_TUITION_PAYMENT_RECALC_INVOICE`
- finance read path:
  - `VW_INVOICE_DETAIL`
  - `VW_PAYMENT_DETAIL`

The next DB-object batch should therefore focus on:

- assignment/class/invoice business command procedures

The assignment procedure is now implemented in code/schema, so the next procedure work should focus on:

- `SP_CREATE_INVOICE_FOR_PERIOD`

The planned command procedures are now implemented in code/schema for:

- `SP_ASSIGN_TUTOR_TO_REQUEST`
- `SP_CREATE_CLASS_FROM_ASSIGNMENT`
- `SP_CREATE_INVOICE_FOR_PERIOD`

See `docs/db_object_migration_plan.md` for the implementation plan.

## Payment Flow

`POST /payments` now works like this:

1. Service validates user-facing constraints first.
2. If the request uses `invoice_id`, service verifies invoice ownership/status and remaining amount.
3. If the request uses `class_id`, service determines the target period and validates student ownership / expected remaining amount.
4. Repository calls `SP_CREATE_TUITION_PAYMENT`.
5. Procedure resolves or creates the invoice snapshot.
6. Procedure validates remaining amount with `FN_INVOICE_REMAINING_AMOUNT`.
7. Procedure inserts the payment.
8. `TRG_TUITION_PAYMENT_RECALC_INVOICE` updates invoice `amount_paid` and `status`.
9. Repository reads the created payment from `VW_PAYMENT_DETAIL`.

This keeps user-facing validation in service logic while still demonstrating database-owned payment synchronization.

## Evidence Commands

### Code / Search

```powershell
uv run python -m compileall backend/app backend/tests/http_crud_smoke.py
rg -n "db\.(query|add|delete|refresh|flush)" backend/app
rg -n "joinedload|\.options\(" backend/app
```

### SQL Server Reset And Seed

```powershell
sqlcmd -b -S localhost -d master -U sa -P 123456 -C -f 65001 -i sql/schema.sql
powershell -ExecutionPolicy Bypass -File .\sql\reset_demo_utf8.ps1 -Seed sample
```

### Live HTTP Verification

```powershell
cd backend
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
uv run python tests/http_crud_smoke.py --base-url http://127.0.0.1:8000 --staff-email staff1@smarttutor.local --staff-password staff123
```

## Current Validation State

- Schema reset succeeded against local SQL Server on 2026-06-15.
- Sample seed succeeded after schema reset on 2026-06-15.
- Auth-aware HTTP smoke test passed after the raw SQL finance migration on 2026-06-15.
- Phase 1 DB object migration changes were compile-verified on 2026-06-15, but direct SQL Server object checks and live HTTP reruns have not been repeated yet for this specific batch.
- Phase 2 assignment-procedure integration was compile-verified on 2026-06-15, but direct `EXEC` checks and live HTTP reruns have not been repeated yet for this specific batch.
- Phase 3 class-procedure integration was compile-verified on 2026-06-15, but direct `EXEC` checks and live HTTP reruns have not been repeated yet for this specific batch.
- Phase 4 invoice-procedure integration was compile-verified on 2026-06-15, but direct `EXEC` checks and live HTTP reruns have not been repeated yet for this specific batch.
- Phase 1-4 DB object migration live verification now completed on 2026-06-15:
  - `sql/schema.sql` reran successfully
  - `sql/sample_data.sql` reseeded successfully
  - direct `EXEC` verification passed for `SP_ASSIGN_TUTOR_TO_REQUEST`, `SP_CREATE_CLASS_FROM_ASSIGNMENT`, and `SP_CREATE_INVOICE_FOR_PERIOD`
  - auth-aware HTTP smoke test passed after the procedure-backed assignment/class/invoice migrations
- Procedure transaction handling is now hardened for live error paths:
  - `SP_ASSIGN_TUTOR_TO_REQUEST`
  - `SP_CREATE_CLASS_FROM_ASSIGNMENT`
  - `SP_CREATE_INVOICE_FOR_PERIOD`
  - `SP_CREATE_TUITION_PAYMENT`
  now use `TRY/CATCH` plus explicit `ROLLBACK` before rethrowing, preventing doomed-session behavior after invalid procedure calls in the same SQL session.
- `backend/app/repositories/data_repository.py` and `backend/app/services/business_service.py` now return no matches for `db.query`, `db.add`, `db.delete`, `db.refresh`, `db.flush`, `joinedload`, or `.options(`.
- Planned next DB-object expansion is documented in `docs/db_object_migration_plan.md`.

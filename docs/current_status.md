# Current Status

## Last Updated

- 2026-06-13

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
uv run python tests/http_crud_smoke.py --base-url http://127.0.0.1:8021
```

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

## Exact Frontend Gaps

- No dedicated page exists yet for:
  - subjects
  - assignments
  - schedules
  - sessions
  - invoices
  - payments
- Students page create works, but update UI is not wired.
- Tutors page create works, but update UI is not wired.
- Learning requests page create works, cancel works, but edit/update UI is not wired.
- Classes page list and cancel work, but create/update/detail UI is not wired.

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

- build first-class frontend screens for subjects, assignments, schedules, sessions, invoices, and payments
- wire update flows for students, tutors, learning requests, and classes
- keep `docs/completion_matrix.md` as the exact PASS/PARTIAL/FAIL source for future batches

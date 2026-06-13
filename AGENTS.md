# SmartTutor Platform - Agent Instructions

## Project Summary

SmartTutor Platform is a tutor center management system for a SQL Server-backed FastAPI and React application.

The backend must follow the `FINAL CLEAN` schema in `sql/schema.sql`.

## Business Model

This is not a tutor marketplace.

- Students do not directly choose tutors.
- Tutors do not apply for classes.
- Center staff coordinates the workflow.

Main flow:

```text
Student creates a learning request
-> Staff reviews the request
-> Staff assigns a tutor
-> Staff creates a study class
-> Staff creates class schedules
-> Tutor/staff updates lesson sessions
-> Staff manages tuition invoices and payments
```

## Normalized Database Rule

`STUDY_CLASS` does not store `student_id`, `tutor_id`, or `subject_id` directly.

To resolve student/tutor/subject for a class, join through:

```text
STUDY_CLASS
-> TUTOR_ASSIGNMENT
-> LEARNING_REQUEST
-> STUDENT / SUBJECT

TUTOR_ASSIGNMENT
-> TUTOR
```

Prefer `VW_STUDY_CLASS_DETAIL` for class list/detail responses.

## Schema Rules

- `STAFF`, `STUDENT`, and `TUTOR` use `contact_email`, not `email`.
- `day_of_week` is `TINYINT` in the range `1..7`.
- `TUTOR_ASSIGNMENT.status` supports only `ASSIGNED` and `CANCELED`.
- `STUDY_CLASS.status` supports `ACTIVE`, `PAUSED`, `COMPLETED`, `CANCELED`.
- `LESSON_SESSION.status` supports `SCHEDULED`, `COMPLETED`, `STUDENT_ABSENT`, `TUTOR_ABSENT`, `CANCELED`.
- `TUITION_INVOICE.status` supports `UNPAID`, `PARTIALLY_PAID`, `PAID`, `OVERDUE`, `CANCELED`.
- `TUITION_PAYMENT.status` supports `SUCCESS`, `CANCELED`, `REFUNDED`.
- `TUITION_PAYMENT` trigger updates `TUITION_INVOICE.amount_paid` and `TUITION_INVOICE.status`.
- Only `SUCCESS` payments count as paid money.
- `TUITION_INVOICE` is a snapshot by period.
- `/classes/{id}/tuition-summary` should be realtime.

## Backend Rules

- FastAPI, SQLAlchemy, pyodbc, SQL Server, Pydantic are the expected stack.
- Prefer `uv` for Python environment and dependency management in this project.
- Follow the current schema; do not silently reintroduce old fields.
- Before inserting a payment, service logic should check remaining amount and return a clean `400` if the payment exceeds the remaining balance.
- Do not rely only on database constraint failures for user-facing validation.
- Use soft delete for `student`, `tutor`, and `subject` by setting status to `INACTIVE`.

## Frontend Rules

- The React frontend already exists.
- Connect screens gradually to the real API.
- Do not remove mock data until the corresponding screen works against backend data.
- Preserve compatibility mappings where possible, especially around class, request, and payment responses.

## Payment / Invoice Rule

- Payment validation should happen in service logic before insert.
- Invoice totals are snapshot values for a period.
- Realtime tuition summary may differ from invoice snapshot until a new invoice is generated.

## Work Discipline

For each coding batch:

1. Read `AGENTS.md`.
2. Read `docs/current_status.md`.
3. Read relevant docs in `docs/`.
4. Modify only files needed for the current task.
5. Run compile/test commands when possible.
6. Update `docs/current_status.md`.
7. Append `docs/agent_worklog.md`.
8. Never do unrelated refactors.
9. Never silently change schema rules.
10. Prefer `uv` for Python env, dependency install, and run commands.
11. Keep doc updates aligned with the current repository state.

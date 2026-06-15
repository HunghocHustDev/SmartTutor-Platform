# Database Rules

## Source Of Truth

- `sql/schema.sql` is the source of truth.
- Backend code must follow the `FINAL CLEAN` schema.
- Do not silently reintroduce the old schema shape.

## Normalized Class Rule

`STUDY_CLASS` does not store `student_id`, `tutor_id`, or `subject_id` directly.

Use these joins to resolve class participants:

```text
STUDY_CLASS
-> TUTOR_ASSIGNMENT
-> LEARNING_REQUEST
-> STUDENT / SUBJECT

TUTOR_ASSIGNMENT
-> TUTOR
```

Prefer `VW_STUDY_CLASS_DETAIL` for class list and class detail responses.

## day_of_week Convention

`day_of_week` is `TINYINT` and uses:

- `1 = Monday`
- `2 = Tuesday`
- `3 = Wednesday`
- `4 = Thursday`
- `5 = Friday`
- `6 = Saturday`
- `7 = Sunday`

## Status Rules

### TUTOR_ASSIGNMENT

- `ASSIGNED`
- `CANCELED`

### STUDY_CLASS

- `ACTIVE`
- `PAUSED`
- `COMPLETED`
- `CANCELED`

### LESSON_SESSION

- `SCHEDULED`
- `COMPLETED`
- `STUDENT_ABSENT`
- `TUTOR_ABSENT`
- `CANCELED`

### TUITION_INVOICE

- `UNPAID`
- `PARTIALLY_PAID`
- `PAID`
- `OVERDUE`
- `CANCELED`

### TUITION_PAYMENT

- `SUCCESS`
- `CANCELED`
- `REFUNDED`

## Invoice And Payment Behavior

- `TUITION_INVOICE` is a snapshot by period.
- `completed_sessions`, `tuition_fee_per_session`, and `amount_due` are snapshot values.
- `/classes/{id}/tuition-summary` should be a realtime summary.
- `TUITION_PAYMENT` trigger updates `TUITION_INVOICE.amount_paid` and `TUITION_INVOICE.status`.
- Only `SUCCESS` payments count as paid money.

## Soft Delete Rule

Use soft delete for records with historical FK impact:

- `DELETE student` -> set `status = INACTIVE`
- `DELETE tutor` -> set `status = INACTIVE`
- `DELETE subject` -> set `status = INACTIVE`

Do not hard delete records that may already be referenced by requests, assignments, classes, invoices, or payments.

## Forbidden Schema Mistakes

- Do not add `student_id`, `tutor_id`, or `subject_id` to `STUDY_CLASS`.
- Do not use `email` in profile tables when the schema uses `contact_email`.
- Do not use `target`, `area`, or `teaching_mode` in the database layer when the schema stores `learning_goal`, `preferred_area`, and `preferred_mode`.
- Do not use `FINISHED` if the schema uses `COMPLETED`.
- Do not use `ACCEPTED` or `REJECTED` for assignment status if the schema only supports `ASSIGNED` and `CANCELED`.


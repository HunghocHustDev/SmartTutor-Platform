# SQL Raw Repository Migration Plan

Last updated: 2026-06-14

Branch baseline: `demo2` created from `demo1` commit `d3cd2e6`.

## 1. Goal

This project is for a Database course. The backend currently uses SQLAlchemy ORM heavily, which works technically but hides many SQL operations behind ORM calls. The goal of this migration is to make database operations explicit and easy to demonstrate:

- Use raw parameterized SQL for CRUD in `backend/app/repositories/data_repository.py`.
- Use SQL views for complex read models.
- Keep and demonstrate triggers for automatic database-side synchronization.
- Add stored procedures for multi-step business workflows where the database should own transaction-sensitive logic.
- Add scalar/table functions only for reusable calculations.
- Add docs proving which SQL object/query supports each business flow.

Important: continue using SQLAlchemy `Session` for connection and transaction management. Do not switch to manually opened `pyodbc` connections in many places.

Target style:

```python
db.execute(text("""
    SELECT ...
    FROM STUDENT
    WHERE student_id = :student_id
"""), {"student_id": student_id})
```

Avoid target style:

```python
db.query(Student).filter(Student.student_id == student_id).first()
db.add(student)
db.delete(model)
```

## 2. Current State Summary

The current runtime database access is mostly in:

- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `backend/app/core/auth.py`

Current repository uses SQLAlchemy ORM:

- `db.query(...)`
- `db.add(...)`
- `db.delete(...)`
- `joinedload(...)`
- ORM relationship traversal such as `payment.invoice.study_class.assignment.learning_request`

Current service also mutates ORM objects directly:

```python
student.status = "INACTIVE"
request.status = "ASSIGNED"
session.content_note = payload.content_note
repo.commit(db)
```

After returning raw SQL result objects, these assignments will not update the database automatically. This is the key migration risk.

Migration rule:

```text
After this migration, every database write must be an explicit repository SQL INSERT/UPDATE/DELETE or stored procedure call.
Service code must not rely on mutating returned objects and committing.
```

Existing database objects in `sql/schema.sql`:

- Trigger: `TRG_TUITION_PAYMENT_RECALC_INVOICE`
- View: `VW_STUDY_CLASS_DETAIL`

Currently missing but recommended:

- `VW_PAYMENT_DETAIL`
- `VW_INVOICE_DETAIL`
- optional `VW_LEARNING_REQUEST_DETAIL`
- `FN_INVOICE_REMAINING_AMOUNT`
- optional `FN_CLASS_COMPLETED_SESSION_COUNT`
- `SP_CREATE_TUITION_PAYMENT`

## 3. Design Principles

1. Keep file name `backend/app/repositories/data_repository.py`.
2. Keep existing repository function names where practical.
3. Replace the inside of repository functions from ORM to raw SQL.
4. Return dot-access objects during migration to reduce service changes.
5. Do not create `data_repository_sql.py`.
6. Do not silently change the schema rules in `sql/schema.sql`.
7. Do not reintroduce old denormalized columns such as `STUDY_CLASS.student_id`, `STUDY_CLASS.tutor_id`, or `STUDY_CLASS.subject_id`.
8. Use parameterized SQL everywhere.
9. Whitelist update columns. Never let user input determine table or column names.
10. Prefer SQL Server database objects for meaningful DB-course value, not for every tiny CRUD path.

## 4. Recommended Repository Helpers

Add these helpers near the top of `data_repository.py`.

```python
from types import SimpleNamespace
from sqlalchemy import text


def to_obj(row):
    if row is None:
        return None
    return SimpleNamespace(**dict(row))


def to_list(rows):
    return [to_obj(row) for row in rows]


def fetch_one(db, sql: str, params: dict | None = None):
    row = db.execute(text(sql), params or {}).mappings().first()
    return to_obj(row)


def fetch_all(db, sql: str, params: dict | None = None):
    rows = db.execute(text(sql), params or {}).mappings().all()
    return to_list(rows)


def execute(db, sql: str, params: dict | None = None):
    return db.execute(text(sql), params or {})
```

Add a safe dynamic update helper:

```python
def update_by_id(db, table: str, id_column: str, id_value, data: dict, allowed_columns: set[str]):
    clean = {
        key: value
        for key, value in data.items()
        if key in allowed_columns and key != "updated_at"
    }
    if not clean:
        return

    assignments = ", ".join([f"{column} = :{column}" for column in clean])
    sql = f"""
        UPDATE {table}
        SET {assignments},
            updated_at = SYSUTCDATETIME()
        WHERE {id_column} = :id_value
    """
    execute(db, sql, {**clean, "id_value": id_value})
```

Safety note: `table`, `id_column`, and `allowed_columns` must be constants defined by developers, never request payload values.

Suggested allowed-column constants:

```python
STUDENT_UPDATE_COLUMNS = {"full_name", "phone", "contact_email", "area", "current_level", "grade_level", "status"}
TUTOR_UPDATE_COLUMNS = {"full_name", "phone", "contact_email", "area", "experience_years", "status"}
SUBJECT_UPDATE_COLUMNS = {"subject_name", "subject_group", "grade_level", "description", "status"}
...
```

## 5. Target Database Access Rules

End-state code search should satisfy:

```powershell
rg "db\.(query|add|delete|refresh|flush)" backend/app
```

Expected result: no runtime app usage, or only explicitly justified leftovers.

Allowed:

```python
db.execute(text(...), params)
db.commit()
db.rollback()
```

Potentially unnecessary after migration:

```python
db.flush()
db.refresh()
```

## 6. Business Flow Mapping

### 6.1 Auth / Register / Login

Current flow:

```text
POST /auth/register
-> service.register
-> create USER_ACCOUNT
-> create STUDENT or TUTOR profile
-> commit

POST /auth/login
-> service.authenticate
-> get USER_ACCOUNT by email
-> get profile by account_id
```

Migration target:

- Raw SQL repository for user/profile CRUD.
- Auth dependency should call repository raw SQL, not `db.query`.

Repository functions:

- `get_user_by_email`
- `get_user_by_username`
- `get_user_by_id`
- `create_user`
- `get_student_by_account_id`
- `get_tutor_by_account_id`
- `get_staff_by_account_id`
- `create_student`
- `create_tutor`

Example SQL:

```sql
SELECT account_id, email, username, password_hash, role, status, created_at, updated_at
FROM USER_ACCOUNT
WHERE email = :email;
```

```sql
INSERT INTO USER_ACCOUNT (
    email, username, password_hash, role, status
)
OUTPUT INSERTED.account_id
VALUES (
    :email, :username, :password_hash, :role, :status
);
```

Recommended DB objects:

- Raw SQL only.
- No view/procedure/function needed for simple auth.

Service changes:

- Replace direct `db.query(Student/Tutor/Staff).filter(account_id...)` in `business_service.authenticate`.
- Replace direct `db.query(...)` in `core/auth.py`.

### 6.2 Student CRUD

Endpoints:

- `GET /students`
- `POST /students`
- `GET /students/{id}`
- `PUT /students/{id}`
- `DELETE /students/{id}` soft-deactivates to `INACTIVE`

Migration target:

- Raw SQL CRUD in repository.
- `DELETE` should be SQL `UPDATE`, not hard delete.

Repository functions:

- `get_students`
- `get_student`
- `create_student`
- `update_student`
- `deactivate_student`

Example list SQL:

```sql
SELECT student_id, account_id, full_name, phone, contact_email, address, area,
       current_level, grade_level, status, created_at, updated_at
FROM STUDENT
WHERE (:status IS NULL OR status = :status)
  AND (:name IS NULL OR full_name LIKE :name)
  AND (:phone IS NULL OR phone LIKE :phone)
  AND (:email IS NULL OR contact_email LIKE :email)
  AND (:area IS NULL OR area LIKE :area)
ORDER BY student_id DESC;
```

Example update SQL:

```sql
UPDATE STUDENT
SET full_name = :full_name,
    phone = :phone,
    contact_email = :contact_email,
    area = :area,
    current_level = :current_level,
    grade_level = :grade_level,
    status = :status,
    updated_at = SYSUTCDATETIME()
WHERE student_id = :student_id;
```

Recommended DB objects:

- Raw SQL only.

Service changes:

- Replace `repo.apply_updates(student, data)` with `repo.update_student(db, student_id, data)`.
- Replace direct status assignment with `repo.deactivate_student(db, student_id)`.

### 6.3 Tutor / Capability / Availability

Endpoints:

- `GET /tutors`
- `POST /tutors`
- `GET /tutors/{id}`
- `PUT /tutors/{id}`
- `DELETE /tutors/{id}` soft-deactivates
- tutor capabilities and subjects
- tutor availability

Migration target:

- Raw SQL for `TUTOR`.
- Raw SQL for `TUTOR_CAPABILITY`.
- Raw SQL for `TUTOR_AVAILABILITY`.
- For tutor detail/list, attach `capabilities` manually from SQL rows because service currently expects `tutor.capabilities`.

Repository functions:

- `get_tutors`
- `get_tutor`
- `create_tutor`
- `update_tutor`
- `deactivate_tutor`
- `get_tutor_capabilities`
- `create_tutor_capability`
- `delete_tutor_capability`
- `get_tutor_availabilities`
- `get_tutor_availability`
- `create_tutor_availability`
- `update_tutor_availability`
- `delete_tutor_availability`

Tutor capability detail SQL:

```sql
SELECT
    tc.capability_id,
    tc.tutor_id,
    tc.subject_id,
    tc.teaching_level,
    tc.years_experience,
    tc.note,
    tc.created_at,
    tc.updated_at,
    s.subject_name,
    s.grade_level,
    s.subject_group,
    s.status AS subject_status
FROM TUTOR_CAPABILITY tc
JOIN SUBJECT s ON s.subject_id = tc.subject_id
WHERE tc.tutor_id = :tutor_id
ORDER BY s.subject_name, s.grade_level;
```

Recommended DB objects:

- Raw SQL is enough.
- Optional view: `VW_TUTOR_CAPABILITY_DETAIL` if reports need it.

Service changes:

- Replace subject rebuild flow in `update_tutor` with explicit delete/insert SQL calls.
- Replace capability direct mutation with `repo.update_tutor_capability(...)`.
- Replace `db.flush()` after deleting capabilities with raw SQL delete. No flush should be needed.

### 6.4 Subject CRUD

Endpoints:

- `GET /subjects`
- `POST /subjects`
- `GET /subjects/{id}`
- `PUT /subjects/{id}`
- `DELETE /subjects/{id}` soft-deactivates

Migration target:

- Raw SQL CRUD.
- Keep duplicate subject name + level validation in service before DB unique constraint.

Repository functions:

- `get_subjects`
- `get_subject`
- `get_subject_by_name_level`
- `create_subject`
- `update_subject`
- `deactivate_subject`

Recommended DB objects:

- Raw SQL only.

### 6.5 Learning Request

Endpoints:

- `GET /learning-requests`
- `POST /learning-requests`
- `GET /learning-requests/{id}`
- `PUT /learning-requests/{id}`
- `DELETE /learning-requests/{id}` soft-cancels to `CANCELED`

Migration target:

- Raw SQL CRUD.
- For response mapping, attach `student` and `subject` data because current mapper uses `request.student` and `request.subject`.

Recommended view:

```text
VW_LEARNING_REQUEST_DETAIL
```

Suggested view:

```sql
CREATE VIEW VW_LEARNING_REQUEST_DETAIL AS
SELECT
    lr.request_id,
    lr.student_id,
    st.full_name AS student_name,
    st.phone AS student_phone,
    st.contact_email AS student_email,
    lr.subject_id,
    su.subject_name,
    su.grade_level AS subject_grade_level,
    lr.requested_level,
    lr.learning_goal,
    lr.preferred_area,
    lr.preferred_mode,
    lr.preferred_schedule,
    lr.expected_fee,
    lr.status,
    lr.created_at,
    lr.updated_at
FROM LEARNING_REQUEST lr
JOIN STUDENT st ON st.student_id = lr.student_id
JOIN SUBJECT su ON su.subject_id = lr.subject_id;
```

Use view for:

- list learning requests
- detail learning request
- student learning request display

Writes still use raw SQL against `LEARNING_REQUEST`.

Service changes:

- Replace `request.subject_id = subject.subject_id` plus commit with `repo.update_learning_request(...)`.
- Replace cancel direct status mutation with `repo.cancel_learning_request(...)`.

### 6.6 Tutor Assignment

Endpoints:

- `GET /assignments`
- `POST /assignments`
- `GET /assignments/{id}`
- `PUT /assignments/{id}`
- `PATCH /assignments/{id}/cancel`
- `DELETE /assignments/{id}` compatibility cancel

Migration target:

- Raw SQL for assignment CRUD.
- Multi-table updates should be explicit SQL in repository or stored procedure.

Important current business rules:

- Request must be `PENDING` to create assignment.
- Tutor must be `ACTIVE`.
- Only one active assignment per request.
- Assignment `CANCELED` should return learning request to `PENDING`, unless blocked by class rules.

Option A: raw SQL repository transaction:

```sql
INSERT INTO TUTOR_ASSIGNMENT (...)
OUTPUT INSERTED.assignment_id
VALUES (...);

UPDATE LEARNING_REQUEST
SET status = 'ASSIGNED',
    updated_at = SYSUTCDATETIME()
WHERE request_id = :request_id;
```

Option B: stored procedure:

```text
SP_CREATE_TUTOR_ASSIGNMENT
SP_CANCEL_TUTOR_ASSIGNMENT
```

Recommendation:

- Use raw SQL repository for assignment first.
- Add stored procedure only if the project needs more DB-object count after finance.

Service changes:

- Replace `request.status = ...` and `assignment.status = ...` with repository SQL calls.
- Ensure repository returns fresh assignment row after writes.

### 6.7 Study Class

Endpoints:

- `GET /classes`
- `POST /classes`
- `GET /classes/{id}`
- `PUT /classes/{id}`
- `DELETE /classes/{id}` soft-cancels
- `GET /classes/{id}/tuition-summary`

Migration target:

- Writes: raw SQL against `STUDY_CLASS`.
- Reads: use `VW_STUDY_CLASS_DETAIL`.

Existing view:

```sql
VW_STUDY_CLASS_DETAIL
```

Use for:

- `repo.get_classes`
- `repo.get_class`

Because service currently expects nested relationships, there are two choices:

Option A: repository builds fake nested objects from view fields.

Example:

```text
study_class.assignment.learning_request.student.full_name
study_class.assignment.tutor.full_name
```

Option B: simplify `class_to_response` to read flattened view fields.

Recommendation:

- Prefer Option B for class read path.
- It is cleaner and demonstrates why view exists.
- Adjust `class_to_response` to support view-backed object fields:
  - `student_id`
  - `student_name`
  - `tutor_id`
  - `tutor_name`
  - `subject_id`
  - `subject_name`
  - `subject_grade_level`
  - `class_status`

Potential compatibility helper:

```python
def class_to_response(study_class):
    if hasattr(study_class, "class_status"):
        return view_class_to_response(study_class)
    return old_orm_class_to_response(study_class)
```

Remove old path once migration finishes.

Recommended new or enhanced view:

- Existing `VW_STUDY_CLASS_DETAIL` is enough for class list/detail.
- If schedule/session counts are needed, add fields or use separate aggregate query.

### 6.8 Class Schedule

Endpoints:

- `GET /schedules`
- `POST /schedules`
- `GET /schedules/{id}`
- `PUT /schedules/{id}`
- `DELETE /schedules/{id}` soft-deactivates

Migration target:

- Raw SQL CRUD.
- For list filters by `tutor_id` or `student_id`, use explicit joins:

```sql
SELECT cs.*
FROM CLASS_SCHEDULE cs
JOIN STUDY_CLASS sc ON sc.class_id = cs.class_id
JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
WHERE (:class_id IS NULL OR cs.class_id = :class_id)
  AND (:tutor_id IS NULL OR ta.tutor_id = :tutor_id)
  AND (:student_id IS NULL OR lr.student_id = :student_id)
ORDER BY cs.schedule_id DESC;
```

Recommended DB objects:

- Raw SQL only.

### 6.9 Lesson Session

Endpoints:

- `GET /sessions`
- `POST /sessions`
- `GET /sessions/{id}`
- `PUT /sessions/{id}`
- `PATCH /sessions/{id}/status`
- `DELETE /sessions/{id}` soft-cancels

Migration target:

- Raw SQL CRUD.
- SQL must preserve schedule/class FK rule.
- `PATCH /sessions/{id}/status` should be SQL update that can clear `content_note` when explicitly sent as null.

Recommended query:

```sql
SELECT ls.*
FROM LESSON_SESSION ls
JOIN STUDY_CLASS sc ON sc.class_id = ls.class_id
JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
WHERE (:class_id IS NULL OR ls.class_id = :class_id)
  AND (:tutor_id IS NULL OR ta.tutor_id = :tutor_id)
  AND (:student_id IS NULL OR lr.student_id = :student_id)
  AND (:status IS NULL OR ls.status = :status)
  AND (:lesson_date IS NULL OR ls.lesson_date = :lesson_date)
ORDER BY ls.lesson_date DESC, ls.session_id DESC;
```

Recommended DB objects:

- Raw SQL for CRUD.
- Function can be used later for completed session count by period.

### 6.10 Invoice

Endpoints:

- `GET /invoices`
- `POST /invoices`
- `GET /invoices/{id}`
- `PUT /invoices/{id}`
- `DELETE /invoices/{id}` soft-cancels

Migration target:

- Raw SQL CRUD for explicit invoice create/update/cancel.
- View for list/detail if frontend needs student/class/subject display.

Recommended view:

```text
VW_INVOICE_DETAIL
```

Suggested view:

```sql
CREATE VIEW VW_INVOICE_DETAIL AS
SELECT
    ti.invoice_id,
    ti.class_id,
    sc.class_code,
    ti.period_start,
    ti.period_end,
    ti.completed_sessions,
    ti.tuition_fee_per_session,
    ti.amount_due,
    ti.amount_paid,
    ti.status,
    ti.created_at,
    ti.updated_at,
    lr.student_id,
    st.full_name AS student_name,
    su.subject_id,
    su.subject_name,
    su.grade_level AS subject_grade_level,
    ta.tutor_id,
    tu.full_name AS tutor_name
FROM TUITION_INVOICE ti
JOIN STUDY_CLASS sc ON sc.class_id = ti.class_id
JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
JOIN STUDENT st ON st.student_id = lr.student_id
JOIN SUBJECT su ON su.subject_id = lr.subject_id
JOIN TUTOR tu ON tu.tutor_id = ta.tutor_id;
```

Recommended DB objects:

- `VW_INVOICE_DETAIL`
- Existing trigger handles amount/status sync after payment.

### 6.11 Payment

Endpoints:

- `GET /payments`
- `POST /payments`
- `GET /payments/{id}`
- `PUT /payments/{id}`
- `DELETE /payments/{id}` soft-cancels

Migration target:

- Read list/detail from `VW_PAYMENT_DETAIL`.
- Create payment via stored procedure `SP_CREATE_TUITION_PAYMENT` if possible.
- Update/cancel payment via raw SQL, relying on trigger to recalc invoice.

Recommended view:

```text
VW_PAYMENT_DETAIL
```

Suggested view:

```sql
CREATE VIEW VW_PAYMENT_DETAIL AS
SELECT
    tp.payment_id,
    tp.invoice_id,
    ti.class_id,
    sc.class_code,
    lr.student_id,
    st.full_name AS student_name,
    su.subject_id,
    su.subject_name,
    su.grade_level AS subject_grade_level,
    tp.staff_id,
    sf.full_name AS staff_name,
    tp.payment_date,
    tp.amount_paid,
    tp.payment_method,
    tp.note,
    tp.status AS payment_status,
    tp.created_at AS payment_created_at,
    tp.updated_at AS payment_updated_at,
    ti.period_start,
    ti.period_end,
    ti.amount_due,
    ti.amount_paid AS invoice_amount_paid,
    ti.status AS invoice_status
FROM TUITION_PAYMENT tp
JOIN TUITION_INVOICE ti ON ti.invoice_id = tp.invoice_id
JOIN STUDY_CLASS sc ON sc.class_id = ti.class_id
JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
JOIN STUDENT st ON st.student_id = lr.student_id
JOIN SUBJECT su ON su.subject_id = lr.subject_id
LEFT JOIN STAFF sf ON sf.staff_id = tp.staff_id;
```

Recommended function:

```text
FN_INVOICE_REMAINING_AMOUNT(@invoice_id)
```

Suggested function:

```sql
CREATE FUNCTION FN_INVOICE_REMAINING_AMOUNT (@invoice_id INT)
RETURNS DECIMAL(18,2)
AS
BEGIN
    DECLARE @remaining DECIMAL(18,2);

    SELECT @remaining =
        CASE
            WHEN amount_due - amount_paid < 0 THEN 0
            ELSE amount_due - amount_paid
        END
    FROM TUITION_INVOICE
    WHERE invoice_id = @invoice_id;

    RETURN COALESCE(@remaining, 0);
END;
```

Recommended stored procedure:

```text
SP_CREATE_TUITION_PAYMENT
```

Purpose:

```text
Accept invoice_id or class_id.
If class_id is provided and invoice does not exist for period, create invoice snapshot.
Validate canceled invoice.
Validate remaining amount for SUCCESS payment.
Insert payment.
Let trigger update invoice amount_paid/status.
Return payment_id or full payment detail.
```

Pseudo SQL:

```sql
CREATE PROCEDURE SP_CREATE_TUITION_PAYMENT
    @invoice_id INT = NULL,
    @class_id INT = NULL,
    @period_start DATE = NULL,
    @period_end DATE = NULL,
    @amount_paid DECIMAL(18,2),
    @payment_method NVARCHAR(50) = NULL,
    @payment_date DATETIME2 = NULL,
    @staff_id INT = NULL,
    @note NVARCHAR(MAX) = NULL,
    @status VARCHAR(20) = 'SUCCESS'
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRANSACTION;

    -- validate @amount_paid > 0
    -- validate @status in SUCCESS/CANCELED/REFUNDED
    -- resolve or create invoice
    -- if creating invoice:
    --   count completed LESSON_SESSION within period
    --   use STUDY_CLASS.tuition_fee_per_session
    --   insert TUITION_INVOICE with status UNPAID
    -- if @status = SUCCESS:
    --   check dbo.FN_INVOICE_REMAINING_AMOUNT(@invoice_id)
    -- insert TUITION_PAYMENT
    -- select created payment detail

    COMMIT TRANSACTION;
END;
```

Repository call:

```python
row = db.execute(text("""
    EXEC SP_CREATE_TUITION_PAYMENT
        @invoice_id = :invoice_id,
        @class_id = :class_id,
        @period_start = :period_start,
        @period_end = :period_end,
        @amount_paid = :amount_paid,
        @payment_method = :payment_method,
        @payment_date = :payment_date,
        @staff_id = :staff_id,
        @note = :note,
        @status = :status
"""), params).mappings().first()
```

Important trigger interaction:

- Procedure inserts payment.
- Trigger recalculates invoice.
- Procedure should return payment detail after trigger effects are visible.

If returning from trigger/procedure causes SQL Server result-set issues, procedure can output only `payment_id`, then repository calls `get_payment(payment_id)` from `VW_PAYMENT_DETAIL`.

### 6.12 Tuition Summary

Endpoint:

- `GET /classes/{id}/tuition-summary`

Current behavior:

- Python loops through sessions and payments.

Migration target:

- Raw SQL aggregate.
- This endpoint is realtime and should not depend only on invoice snapshots.

Recommended SQL:

```sql
WITH completed AS (
    SELECT
        class_id,
        COUNT(*) AS completed_sessions
    FROM LESSON_SESSION
    WHERE class_id = :class_id
      AND status = 'COMPLETED'
    GROUP BY class_id
),
paid AS (
    SELECT
        ti.class_id,
        COALESCE(SUM(CASE WHEN tp.status = 'SUCCESS' THEN tp.amount_paid ELSE 0 END), 0) AS paid_amount
    FROM TUITION_INVOICE ti
    LEFT JOIN TUITION_PAYMENT tp ON tp.invoice_id = ti.invoice_id
    WHERE ti.class_id = :class_id
    GROUP BY ti.class_id
)
SELECT
    sc.class_id,
    COALESCE(c.completed_sessions, 0) AS completed_sessions,
    sc.tuition_fee_per_session,
    COALESCE(c.completed_sessions, 0) * sc.tuition_fee_per_session AS total_fee,
    COALESCE(p.paid_amount, 0) AS paid_amount,
    (COALESCE(c.completed_sessions, 0) * sc.tuition_fee_per_session) - COALESCE(p.paid_amount, 0) AS remaining_amount
FROM STUDY_CLASS sc
LEFT JOIN completed c ON c.class_id = sc.class_id
LEFT JOIN paid p ON p.class_id = sc.class_id
WHERE sc.class_id = :class_id;
```

Recommended DB objects:

- Raw SQL aggregate is enough.
- Optional table-valued function only if reused in reports.

### 6.13 Dashboard Summary

Endpoint:

- `GET /dashboard/summary`

Current behavior:

- multiple `db.query(...).count()`

Migration target:

- one raw SQL aggregate statement.

Recommended SQL:

```sql
SELECT
    (SELECT COUNT(*) FROM STUDENT) AS total_students,
    (SELECT COUNT(*) FROM TUTOR) AS total_tutors,
    (SELECT COUNT(*) FROM LEARNING_REQUEST WHERE status = 'PENDING') AS pending_learning_requests,
    (SELECT COUNT(*) FROM STUDY_CLASS WHERE status = 'ACTIVE') AS active_classes,
    (SELECT COUNT(*) FROM LESSON_SESSION WHERE status = 'COMPLETED') AS completed_sessions,
    (SELECT COUNT(*) FROM TUITION_INVOICE WHERE status = 'UNPAID') AS unpaid_invoices,
    (SELECT COUNT(*) FROM TUITION_INVOICE WHERE status = 'PARTIALLY_PAID') AS partially_paid_invoices,
    (SELECT COUNT(*) FROM TUITION_PAYMENT WHERE status = 'SUCCESS') AS successful_payments;
```

Recommended DB objects:

- Raw SQL aggregate.
- Optional view only if dashboard grows.

## 7. SQL Schema Object Additions

Modify `sql/schema.sql` carefully.

Drop order near top should include new objects before tables:

```sql
IF OBJECT_ID(N'SP_CREATE_TUITION_PAYMENT', N'P') IS NOT NULL
    DROP PROCEDURE SP_CREATE_TUITION_PAYMENT;
GO

IF OBJECT_ID(N'FN_INVOICE_REMAINING_AMOUNT', N'FN') IS NOT NULL
    DROP FUNCTION FN_INVOICE_REMAINING_AMOUNT;
GO

DROP VIEW IF EXISTS VW_PAYMENT_DETAIL;
DROP VIEW IF EXISTS VW_INVOICE_DETAIL;
DROP VIEW IF EXISTS VW_LEARNING_REQUEST_DETAIL;
DROP VIEW IF EXISTS VW_STUDY_CLASS_DETAIL;
GO
```

Suggested final DB object set:

- Existing: `TRG_TUITION_PAYMENT_RECALC_INVOICE`
- Existing: `VW_STUDY_CLASS_DETAIL`
- New: `VW_LEARNING_REQUEST_DETAIL`
- New: `VW_INVOICE_DETAIL`
- New: `VW_PAYMENT_DETAIL`
- New: `FN_INVOICE_REMAINING_AMOUNT`
- New: `SP_CREATE_TUITION_PAYMENT`

Do not add objects just to add objects. Every object must support an endpoint or business rule.

## 8. Migration Batches

### Batch 1: Repository Foundation + Auth/Master Data

Files:

- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `backend/app/core/auth.py`
- `docs/current_status.md`
- `docs/agent_worklog.md`

Tasks:

1. Add raw SQL helper functions.
2. Convert user/account queries.
3. Convert staff/student/subject basic CRUD.
4. Convert auth profile resolution.
5. Replace service direct object mutations for student/subject with repository SQL update functions.

Validation:

```powershell
uv run python -m compileall backend/app backend/tests/http_crud_smoke.py
rg "db\.(query|add|delete)" backend/app
```

Expected partial result:

- Some `db.query` remains for unconverted modules.
- No `db.query` remains in auth/master-data paths.

### Batch 2: Tutor Profile

Files:

- `data_repository.py`
- `business_service.py`

Tasks:

1. Convert tutor CRUD.
2. Convert tutor capabilities.
3. Convert tutor availability.
4. Manually attach `capabilities` and `subject` objects for response compatibility.
5. Remove service `db.flush()` usage in tutor subject rebuild.

Validation:

```powershell
uv run python -m compileall backend/app backend/tests/http_crud_smoke.py
```

If backend is running:

```powershell
cd backend
uv run python tests/http_crud_smoke.py --base-url http://127.0.0.1:8000 --staff-email staff1@smarttutor.local --staff-password staff123
```

### Batch 3: Request + Assignment

Files:

- `sql/schema.sql` optionally for `VW_LEARNING_REQUEST_DETAIL`
- `data_repository.py`
- `business_service.py`

Tasks:

1. Add/use `VW_LEARNING_REQUEST_DETAIL` if desired.
2. Convert learning request CRUD.
3. Convert assignment CRUD.
4. Replace assignment/request status transitions with explicit SQL updates.
5. Ensure cancel assignment still refuses if a class already exists.

Validation:

- Compile.
- Auth-aware smoke test if backend is running.
- Negative tests later for duplicate active assignment and non-pending request.

### Batch 4: Class + Schedule + Session

Files:

- `data_repository.py`
- `business_service.py`
- possibly `sql/schema.sql` if `VW_STUDY_CLASS_DETAIL` needs additional fields

Tasks:

1. Convert class create/update/cancel to raw SQL.
2. Convert class list/detail to `VW_STUDY_CLASS_DETAIL`.
3. Adjust `class_to_response` to support view-backed flat rows.
4. Convert schedules to raw SQL.
5. Convert sessions to raw SQL.
6. Convert `tuition_summary` from Python loops to raw SQL aggregate.

Validation:

- Compile.
- Smoke test.
- Manually verify `GET /classes` still returns student/tutor/subject display fields.
- Manually verify `GET /classes/{id}/tuition-summary`.

### Batch 5: Finance Views + Function + Procedure

Files:

- `sql/schema.sql`
- `data_repository.py`
- `business_service.py`
- `docs/api_contract.md`

Tasks:

1. Add `VW_INVOICE_DETAIL`.
2. Add `VW_PAYMENT_DETAIL`.
3. Add `FN_INVOICE_REMAINING_AMOUNT`.
4. Add `SP_CREATE_TUITION_PAYMENT`.
5. Convert invoice list/detail reads to view or raw join.
6. Convert payment list/detail reads to `VW_PAYMENT_DETAIL`.
7. Convert `create_payment` to call `SP_CREATE_TUITION_PAYMENT`.
8. Keep trigger `TRG_TUITION_PAYMENT_RECALC_INVOICE`.
9. Convert payment update/cancel to raw SQL and rely on trigger recalculation.

Validation:

- Re-run schema reset locally if safe.
- Compile.
- Smoke test.
- SQL direct verification:

```sql
SELECT * FROM VW_PAYMENT_DETAIL;
SELECT dbo.FN_INVOICE_REMAINING_AMOUNT(1);
EXEC SP_CREATE_TUITION_PAYMENT ...;
```

### Batch 6: Dashboard + Final Cleanup

Files:

- `data_repository.py`
- `business_service.py`
- docs

Tasks:

1. Convert dashboard summary to raw SQL aggregate.
2. Remove unused ORM imports from repository/service where possible.
3. Search for leftover ORM access:

```powershell
rg "db\.(query|add|delete|refresh|flush)" backend/app
rg "joinedload|\\.options\\(" backend/app
```

4. Update docs:
   - `docs/current_status.md`
   - `docs/completion_matrix.md`
   - `docs/database_implementation.md`

## 9. Documentation Deliverables

Create a new doc:

```text
docs/database_implementation.md
```

It should include:

1. Database architecture summary.
2. List of raw SQL repository CRUD groups.
3. Views and which endpoints use them.
4. Trigger behavior and example verification SQL.
5. Stored procedure behavior and example call.
6. Function behavior and example call.
7. Evidence commands.

Suggested evidence table:

| Area | DB Technique | File/Object | Endpoint |
| --- | --- | --- | --- |
| Student CRUD | Raw SQL | `data_repository.py` | `/students` |
| Class list/detail | View | `VW_STUDY_CLASS_DETAIL` | `/classes` |
| Payment detail | View | `VW_PAYMENT_DETAIL` | `/payments` |
| Invoice sync | Trigger | `TRG_TUITION_PAYMENT_RECALC_INVOICE` | `/payments` |
| Payment create | Stored procedure | `SP_CREATE_TUITION_PAYMENT` | `POST /payments` |
| Remaining amount | Function | `FN_INVOICE_REMAINING_AMOUNT` | payment validation |
| Dashboard | Aggregate SQL | `dashboard_summary` query | `/dashboard/summary` |

## 10. Risks And Mitigations

Risk: service mutates fake object and commit does nothing.

Mitigation:

- Replace all `repo.apply_updates(model, data)` with explicit `repo.update_*`.
- Replace all direct assignments before commit with explicit SQL update functions.
- Search patterns:

```powershell
rg "\\.status\\s*=|\\.content_note\\s*=|repo\\.apply_updates|repo\\.touch_model" backend/app/services/business_service.py
```

Risk: response mappers expect nested ORM relationships.

Mitigation:

- For early batches, attach fake nested objects.
- For class/payment/invoice, prefer view-backed flat response mappers.

Risk: SQL injection in dynamic update helper.

Mitigation:

- Whitelist all update columns.
- Never pass request-provided table or column names.
- Values always use bound parameters.

Risk: trigger/procedure result ordering causes SQL Server driver issues.

Mitigation:

- Use `SET NOCOUNT ON`.
- If procedure returning a result set is unreliable, return only inserted id and then repository selects detail row separately.

Risk: docs say PASS but live backend not tested.

Mitigation:

- Mark compile-only coverage as pending live rerun.
- Only mark PASS after running smoke test against SQL Server.

## 11. Final Acceptance Criteria

Code criteria:

- `data_repository.py` uses raw SQL via `sqlalchemy.text`.
- No app runtime code uses `db.query`, `db.add`, or `db.delete`.
- Service does not rely on ORM object mutation for writes.
- Auth uses raw SQL repository functions.
- Dashboard uses aggregate SQL.
- Class read path uses `VW_STUDY_CLASS_DETAIL`.
- Finance read path uses finance view(s).
- Payment create uses procedure or an explicitly documented raw SQL transaction.
- Payment/invoice synchronization remains database-side through trigger.

SQL criteria:

- `sql/schema.sql` contains all final views/triggers/functions/procedures.
- SQL object drop/create order works on clean reset.
- Constraints remain aligned with `AGENTS.md`.

Validation criteria:

```powershell
uv run python -m compileall backend/app backend/tests/http_crud_smoke.py
```

If backend is running:

```powershell
cd backend
uv run python tests/http_crud_smoke.py --base-url http://127.0.0.1:8000 --staff-email staff1@smarttutor.local --staff-password staff123
```

Search criteria:

```powershell
rg "db\.(query|add|delete|refresh|flush)" backend/app
rg "joinedload|\\.options\\(" backend/app
```

Docs criteria:

- `docs/current_status.md` reflects raw SQL DB layer status.
- `docs/completion_matrix.md` reflects exact PASS/PARTIAL state.
- `docs/agent_worklog.md` has one entry per batch.
- `docs/database_implementation.md` proves raw SQL, views, trigger, procedure, and function usage.

## 12. Recommended Starting Prompt For New Chat

Use this prompt in a new chat:

```text
We are on branch demo2 of SmartTutor-Platform.
Read AGENTS.md, docs/current_status.md, and docs/sql_raw_repository_migration_plan.md.
Start Batch 1 only: convert repository foundation + auth/master data to raw SQL in backend/app/repositories/data_repository.py, without creating data_repository_sql.py.
Keep function names where practical.
Do not convert class/payment yet.
Run compile and update docs/current_status.md + docs/agent_worklog.md.
```


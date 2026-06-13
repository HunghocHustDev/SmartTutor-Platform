-- TutorCenterDB - SQL Server schema FINAL CLEAN
-- Project: Tutor Center Management System
-- Database: SQL Server
--
-- Design principle:
--   Keep normalized business flow:
--   LEARNING_REQUEST -> TUTOR_ASSIGNMENT -> STUDY_CLASS
--
-- Important normalization rule:
--   STUDY_CLASS does NOT store student_id, tutor_id, or subject_id directly.
--   Class-related student/tutor/subject data is reached through:
--   STUDY_CLASS -> TUTOR_ASSIGNMENT -> LEARNING_REQUEST -> STUDENT/SUBJECT
--   and TUTOR_ASSIGNMENT -> TUTOR.
--
-- Day of week convention:
--   1 = Monday
--   2 = Tuesday
--   3 = Wednesday
--   4 = Thursday
--   5 = Friday
--   6 = Saturday
--   7 = Sunday
--
-- Notes:
--   This script resets application objects inside TutorCenterDB.
--   Do not run on production data unless you intentionally want to recreate the schema.

IF DB_ID(N'TutorCenterDB') IS NULL
BEGIN
    CREATE DATABASE TutorCenterDB;
END
GO

USE TutorCenterDB;
GO

/* =========================================================
   0. DROP OLD OBJECTS FOR CLEAN RE-RUN
   ========================================================= */

IF OBJECT_ID(N'TRG_TUITION_PAYMENT_RECALC_INVOICE', N'TR') IS NOT NULL
    DROP TRIGGER TRG_TUITION_PAYMENT_RECALC_INVOICE;
GO

DROP VIEW IF EXISTS VW_STUDY_CLASS_DETAIL;
GO

DROP TABLE IF EXISTS TUITION_PAYMENT;
DROP TABLE IF EXISTS TUITION_INVOICE;
DROP TABLE IF EXISTS LESSON_SESSION;
DROP TABLE IF EXISTS CLASS_SCHEDULE;
DROP TABLE IF EXISTS STUDY_CLASS;
DROP TABLE IF EXISTS TUTOR_ASSIGNMENT;
DROP TABLE IF EXISTS LEARNING_REQUEST;
DROP TABLE IF EXISTS TUTOR_CAPABILITY;
DROP TABLE IF EXISTS TUTOR_AVAILABILITY;
DROP TABLE IF EXISTS TUTOR;
DROP TABLE IF EXISTS STUDENT;
DROP TABLE IF EXISTS STAFF;
DROP TABLE IF EXISTS SUBJECT;
DROP TABLE IF EXISTS USER_ACCOUNT;
GO

/* =========================================================
   1. USER / MASTER TABLES
   ========================================================= */

CREATE TABLE USER_ACCOUNT (
    account_id INT IDENTITY(1,1) PRIMARY KEY,
    email NVARCHAR(255) NOT NULL,
    username NVARCHAR(50) NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT UQ_USER_ACCOUNT_EMAIL UNIQUE (email),
    CONSTRAINT UQ_USER_ACCOUNT_USERNAME UNIQUE (username),
    CONSTRAINT CK_USER_ACCOUNT_ROLE CHECK (role IN ('STAFF', 'STUDENT', 'TUTOR')),
    CONSTRAINT CK_USER_ACCOUNT_STATUS CHECK (status IN ('ACTIVE', 'INACTIVE'))
);
GO

CREATE TABLE SUBJECT (
    subject_id INT IDENTITY(1,1) PRIMARY KEY,
    subject_name NVARCHAR(100) NOT NULL,
    subject_group NVARCHAR(50) NULL,
    grade_level NVARCHAR(50) NULL,
    description NVARCHAR(MAX) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT CK_SUBJECT_STATUS CHECK (status IN ('ACTIVE', 'INACTIVE')),
    CONSTRAINT UQ_SUBJECT_NAME_LEVEL UNIQUE (subject_name, grade_level)
);
GO

CREATE TABLE STAFF (
    staff_id INT IDENTITY(1,1) PRIMARY KEY,
    account_id INT NULL,
    full_name NVARCHAR(150) NOT NULL,
    phone NVARCHAR(20) NULL,
    contact_email NVARCHAR(255) NULL,
    position NVARCHAR(50) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT FK_STAFF_ACCOUNT
        FOREIGN KEY (account_id) REFERENCES USER_ACCOUNT(account_id),
    CONSTRAINT CK_STAFF_STATUS CHECK (status IN ('ACTIVE', 'INACTIVE'))
);
GO

CREATE TABLE STUDENT (
    student_id INT IDENTITY(1,1) PRIMARY KEY,
    account_id INT NULL,
    full_name NVARCHAR(150) NOT NULL,
    phone NVARCHAR(20) NOT NULL,
    contact_email NVARCHAR(255) NULL,
    address NVARCHAR(255) NULL,
    area NVARCHAR(150) NULL,
    current_level NVARCHAR(50) NULL,
    grade_level NVARCHAR(50) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT FK_STUDENT_ACCOUNT
        FOREIGN KEY (account_id) REFERENCES USER_ACCOUNT(account_id),
    CONSTRAINT CK_STUDENT_STATUS CHECK (status IN ('ACTIVE', 'INACTIVE'))
);
GO

CREATE TABLE TUTOR (
    tutor_id INT IDENTITY(1,1) PRIMARY KEY,
    account_id INT NULL,
    full_name NVARCHAR(150) NOT NULL,
    phone NVARCHAR(20) NULL,
    contact_email NVARCHAR(255) NULL,
    university NVARCHAR(150) NULL,
    major NVARCHAR(150) NULL,
    experience_years INT NOT NULL DEFAULT 0,
    area NVARCHAR(255) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT FK_TUTOR_ACCOUNT
        FOREIGN KEY (account_id) REFERENCES USER_ACCOUNT(account_id),
    CONSTRAINT CK_TUTOR_STATUS CHECK (status IN ('ACTIVE', 'INACTIVE', 'PAUSED')),
    CONSTRAINT CK_TUTOR_EXPERIENCE CHECK (experience_years >= 0)
);
GO

/* Filtered unique indexes for nullable account_id.
   This avoids SQL Server UNIQUE + multiple NULL issue. */
CREATE UNIQUE INDEX UQ_STAFF_ACCOUNT_NOT_NULL
ON STAFF(account_id)
WHERE account_id IS NOT NULL;
GO

CREATE UNIQUE INDEX UQ_STUDENT_ACCOUNT_NOT_NULL
ON STUDENT(account_id)
WHERE account_id IS NOT NULL;
GO

CREATE UNIQUE INDEX UQ_TUTOR_ACCOUNT_NOT_NULL
ON TUTOR(account_id)
WHERE account_id IS NOT NULL;
GO

/* =========================================================
   2. TUTOR PROFILE DETAILS
   ========================================================= */

CREATE TABLE TUTOR_AVAILABILITY (
    availability_id INT IDENTITY(1,1) PRIMARY KEY,
    tutor_id INT NOT NULL,
    day_of_week TINYINT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    teaching_mode VARCHAR(20) NOT NULL DEFAULT 'OFFLINE',
    area NVARCHAR(150) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT FK_TUTOR_AVAILABILITY_TUTOR
        FOREIGN KEY (tutor_id) REFERENCES TUTOR(tutor_id),
    CONSTRAINT CK_TUTOR_AVAILABILITY_DAY CHECK (day_of_week BETWEEN 1 AND 7),
    CONSTRAINT CK_TUTOR_AVAILABILITY_TIME CHECK (start_time < end_time),
    CONSTRAINT CK_TUTOR_AVAILABILITY_MODE CHECK (teaching_mode IN ('ONLINE', 'OFFLINE', 'BOTH')),
    CONSTRAINT CK_TUTOR_AVAILABILITY_STATUS CHECK (status IN ('AVAILABLE', 'UNAVAILABLE'))
);
GO

CREATE TABLE TUTOR_CAPABILITY (
    capability_id INT IDENTITY(1,1) PRIMARY KEY,
    tutor_id INT NOT NULL,
    subject_id INT NOT NULL,
    teaching_level NVARCHAR(50) NULL,
    years_experience INT NOT NULL DEFAULT 0,
    note NVARCHAR(500) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT FK_TUTOR_CAPABILITY_TUTOR
        FOREIGN KEY (tutor_id) REFERENCES TUTOR(tutor_id),
    CONSTRAINT FK_TUTOR_CAPABILITY_SUBJECT
        FOREIGN KEY (subject_id) REFERENCES SUBJECT(subject_id),
    CONSTRAINT CK_TUTOR_CAPABILITY_EXPERIENCE CHECK (years_experience >= 0),
    CONSTRAINT UQ_TUTOR_CAPABILITY UNIQUE (tutor_id, subject_id, teaching_level)
);
GO

/* =========================================================
   3. LEARNING REQUEST -> ASSIGNMENT -> STUDY CLASS
   ========================================================= */

CREATE TABLE LEARNING_REQUEST (
    request_id INT IDENTITY(1,1) PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    requested_level NVARCHAR(50) NULL,
    learning_goal NVARCHAR(MAX) NULL,
    preferred_area NVARCHAR(255) NULL,
    preferred_mode VARCHAR(20) NOT NULL DEFAULT 'OFFLINE',
    preferred_schedule NVARCHAR(255) NULL,
    expected_fee DECIMAL(18,2) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT FK_LEARNING_REQUEST_STUDENT
        FOREIGN KEY (student_id) REFERENCES STUDENT(student_id),
    CONSTRAINT FK_LEARNING_REQUEST_SUBJECT
        FOREIGN KEY (subject_id) REFERENCES SUBJECT(subject_id),
    CONSTRAINT CK_LEARNING_REQUEST_MODE CHECK (preferred_mode IN ('ONLINE', 'OFFLINE', 'BOTH')),
    CONSTRAINT CK_LEARNING_REQUEST_STATUS CHECK (status IN ('PENDING', 'ASSIGNED', 'CANCELED')),
    CONSTRAINT CK_LEARNING_REQUEST_EXPECTED_FEE CHECK (expected_fee IS NULL OR expected_fee >= 0)
);
GO

CREATE TABLE TUTOR_ASSIGNMENT (
    assignment_id INT IDENTITY(1,1) PRIMARY KEY,
    request_id INT NOT NULL,
    tutor_id INT NOT NULL,
    staff_id INT NULL,
    assigned_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    status VARCHAR(20) NOT NULL DEFAULT 'ASSIGNED',
    note NVARCHAR(500) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT FK_TUTOR_ASSIGNMENT_REQUEST
        FOREIGN KEY (request_id) REFERENCES LEARNING_REQUEST(request_id),
    CONSTRAINT FK_TUTOR_ASSIGNMENT_TUTOR
        FOREIGN KEY (tutor_id) REFERENCES TUTOR(tutor_id),
    CONSTRAINT FK_TUTOR_ASSIGNMENT_STAFF
        FOREIGN KEY (staff_id) REFERENCES STAFF(staff_id),
    CONSTRAINT CK_TUTOR_ASSIGNMENT_STATUS CHECK (status IN ('ASSIGNED', 'CANCELED'))
);
GO

/* A request may have assignment history, but only one active assignment at a time. */
CREATE UNIQUE INDEX UQ_ACTIVE_ASSIGNMENT_PER_REQUEST
ON TUTOR_ASSIGNMENT(request_id)
WHERE status = 'ASSIGNED';
GO

CREATE TABLE STUDY_CLASS (
    class_id INT IDENTITY(1,1) PRIMARY KEY,
    assignment_id INT NOT NULL,
    class_code NVARCHAR(50) NOT NULL,
    tuition_fee_per_session DECIMAL(18,2) NOT NULL,
    teaching_mode VARCHAR(20) NOT NULL DEFAULT 'OFFLINE',
    location NVARCHAR(255) NULL,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT UQ_STUDY_CLASS_ASSIGNMENT UNIQUE (assignment_id),
    CONSTRAINT UQ_STUDY_CLASS_CODE UNIQUE (class_code),
    CONSTRAINT FK_STUDY_CLASS_ASSIGNMENT
        FOREIGN KEY (assignment_id) REFERENCES TUTOR_ASSIGNMENT(assignment_id),
    CONSTRAINT CK_STUDY_CLASS_TUITION CHECK (tuition_fee_per_session >= 0),
    CONSTRAINT CK_STUDY_CLASS_MODE CHECK (teaching_mode IN ('ONLINE', 'OFFLINE')),
    CONSTRAINT CK_STUDY_CLASS_STATUS CHECK (status IN ('ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELED')),
    CONSTRAINT CK_STUDY_CLASS_DATE CHECK (end_date IS NULL OR end_date >= start_date)
);
GO

/* =========================================================
   4. SCHEDULES AND LESSON SESSIONS
   ========================================================= */

CREATE TABLE CLASS_SCHEDULE (
    schedule_id INT IDENTITY(1,1) PRIMARY KEY,
    class_id INT NOT NULL,
    day_of_week TINYINT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    effective_from DATE NULL,
    effective_to DATE NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    note NVARCHAR(500) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT FK_CLASS_SCHEDULE_CLASS
        FOREIGN KEY (class_id) REFERENCES STUDY_CLASS(class_id),
    CONSTRAINT CK_CLASS_SCHEDULE_DAY CHECK (day_of_week BETWEEN 1 AND 7),
    CONSTRAINT CK_CLASS_SCHEDULE_TIME CHECK (start_time < end_time),
    CONSTRAINT CK_CLASS_SCHEDULE_STATUS CHECK (status IN ('ACTIVE', 'INACTIVE')),
    CONSTRAINT CK_CLASS_SCHEDULE_DATE CHECK (effective_to IS NULL OR effective_from IS NULL OR effective_to >= effective_from),
    CONSTRAINT UQ_CLASS_SCHEDULE_SLOT UNIQUE (class_id, day_of_week, start_time, end_time),
    CONSTRAINT UQ_CLASS_SCHEDULE_ID_CLASS UNIQUE (schedule_id, class_id)
);
GO

CREATE TABLE LESSON_SESSION (
    session_id INT IDENTITY(1,1) PRIMARY KEY,
    class_id INT NOT NULL,
    schedule_id INT NULL,
    session_number INT NULL,
    lesson_date DATE NOT NULL,
    start_time TIME NULL,
    end_time TIME NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'SCHEDULED',
    content_note NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT FK_LESSON_SESSION_CLASS
        FOREIGN KEY (class_id) REFERENCES STUDY_CLASS(class_id),
    CONSTRAINT FK_LESSON_SESSION_SCHEDULE_CLASS
        FOREIGN KEY (schedule_id, class_id) REFERENCES CLASS_SCHEDULE(schedule_id, class_id),
    CONSTRAINT CK_LESSON_SESSION_NUMBER CHECK (session_number IS NULL OR session_number > 0),
    CONSTRAINT CK_LESSON_SESSION_TIME CHECK (
        (start_time IS NULL AND end_time IS NULL)
        OR
        (start_time IS NOT NULL AND end_time IS NOT NULL AND start_time < end_time)
    ),
    CONSTRAINT CK_LESSON_SESSION_STATUS CHECK (status IN ('SCHEDULED', 'COMPLETED', 'STUDENT_ABSENT', 'TUTOR_ABSENT', 'CANCELED'))
);
GO

CREATE UNIQUE INDEX UQ_LESSON_SESSION_CLASS_NUMBER_NOT_NULL
ON LESSON_SESSION(class_id, session_number)
WHERE session_number IS NOT NULL;
GO

/* =========================================================
   5. TUITION INVOICE AND PAYMENT
   ========================================================= */

CREATE TABLE TUITION_INVOICE (
    invoice_id INT IDENTITY(1,1) PRIMARY KEY,
    class_id INT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    completed_sessions INT NOT NULL DEFAULT 0,
    tuition_fee_per_session DECIMAL(18,2) NOT NULL,
    amount_due DECIMAL(18,2) NOT NULL,
    amount_paid DECIMAL(18,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'UNPAID',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT FK_TUITION_INVOICE_CLASS
        FOREIGN KEY (class_id) REFERENCES STUDY_CLASS(class_id),
    CONSTRAINT CK_TUITION_INVOICE_PERIOD CHECK (period_end >= period_start),
    CONSTRAINT CK_TUITION_INVOICE_COMPLETED CHECK (completed_sessions >= 0),
    CONSTRAINT CK_TUITION_INVOICE_FEE CHECK (tuition_fee_per_session >= 0),
    CONSTRAINT CK_TUITION_INVOICE_AMOUNT CHECK (amount_due >= 0 AND amount_paid >= 0 AND amount_paid <= amount_due),
    CONSTRAINT CK_TUITION_INVOICE_STATUS CHECK (status IN ('UNPAID', 'PARTIALLY_PAID', 'PAID', 'OVERDUE', 'CANCELED')),
    CONSTRAINT UQ_TUITION_INVOICE_CLASS_PERIOD UNIQUE (class_id, period_start, period_end)
);
GO

CREATE TABLE TUITION_PAYMENT (
    payment_id INT IDENTITY(1,1) PRIMARY KEY,
    invoice_id INT NOT NULL,
    staff_id INT NULL,
    payment_date DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    amount_paid DECIMAL(18,2) NOT NULL,
    payment_method NVARCHAR(50) NULL,
    note NVARCHAR(MAX) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'SUCCESS',
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT FK_TUITION_PAYMENT_INVOICE
        FOREIGN KEY (invoice_id) REFERENCES TUITION_INVOICE(invoice_id),
    CONSTRAINT FK_TUITION_PAYMENT_STAFF
        FOREIGN KEY (staff_id) REFERENCES STAFF(staff_id),
    CONSTRAINT CK_TUITION_PAYMENT_AMOUNT CHECK (amount_paid > 0),
    CONSTRAINT CK_TUITION_PAYMENT_STATUS CHECK (status IN ('SUCCESS', 'CANCELED', 'REFUNDED'))
);
GO

/* Keep TUITION_INVOICE.amount_paid and status consistent with successful payments.
   Only payments with status = 'SUCCESS' are counted as paid money.
   If successful payments exceed amount_due, the invoice CHECK constraint fails and rolls back the operation. */
CREATE TRIGGER TRG_TUITION_PAYMENT_RECALC_INVOICE
ON TUITION_PAYMENT
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    ;WITH affected_invoice AS (
        SELECT invoice_id FROM inserted
        UNION
        SELECT invoice_id FROM deleted
    ),
    paid_summary AS (
        SELECT
            ai.invoice_id,
            COALESCE(SUM(CASE WHEN tp.status = 'SUCCESS' THEN tp.amount_paid ELSE 0 END), 0) AS total_paid
        FROM affected_invoice ai
        LEFT JOIN TUITION_PAYMENT tp
            ON ai.invoice_id = tp.invoice_id
        GROUP BY ai.invoice_id
    )
    UPDATE ti
    SET
        amount_paid = ps.total_paid,
        status =
            CASE
                WHEN ti.status = 'CANCELED' THEN 'CANCELED'
                WHEN ti.amount_due = 0 THEN 'PAID'
                WHEN ps.total_paid = 0 THEN 'UNPAID'
                WHEN ps.total_paid < ti.amount_due THEN 'PARTIALLY_PAID'
                ELSE 'PAID'
            END,
        updated_at = SYSUTCDATETIME()
    FROM TUITION_INVOICE ti
    JOIN paid_summary ps
        ON ti.invoice_id = ps.invoice_id;
END;
GO

/* =========================================================
   6. VIEWS FOR BACKEND/FRONTEND DISPLAY
   ========================================================= */

CREATE VIEW VW_STUDY_CLASS_DETAIL
AS
SELECT
    sc.class_id,
    sc.class_code,
    sc.tuition_fee_per_session,
    sc.teaching_mode,
    sc.location,
    sc.start_date,
    sc.end_date,
    sc.status AS class_status,
    sc.created_at AS class_created_at,

    ta.assignment_id,
    ta.status AS assignment_status,
    ta.assigned_at,

    lr.request_id,
    lr.requested_level,
    lr.learning_goal,
    lr.preferred_area,
    lr.preferred_mode,
    lr.preferred_schedule,

    st.student_id,
    st.full_name AS student_name,
    st.phone AS student_phone,

    tu.tutor_id,
    tu.full_name AS tutor_name,
    tu.phone AS tutor_phone,

    su.subject_id,
    su.subject_name,
    su.grade_level AS subject_grade_level,

    sf.staff_id,
    sf.full_name AS staff_name
FROM STUDY_CLASS sc
JOIN TUTOR_ASSIGNMENT ta
    ON sc.assignment_id = ta.assignment_id
JOIN LEARNING_REQUEST lr
    ON ta.request_id = lr.request_id
JOIN STUDENT st
    ON lr.student_id = st.student_id
JOIN SUBJECT su
    ON lr.subject_id = su.subject_id
JOIN TUTOR tu
    ON ta.tutor_id = tu.tutor_id
LEFT JOIN STAFF sf
    ON ta.staff_id = sf.staff_id;
GO

/* =========================================================
   7. INDEXES FOR SEARCH / FILTER / JOIN
   ========================================================= */

CREATE INDEX IX_USER_ACCOUNT_ROLE_STATUS ON USER_ACCOUNT(role, status);

CREATE INDEX IX_SUBJECT_NAME ON SUBJECT(subject_name);
CREATE INDEX IX_SUBJECT_STATUS ON SUBJECT(status);

CREATE INDEX IX_STAFF_FULL_NAME ON STAFF(full_name);
CREATE INDEX IX_STAFF_STATUS ON STAFF(status);

CREATE INDEX IX_STUDENT_FULL_NAME ON STUDENT(full_name);
CREATE INDEX IX_STUDENT_PHONE ON STUDENT(phone);
CREATE INDEX IX_STUDENT_STATUS ON STUDENT(status);
CREATE INDEX IX_STUDENT_AREA ON STUDENT(area);

CREATE INDEX IX_TUTOR_FULL_NAME ON TUTOR(full_name);
CREATE INDEX IX_TUTOR_PHONE ON TUTOR(phone);
CREATE INDEX IX_TUTOR_STATUS ON TUTOR(status);
CREATE INDEX IX_TUTOR_AREA ON TUTOR(area);

CREATE INDEX IX_TUTOR_AVAILABILITY_TUTOR ON TUTOR_AVAILABILITY(tutor_id);
CREATE INDEX IX_TUTOR_AVAILABILITY_DAY_TIME ON TUTOR_AVAILABILITY(day_of_week, start_time, end_time);
CREATE INDEX IX_TUTOR_CAPABILITY_TUTOR ON TUTOR_CAPABILITY(tutor_id);
CREATE INDEX IX_TUTOR_CAPABILITY_SUBJECT ON TUTOR_CAPABILITY(subject_id);

CREATE INDEX IX_LEARNING_REQUEST_STUDENT ON LEARNING_REQUEST(student_id);
CREATE INDEX IX_LEARNING_REQUEST_SUBJECT ON LEARNING_REQUEST(subject_id);
CREATE INDEX IX_LEARNING_REQUEST_STATUS ON LEARNING_REQUEST(status);

CREATE INDEX IX_TUTOR_ASSIGNMENT_REQUEST ON TUTOR_ASSIGNMENT(request_id);
CREATE INDEX IX_TUTOR_ASSIGNMENT_TUTOR ON TUTOR_ASSIGNMENT(tutor_id);
CREATE INDEX IX_TUTOR_ASSIGNMENT_STAFF ON TUTOR_ASSIGNMENT(staff_id);
CREATE INDEX IX_TUTOR_ASSIGNMENT_STATUS ON TUTOR_ASSIGNMENT(status);

CREATE INDEX IX_STUDY_CLASS_STATUS ON STUDY_CLASS(status);

CREATE INDEX IX_CLASS_SCHEDULE_CLASS ON CLASS_SCHEDULE(class_id);
CREATE INDEX IX_CLASS_SCHEDULE_DAY_TIME ON CLASS_SCHEDULE(day_of_week, start_time, end_time);

CREATE INDEX IX_LESSON_SESSION_CLASS_DATE ON LESSON_SESSION(class_id, lesson_date);
CREATE INDEX IX_LESSON_SESSION_SCHEDULE ON LESSON_SESSION(schedule_id);
CREATE INDEX IX_LESSON_SESSION_STATUS ON LESSON_SESSION(status);

CREATE INDEX IX_TUITION_INVOICE_CLASS ON TUITION_INVOICE(class_id);
CREATE INDEX IX_TUITION_INVOICE_STATUS ON TUITION_INVOICE(status);
CREATE INDEX IX_TUITION_PAYMENT_INVOICE ON TUITION_PAYMENT(invoice_id);
CREATE INDEX IX_TUITION_PAYMENT_STAFF ON TUITION_PAYMENT(staff_id);
GO

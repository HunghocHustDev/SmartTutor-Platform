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

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

/* =========================================================
   0. DROP OLD OBJECTS FOR CLEAN RE-RUN
   ========================================================= */

IF OBJECT_ID(N'TRG_TUITION_PAYMENT_RECALC_INVOICE', N'TR') IS NOT NULL
    DROP TRIGGER TRG_TUITION_PAYMENT_RECALC_INVOICE;
GO

IF OBJECT_ID(N'SP_CREATE_TUITION_PAYMENT', N'P') IS NOT NULL
    DROP PROCEDURE SP_CREATE_TUITION_PAYMENT;
GO

IF OBJECT_ID(N'SP_ASSIGN_TUTOR_TO_REQUEST', N'P') IS NOT NULL
    DROP PROCEDURE SP_ASSIGN_TUTOR_TO_REQUEST;
GO

IF OBJECT_ID(N'FN_INVOICE_REMAINING_AMOUNT', N'FN') IS NOT NULL
    DROP FUNCTION FN_INVOICE_REMAINING_AMOUNT;
GO

IF OBJECT_ID(N'FN_CLASS_TUITION_SUMMARY', N'IF') IS NOT NULL
    DROP FUNCTION FN_CLASS_TUITION_SUMMARY;
GO

DROP VIEW IF EXISTS VW_PAYMENT_DETAIL;
DROP VIEW IF EXISTS VW_INVOICE_DETAIL;
DROP VIEW IF EXISTS VW_LESSON_SESSION_DETAIL;
DROP VIEW IF EXISTS VW_LEARNING_REQUEST_DETAIL;
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

CREATE FUNCTION FN_INVOICE_REMAINING_AMOUNT (@invoice_id INT)
RETURNS DECIMAL(18,2)
AS
BEGIN
    DECLARE @remaining DECIMAL(18,2);

    SELECT
        @remaining =
            CASE
                WHEN amount_due - amount_paid < 0 THEN 0
                ELSE amount_due - amount_paid
            END
    FROM TUITION_INVOICE
    WHERE invoice_id = @invoice_id;

    RETURN COALESCE(@remaining, 0);
END;
GO

CREATE FUNCTION FN_CLASS_TUITION_SUMMARY (@class_id INT)
RETURNS TABLE
AS
RETURN
WITH completed AS (
    SELECT
        ls.class_id,
        COUNT(*) AS completed_sessions
    FROM LESSON_SESSION ls
    WHERE ls.class_id = @class_id
      AND ls.status = 'COMPLETED'
    GROUP BY ls.class_id
),
invoice_totals AS (
    SELECT
        ti.class_id,
        COALESCE(SUM(ti.amount_due), 0) AS total_invoiced,
        SUM(CASE WHEN ti.status IN ('UNPAID', 'PARTIALLY_PAID', 'OVERDUE') THEN 1 ELSE 0 END) AS unpaid_invoice_count,
        SUM(CASE WHEN ti.status = 'OVERDUE' THEN 1 ELSE 0 END) AS overdue_invoice_count
    FROM TUITION_INVOICE ti
    WHERE ti.class_id = @class_id
    GROUP BY ti.class_id
),
payment_totals AS (
    SELECT
        ti.class_id,
        COALESCE(SUM(CASE WHEN tp.status = 'SUCCESS' THEN tp.amount_paid ELSE 0 END), 0) AS total_paid_success
    FROM TUITION_INVOICE ti
    LEFT JOIN TUITION_PAYMENT tp
        ON tp.invoice_id = ti.invoice_id
    WHERE ti.class_id = @class_id
    GROUP BY ti.class_id
)
SELECT
    sc.class_id,
    COALESCE(c.completed_sessions, 0) AS completed_sessions,
    sc.tuition_fee_per_session,
    COALESCE(c.completed_sessions, 0) * sc.tuition_fee_per_session AS total_fee,
    COALESCE(i.total_invoiced, 0) AS total_invoiced,
    COALESCE(p.total_paid_success, 0) AS total_paid_success,
    CASE
        WHEN (COALESCE(c.completed_sessions, 0) * sc.tuition_fee_per_session) - COALESCE(p.total_paid_success, 0) < 0 THEN 0
        ELSE (COALESCE(c.completed_sessions, 0) * sc.tuition_fee_per_session) - COALESCE(p.total_paid_success, 0)
    END AS total_remaining,
    COALESCE(i.unpaid_invoice_count, 0) AS unpaid_invoice_count,
    COALESCE(i.overdue_invoice_count, 0) AS overdue_invoice_count,
    COALESCE(p.total_paid_success, 0) AS paid_amount,
    CASE
        WHEN (COALESCE(c.completed_sessions, 0) * sc.tuition_fee_per_session) - COALESCE(p.total_paid_success, 0) < 0 THEN 0
        ELSE (COALESCE(c.completed_sessions, 0) * sc.tuition_fee_per_session) - COALESCE(p.total_paid_success, 0)
    END AS remaining_amount
FROM STUDY_CLASS sc
LEFT JOIN completed c
    ON c.class_id = sc.class_id
LEFT JOIN invoice_totals i
    ON i.class_id = sc.class_id
LEFT JOIN payment_totals p
    ON p.class_id = sc.class_id
WHERE sc.class_id = @class_id;
GO

CREATE PROCEDURE SP_ASSIGN_TUTOR_TO_REQUEST
    @request_id INT,
    @tutor_id INT,
    @staff_id INT = NULL,
    @note NVARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @request_status VARCHAR(20);
    DECLARE @request_subject_id INT;
    DECLARE @assignment_id INT;

    BEGIN TRANSACTION;

    SELECT
        @request_status = lr.status,
        @request_subject_id = lr.subject_id
    FROM LEARNING_REQUEST lr WITH (UPDLOCK, HOLDLOCK)
    WHERE lr.request_id = @request_id;

    IF @request_status IS NULL
        THROW 50000, 'Learning request not found', 1;

    IF @request_status = 'CANCELED'
        THROW 50000, 'Learning request is canceled', 1;

    IF @request_status <> 'PENDING'
        THROW 50000, 'Learning request is not pending', 1;

    IF EXISTS (
        SELECT 1
        FROM TUTOR_ASSIGNMENT ta WITH (UPDLOCK, HOLDLOCK)
        WHERE ta.request_id = @request_id
          AND ta.status = 'ASSIGNED'
    )
        THROW 50000, 'Learning request already has an active assignment', 1;

    IF NOT EXISTS (
        SELECT 1
        FROM TUTOR t
        WHERE t.tutor_id = @tutor_id
          AND t.status = 'ACTIVE'
    )
        THROW 50000, 'Tutor must be ACTIVE to receive an assignment', 1;

    IF NOT EXISTS (
        SELECT 1
        FROM TUTOR_CAPABILITY tc
        WHERE tc.tutor_id = @tutor_id
          AND tc.subject_id = @request_subject_id
    )
        THROW 50000, 'Tutor does not have capability for requested subject', 1;

    INSERT INTO TUTOR_ASSIGNMENT (
        request_id,
        tutor_id,
        staff_id,
        status,
        note
    )
    VALUES (
        @request_id,
        @tutor_id,
        @staff_id,
        'ASSIGNED',
        @note
    );

    SET @assignment_id = CAST(SCOPE_IDENTITY() AS INT);

    UPDATE LEARNING_REQUEST
    SET
        status = 'ASSIGNED',
        updated_at = SYSUTCDATETIME()
    WHERE request_id = @request_id;

    COMMIT TRANSACTION;

    SELECT
        ta.assignment_id,
        ta.request_id,
        ta.tutor_id,
        ta.staff_id,
        ta.assigned_at,
        ta.status,
        ta.note,
        ta.created_at,
        ta.updated_at
    FROM TUTOR_ASSIGNMENT ta
    WHERE ta.assignment_id = @assignment_id;
END;
GO

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

    DECLARE @resolved_invoice_id INT = @invoice_id;
    DECLARE @tuition_fee_per_session DECIMAL(18,2);
    DECLARE @completed_sessions INT;
    DECLARE @amount_due DECIMAL(18,2);
    DECLARE @payment_id INT;

    IF @amount_paid IS NULL OR @amount_paid <= 0
        THROW 50000, 'Payment amount must be greater than zero', 1;

    IF @status NOT IN ('SUCCESS', 'CANCELED', 'REFUNDED')
        THROW 50000, 'Invalid payment status', 1;

    BEGIN TRANSACTION;

    IF @resolved_invoice_id IS NULL
    BEGIN
        IF @class_id IS NULL
            THROW 50000, 'invoice_id or class_id is required', 1;

        IF @period_start IS NULL OR @period_end IS NULL
            THROW 50000, 'period_start and period_end are required when invoice_id is missing', 1;

        IF @period_end < @period_start
            THROW 50000, 'period_end must be on or after period_start', 1;

        SELECT
            @resolved_invoice_id = invoice_id
        FROM TUITION_INVOICE
        WHERE class_id = @class_id
          AND period_start = @period_start
          AND period_end = @period_end;

        IF @resolved_invoice_id IS NULL
        BEGIN
            SELECT
                @tuition_fee_per_session = tuition_fee_per_session
            FROM STUDY_CLASS
            WHERE class_id = @class_id;

            IF @tuition_fee_per_session IS NULL
                THROW 50000, 'Class not found', 1;

            SELECT
                @completed_sessions = COUNT(*)
            FROM LESSON_SESSION
            WHERE class_id = @class_id
              AND status = 'COMPLETED'
              AND lesson_date BETWEEN @period_start AND @period_end;

            SET @completed_sessions = COALESCE(@completed_sessions, 0);
            SET @amount_due = @completed_sessions * @tuition_fee_per_session;

            INSERT INTO TUITION_INVOICE (
                class_id,
                period_start,
                period_end,
                completed_sessions,
                tuition_fee_per_session,
                amount_due,
                amount_paid,
                status
            )
            VALUES (
                @class_id,
                @period_start,
                @period_end,
                @completed_sessions,
                @tuition_fee_per_session,
                @amount_due,
                0,
                'UNPAID'
            );

            SET @resolved_invoice_id = CAST(SCOPE_IDENTITY() AS INT);
        END
    END

    IF NOT EXISTS (SELECT 1 FROM TUITION_INVOICE WHERE invoice_id = @resolved_invoice_id)
        THROW 50000, 'Invoice not found', 1;

    IF EXISTS (
        SELECT 1
        FROM TUITION_INVOICE
        WHERE invoice_id = @resolved_invoice_id
          AND status = 'CANCELED'
    )
        THROW 50000, 'Cannot record payment for a canceled invoice', 1;

    IF @status = 'SUCCESS' AND dbo.FN_INVOICE_REMAINING_AMOUNT(@resolved_invoice_id) < @amount_paid
        THROW 50000, 'Payment amount exceeds invoice remaining amount', 1;

    INSERT INTO TUITION_PAYMENT (
        invoice_id,
        staff_id,
        payment_date,
        amount_paid,
        payment_method,
        note,
        status
    )
    VALUES (
        @resolved_invoice_id,
        @staff_id,
        COALESCE(@payment_date, SYSUTCDATETIME()),
        @amount_paid,
        @payment_method,
        @note,
        @status
    );

    SET @payment_id = CAST(SCOPE_IDENTITY() AS INT);

    COMMIT TRANSACTION;

    SELECT @payment_id AS payment_id, @resolved_invoice_id AS invoice_id;
END;
GO

/* =========================================================
   6. VIEWS FOR BACKEND/FRONTEND DISPLAY
   ========================================================= */

CREATE VIEW VW_LEARNING_REQUEST_DETAIL
AS
SELECT
    lr.request_id,
    lr.student_id,
    st.full_name AS student_name,
    st.phone AS student_phone,
    st.contact_email AS student_email,
    lr.subject_id,
    su.subject_name,
    su.grade_level AS subject_grade_level,
    su.subject_group,
    lr.requested_level,
    lr.learning_goal,
    lr.preferred_area,
    lr.preferred_mode,
    lr.preferred_schedule,
    lr.expected_fee,
    lr.status,
    lr.created_at,
    lr.updated_at,
    latest_assignment.assignment_id,
    latest_assignment.assignment_status,
    latest_assignment.assignment_assigned_at,
    latest_assignment.assignment_note,
    latest_assignment.assignment_staff_id,
    latest_assignment.assignment_tutor_id,
    latest_assignment.class_id,
    latest_assignment.assignment_staff_name,
    latest_assignment.assigned_tutor_name
FROM LEARNING_REQUEST lr
JOIN STUDENT st
    ON st.student_id = lr.student_id
JOIN SUBJECT su
    ON su.subject_id = lr.subject_id
OUTER APPLY (
    SELECT TOP 1
        ta.assignment_id,
        ta.status AS assignment_status,
        ta.assigned_at AS assignment_assigned_at,
        ta.note AS assignment_note,
        ta.staff_id AS assignment_staff_id,
        ta.tutor_id AS assignment_tutor_id,
        sc.class_id,
        sf.full_name AS assignment_staff_name,
        tu.full_name AS assigned_tutor_name
    FROM TUTOR_ASSIGNMENT ta
    LEFT JOIN STUDY_CLASS sc
        ON sc.assignment_id = ta.assignment_id
    LEFT JOIN STAFF sf
        ON sf.staff_id = ta.staff_id
    LEFT JOIN TUTOR tu
        ON tu.tutor_id = ta.tutor_id
    WHERE ta.request_id = lr.request_id
    ORDER BY
        CASE WHEN ta.status = 'ASSIGNED' THEN 0 ELSE 1 END,
        ta.assigned_at DESC,
        ta.assignment_id DESC
) latest_assignment;
GO

CREATE VIEW VW_LESSON_SESSION_DETAIL
AS
SELECT
    ls.session_id,
    ls.class_id,
    sc.class_code,
    ls.schedule_id,
    ls.session_number,
    ls.lesson_date,
    ls.start_time,
    ls.end_time,
    ls.status,
    ls.content_note,
    ls.created_at,
    ls.updated_at,
    cs.day_of_week AS schedule_day_of_week,
    cs.start_time AS schedule_start_time,
    cs.end_time AS schedule_end_time,
    cs.effective_from AS schedule_effective_from,
    cs.effective_to AS schedule_effective_to,
    lr.request_id,
    lr.student_id,
    st.full_name AS student_name,
    su.subject_id,
    su.subject_name,
    su.grade_level AS subject_grade_level,
    ta.tutor_id,
    tu.full_name AS tutor_name,
    CONCAT(su.subject_name, COALESCE(N' - ' + su.grade_level, N'')) AS class_label
FROM LESSON_SESSION ls
JOIN STUDY_CLASS sc
    ON sc.class_id = ls.class_id
JOIN TUTOR_ASSIGNMENT ta
    ON ta.assignment_id = sc.assignment_id
JOIN LEARNING_REQUEST lr
    ON lr.request_id = ta.request_id
JOIN STUDENT st
    ON st.student_id = lr.student_id
JOIN SUBJECT su
    ON su.subject_id = lr.subject_id
JOIN TUTOR tu
    ON tu.tutor_id = ta.tutor_id
LEFT JOIN CLASS_SCHEDULE cs
    ON cs.schedule_id = ls.schedule_id;
GO

CREATE VIEW VW_INVOICE_DETAIL
AS
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
JOIN STUDY_CLASS sc
    ON sc.class_id = ti.class_id
JOIN TUTOR_ASSIGNMENT ta
    ON ta.assignment_id = sc.assignment_id
JOIN LEARNING_REQUEST lr
    ON lr.request_id = ta.request_id
JOIN STUDENT st
    ON st.student_id = lr.student_id
JOIN SUBJECT su
    ON su.subject_id = lr.subject_id
JOIN TUTOR tu
    ON tu.tutor_id = ta.tutor_id;
GO

CREATE VIEW VW_PAYMENT_DETAIL
AS
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
JOIN TUITION_INVOICE ti
    ON ti.invoice_id = tp.invoice_id
JOIN STUDY_CLASS sc
    ON sc.class_id = ti.class_id
JOIN TUTOR_ASSIGNMENT ta
    ON ta.assignment_id = sc.assignment_id
JOIN LEARNING_REQUEST lr
    ON lr.request_id = ta.request_id
JOIN STUDENT st
    ON st.student_id = lr.student_id
JOIN SUBJECT su
    ON su.subject_id = lr.subject_id
LEFT JOIN STAFF sf
    ON sf.staff_id = tp.staff_id;
GO

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

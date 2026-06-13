SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

/*
Query 1: Dashboard summary
*/
SELECT
    (SELECT COUNT(*) FROM STUDENT WHERE status = 'ACTIVE') AS total_active_students,
    (SELECT COUNT(*) FROM TUTOR WHERE status = 'ACTIVE') AS total_active_tutors,
    (SELECT COUNT(*) FROM LEARNING_REQUEST WHERE status = 'PENDING') AS pending_learning_requests;
GO

/*
Query 2: Class list using the normalized view
*/
SELECT
    class_id,
    class_code,
    student_name,
    tutor_name,
    subject_name,
    requested_level,
    teaching_mode,
    location,
    class_status
FROM VW_STUDY_CLASS_DETAIL
ORDER BY class_id DESC;
GO

/*
Query 3: Tutor workload by active class count
*/
SELECT
    t.tutor_id,
    t.full_name,
    COUNT(sc.class_id) AS active_class_count
FROM TUTOR t
LEFT JOIN TUTOR_ASSIGNMENT ta
    ON ta.tutor_id = t.tutor_id
    AND ta.status = 'ASSIGNED'
LEFT JOIN STUDY_CLASS sc
    ON sc.assignment_id = ta.assignment_id
    AND sc.status IN ('ACTIVE', 'PAUSED')
GROUP BY t.tutor_id, t.full_name
ORDER BY active_class_count DESC, t.tutor_id ASC;
GO

/*
Query 4: Realtime tuition summary by class
*/
SELECT
    sc.class_id,
    sc.class_code,
    SUM(CASE WHEN ls.status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_sessions,
    sc.tuition_fee_per_session,
    SUM(CASE WHEN ls.status = 'COMPLETED' THEN 1 ELSE 0 END) * sc.tuition_fee_per_session AS realtime_total_fee
FROM STUDY_CLASS sc
LEFT JOIN LESSON_SESSION ls
    ON ls.class_id = sc.class_id
GROUP BY sc.class_id, sc.class_code, sc.tuition_fee_per_session
ORDER BY sc.class_id DESC;
GO

/*
Query 5: Invoice and payment status by class period
*/
SELECT
    ti.invoice_id,
    ti.class_id,
    ti.period_start,
    ti.period_end,
    ti.amount_due,
    ti.amount_paid,
    ti.status AS invoice_status,
    COUNT(tp.payment_id) AS payment_count
FROM TUITION_INVOICE ti
LEFT JOIN TUITION_PAYMENT tp
    ON tp.invoice_id = ti.invoice_id
GROUP BY
    ti.invoice_id,
    ti.class_id,
    ti.period_start,
    ti.period_end,
    ti.amount_due,
    ti.amount_paid,
    ti.status
ORDER BY ti.invoice_id DESC;
GO

/*
Query 6: Revenue received by payment month
*/
SELECT
    YEAR(payment_date) AS payment_year,
    MONTH(payment_date) AS payment_month,
    SUM(CASE WHEN status = 'SUCCESS' THEN amount_paid ELSE 0 END) AS revenue_received
FROM TUITION_PAYMENT
GROUP BY YEAR(payment_date), MONTH(payment_date)
ORDER BY payment_year DESC, payment_month DESC;
GO

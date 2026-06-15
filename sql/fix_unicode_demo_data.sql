USE TutorCenterDB;
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

/*
  Fix/demo refresh script for Vietnamese Unicode data.
  - xóa dữ liệu test tạm thời tạo trong quá trình smoke test
  - chuẩn hóa lại dữ liệu demo cốt lõi sang tiếng Việt có dấu
*/

DELETE FROM TUITION_PAYMENT
WHERE invoice_id IN (
    SELECT i.invoice_id
    FROM TUITION_INVOICE i
    JOIN STUDY_CLASS sc ON sc.class_id = i.class_id
    JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
    JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
    JOIN STUDENT s ON s.student_id = lr.student_id
    WHERE s.contact_email LIKE N'%@example.com'
)
OR invoice_id IN (
    SELECT i.invoice_id
    FROM TUITION_INVOICE i
    JOIN STUDY_CLASS sc ON sc.class_id = i.class_id
    JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
    JOIN TUTOR t ON t.tutor_id = ta.tutor_id
    WHERE t.contact_email LIKE N'%@example.com'
);
GO

DELETE FROM TUITION_INVOICE
WHERE class_id IN (
    SELECT sc.class_id
    FROM STUDY_CLASS sc
    JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
    JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
    JOIN STUDENT s ON s.student_id = lr.student_id
    WHERE s.contact_email LIKE N'%@example.com'
)
OR class_id IN (
    SELECT sc.class_id
    FROM STUDY_CLASS sc
    JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
    JOIN TUTOR t ON t.tutor_id = ta.tutor_id
    WHERE t.contact_email LIKE N'%@example.com'
);
GO

DELETE FROM LESSON_SESSION
WHERE class_id IN (
    SELECT sc.class_id
    FROM STUDY_CLASS sc
    JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
    JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
    JOIN STUDENT s ON s.student_id = lr.student_id
    WHERE s.contact_email LIKE N'%@example.com'
)
OR class_id IN (
    SELECT sc.class_id
    FROM STUDY_CLASS sc
    JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
    JOIN TUTOR t ON t.tutor_id = ta.tutor_id
    WHERE t.contact_email LIKE N'%@example.com'
);
GO

DELETE FROM CLASS_SCHEDULE
WHERE class_id IN (
    SELECT sc.class_id
    FROM STUDY_CLASS sc
    JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
    JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
    JOIN STUDENT s ON s.student_id = lr.student_id
    WHERE s.contact_email LIKE N'%@example.com'
)
OR class_id IN (
    SELECT sc.class_id
    FROM STUDY_CLASS sc
    JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
    JOIN TUTOR t ON t.tutor_id = ta.tutor_id
    WHERE t.contact_email LIKE N'%@example.com'
);
GO

DELETE FROM STUDY_CLASS
WHERE assignment_id IN (
    SELECT ta.assignment_id
    FROM TUTOR_ASSIGNMENT ta
    JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
    JOIN STUDENT s ON s.student_id = lr.student_id
    WHERE s.contact_email LIKE N'%@example.com'
)
OR assignment_id IN (
    SELECT ta.assignment_id
    FROM TUTOR_ASSIGNMENT ta
    JOIN TUTOR t ON t.tutor_id = ta.tutor_id
    WHERE t.contact_email LIKE N'%@example.com'
);
GO

DELETE FROM TUTOR_ASSIGNMENT
WHERE request_id IN (
    SELECT request_id FROM LEARNING_REQUEST
    WHERE student_id IN (SELECT student_id FROM STUDENT WHERE contact_email LIKE N'%@example.com')
)
OR tutor_id IN (
    SELECT tutor_id FROM TUTOR WHERE contact_email LIKE N'%@example.com'
);
GO

DELETE FROM LEARNING_REQUEST
WHERE student_id IN (
    SELECT student_id FROM STUDENT WHERE contact_email LIKE N'%@example.com'
);
GO

DELETE FROM TUTOR_CAPABILITY
WHERE tutor_id IN (
    SELECT tutor_id FROM TUTOR WHERE contact_email LIKE N'%@example.com'
);
GO

DELETE FROM TUTOR_AVAILABILITY
WHERE tutor_id IN (
    SELECT tutor_id FROM TUTOR WHERE contact_email LIKE N'%@example.com'
);
GO

DELETE FROM STUDENT WHERE contact_email LIKE N'%@example.com';
DELETE FROM TUTOR WHERE contact_email LIKE N'%@example.com';
DELETE FROM USER_ACCOUNT WHERE email LIKE N'%@example.com';
GO

UPDATE STAFF
SET
    full_name = N'Trần Thu Hà',
    position = N'Điều phối viên',
    updated_at = SYSUTCDATETIME()
WHERE contact_email = N'staff1@smarttutor.local';
GO

UPDATE STUDENT
SET
    full_name = N'Nguyễn Khánh An',
    address = N'Cầu Giấy, Hà Nội',
    area = N'Cầu Giấy',
    current_level = N'Lớp 12',
    grade_level = N'Lớp 12',
    updated_at = SYSUTCDATETIME()
WHERE contact_email = N'an.nguyen@student.local';

UPDATE STUDENT
SET
    full_name = N'Trần Đức Minh',
    address = N'Hà Đông, Hà Nội',
    area = N'Hà Đông',
    current_level = N'Lớp 10',
    grade_level = N'Lớp 10',
    updated_at = SYSUTCDATETIME()
WHERE contact_email = N'minh.tran@student.local';
GO

UPDATE TUTOR
SET
    full_name = N'Ngô Quốc Bảo',
    university = N'Đại học Sư phạm Hà Nội',
    major = N'Sư phạm Toán',
    area = N'Cầu Giấy',
    updated_at = SYSUTCDATETIME()
WHERE contact_email = N'bao.ngo@tutor.local';

UPDATE TUTOR
SET
    full_name = N'Phạm Ngọc Linh',
    university = N'Đại học Quốc gia Hà Nội',
    major = N'Vật lý',
    area = N'Hà Đông',
    updated_at = SYSUTCDATETIME()
WHERE contact_email = N'linh.pham@tutor.local';
GO

UPDATE SUBJECT
SET subject_name = N'Toán', grade_level = N'Lớp 12', description = N'Luyện thi THPT môn Toán', updated_at = SYSUTCDATETIME()
WHERE subject_id = 1;

UPDATE SUBJECT
SET subject_name = N'Vật lý', grade_level = N'Lớp 10', description = N'Cơ bản và nâng cao', updated_at = SYSUTCDATETIME()
WHERE subject_id = 2;

UPDATE SUBJECT
SET subject_name = N'Tiếng Anh', grade_level = N'Lớp 8', description = N'Giao tiếp và ngữ pháp', updated_at = SYSUTCDATETIME()
WHERE subject_id = 3;
GO

UPDATE TUTOR_CAPABILITY
SET teaching_level = N'Lớp 12', note = N'Chuyên luyện thi', updated_at = SYSUTCDATETIME()
WHERE capability_id = 1;

UPDATE TUTOR_CAPABILITY
SET teaching_level = N'Lớp 10', note = N'Dạy offline tại Hà Đông', updated_at = SYSUTCDATETIME()
WHERE capability_id = 2;
GO

UPDATE TUTOR_AVAILABILITY
SET area = N'Cầu Giấy', updated_at = SYSUTCDATETIME()
WHERE availability_id IN (1, 2);

UPDATE TUTOR_AVAILABILITY
SET area = N'Hà Đông', updated_at = SYSUTCDATETIME()
WHERE availability_id = 3;
GO

UPDATE LEARNING_REQUEST
SET
    requested_level = N'Lớp 12',
    learning_goal = N'Ôn thi đại học khối A',
    preferred_area = N'Cầu Giấy',
    preferred_schedule = N'T2, T4 tối',
    updated_at = SYSUTCDATETIME()
WHERE request_id = 1;

UPDATE LEARNING_REQUEST
SET
    requested_level = N'Lớp 10',
    learning_goal = N'Củng cố nền tảng Vật lý',
    preferred_area = N'Hà Đông',
    preferred_schedule = N'T3, T5 tối',
    updated_at = SYSUTCDATETIME()
WHERE request_id = 2;
GO

UPDATE TUTOR_ASSIGNMENT
SET note = N'Phù hợp lịch và khu vực', updated_at = SYSUTCDATETIME()
WHERE assignment_id = 1;
GO

UPDATE STUDY_CLASS
SET location = N'Nhà học viên - Cầu Giấy', updated_at = SYSUTCDATETIME()
WHERE class_id = 1;
GO

UPDATE CLASS_SCHEDULE
SET note = N'Ca tối thứ 2', updated_at = SYSUTCDATETIME()
WHERE schedule_id = 1;

UPDATE CLASS_SCHEDULE
SET note = N'Ca tối thứ 4', updated_at = SYSUTCDATETIME()
WHERE schedule_id = 2;
GO

UPDATE LESSON_SESSION
SET content_note = N'Hàm số và đồ thị', updated_at = SYSUTCDATETIME()
WHERE session_id = 1;

UPDATE LESSON_SESSION
SET content_note = N'Đạo hàm cơ bản', updated_at = SYSUTCDATETIME()
WHERE session_id = 2;
GO

UPDATE TUITION_PAYMENT
SET note = N'Thanh toán đợt 1', updated_at = SYSUTCDATETIME()
WHERE payment_id = 1;
GO

PRINT N'Unicode demo data fix completed.';
GO

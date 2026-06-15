USE TutorCenterDB;
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

/* Minimal backend smoke-test seed.
   Assumes `sql/schema.sql` has already been executed. */

DELETE FROM TUITION_PAYMENT;
DELETE FROM TUITION_INVOICE;
DELETE FROM LESSON_SESSION;
DELETE FROM CLASS_SCHEDULE;
DELETE FROM STUDY_CLASS;
DELETE FROM TUTOR_ASSIGNMENT;
DELETE FROM LEARNING_REQUEST;
DELETE FROM TUTOR_CAPABILITY;
DELETE FROM TUTOR_AVAILABILITY;
DELETE FROM TUTOR;
DELETE FROM STUDENT;
DELETE FROM STAFF;
DELETE FROM SUBJECT;
DELETE FROM USER_ACCOUNT;
GO

SET IDENTITY_INSERT USER_ACCOUNT ON;
INSERT INTO USER_ACCOUNT (account_id, email, username, password_hash, role, status)
VALUES
    (1, N'staff1@smarttutor.local', N'staff1', N'10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6', 'STAFF', 'ACTIVE'),
    (2, N'an.nguyen@student.local', N'an.nguyen', N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),
    (3, N'bao.ngo@tutor.local', N'bao.ngo', N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE');
SET IDENTITY_INSERT USER_ACCOUNT OFF;
GO

SET IDENTITY_INSERT STAFF ON;
INSERT INTO STAFF (staff_id, account_id, full_name, phone, contact_email, position, status)
VALUES
    (1, 1, N'Trần Thu Hà', N'0901000001', N'staff1@smarttutor.local', N'Điều phối viên', 'ACTIVE');
SET IDENTITY_INSERT STAFF OFF;
GO

SET IDENTITY_INSERT STUDENT ON;
INSERT INTO STUDENT (student_id, account_id, full_name, phone, contact_email, address, area, current_level, grade_level, status)
VALUES
    (1, 2, N'Nguyễn Khánh An', N'0987000001', N'an.nguyen@student.local', N'Cầu Giấy, Hà Nội', N'Cầu Giấy', N'Lớp 12', N'Lớp 12', 'ACTIVE');
SET IDENTITY_INSERT STUDENT OFF;
GO

SET IDENTITY_INSERT TUTOR ON;
INSERT INTO TUTOR (tutor_id, account_id, full_name, phone, contact_email, university, major, experience_years, area, status)
VALUES
    (1, 3, N'Ngô Quốc Bảo', N'0903000001', N'bao.ngo@tutor.local', N'Đại học Sư phạm Hà Nội', N'Sư phạm Toán', 5, N'Cầu Giấy', 'ACTIVE');
SET IDENTITY_INSERT TUTOR OFF;
GO

SET IDENTITY_INSERT SUBJECT ON;
INSERT INTO SUBJECT (subject_id, subject_name, subject_group, grade_level, description, status)
VALUES
    (1, N'Toán', N'STEM', N'Lớp 12', N'Luyện thi THPT môn Toán', 'ACTIVE');
SET IDENTITY_INSERT SUBJECT OFF;
GO

SET IDENTITY_INSERT TUTOR_CAPABILITY ON;
INSERT INTO TUTOR_CAPABILITY (capability_id, tutor_id, subject_id, teaching_level, years_experience, note)
VALUES
    (1, 1, 1, N'Lớp 12', 5, N'Chuyên luyện thi');
SET IDENTITY_INSERT TUTOR_CAPABILITY OFF;
GO

SET IDENTITY_INSERT LEARNING_REQUEST ON;
INSERT INTO LEARNING_REQUEST (
    request_id, student_id, subject_id, requested_level, learning_goal,
    preferred_area, preferred_mode, preferred_schedule, expected_fee, status
)
VALUES
    (1, 1, 1, N'Lớp 12', N'Ôn thi đại học khối A', N'Cầu Giấy', 'OFFLINE', N'T2, T4 tối', 250000, 'ASSIGNED');
SET IDENTITY_INSERT LEARNING_REQUEST OFF;
GO

SET IDENTITY_INSERT TUTOR_ASSIGNMENT ON;
INSERT INTO TUTOR_ASSIGNMENT (assignment_id, request_id, tutor_id, staff_id, assigned_at, status, note)
VALUES
    (1, 1, 1, 1, SYSUTCDATETIME(), 'ASSIGNED', N'Phù hợp lịch và khu vực');
SET IDENTITY_INSERT TUTOR_ASSIGNMENT OFF;
GO

SET IDENTITY_INSERT STUDY_CLASS ON;
INSERT INTO STUDY_CLASS (
    class_id, assignment_id, class_code, tuition_fee_per_session, teaching_mode,
    location, start_date, end_date, status
)
VALUES
    (1, 1, N'CLS-0001', 250000, 'OFFLINE', N'Nhà học viên - Cầu Giấy', '2026-06-01', NULL, 'ACTIVE');
SET IDENTITY_INSERT STUDY_CLASS OFF;
GO

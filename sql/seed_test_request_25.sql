-- ============================================================
-- Test seed: gia sư rảnh cho learning request #25
-- Request #25:
--   subject_id=9 (Tieng Anh Lớp 11)
--   preferred_schedule = 'T3 18:30-20:30'  -> T3 = day_of_week=2
--   preferred_mode     = 'OFFLINE'
--   preferred_area     = 'Cầu giấy'
--   requested_level    = '2 năm kinh nghiệm trở lên'
-- ============================================================
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
GO

-- 1) USER_ACCOUNT cho 2 tutor mới
-- password = 'tutor123' -> 537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf
SET IDENTITY_INSERT USER_ACCOUNT ON;
INSERT INTO USER_ACCOUNT (account_id, email, username, password_hash, role, status)
VALUES
    (901, N'tutor901@smarttutor.local', N'tutor901', N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE'),
    (902, N'tutor902@smarttutor.local', N'tutor902', N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE');
SET IDENTITY_INSERT USER_ACCOUNT OFF;
GO

-- 2) TUTOR (id 901, 902). account_id khớp với USER_ACCOUNT vừa tạo.
SET IDENTITY_INSERT TUTOR ON;
INSERT INTO TUTOR (tutor_id, account_id, full_name, phone, contact_email, university, major, experience_years, area, status)
VALUES
    (901, 901, N'Lê Minh Anh', N'0903900001', N'tutor901@smarttutor.local',
     N'Đại học Hà Nội', N'Sư phạm Tiếng Anh', 5, N'Cầu giấy', 'ACTIVE'),
    (902, 902, N'Phạm Quốc Đạt', N'0903900002', N'tutor902@smarttutor.local',
     N'Đại học Ngoại ngữ', N'Sư phạm Tiếng Anh', 8, N'Cầu Giấy, Hà Nội', 'ACTIVE');
SET IDENTITY_INSERT TUTOR OFF;
GO

-- 3) TUTOR_CAPABILITY: dạy được "Tiếng Anh Lớp 11"
-- subject_id=9 (seed) và subject_id=20 (UI) đều có cùng effective subject
INSERT INTO TUTOR_CAPABILITY (tutor_id, subject_id, teaching_level, years_experience, note)
VALUES
    (901, 9,  N'Lớp 11', 5, N'Luyện thi IELTS + giao tiếp'),
    (902, 9,  N'Lớp 11', 8, N'5 năm luyện thi vào 10 và ĐH');
GO

-- 4) TUTOR_AVAILABILITY: lịch OFFLINE T3 18:30-20:30 (đúng lịch request)
-- day_of_week 2 = T3, OFFLINE
INSERT INTO TUTOR_AVAILABILITY (tutor_id, day_of_week, start_time, end_time, teaching_mode, area, status)
VALUES
    (901, 2, '18:30:00', '20:30:00', 'OFFLINE', N'Cầu giấy',    'AVAILABLE'),
    (902, 2, '18:30:00', '20:30:00', 'OFFLINE', N'Cầu Giấy, Hà Nội', 'AVAILABLE');
GO

PRINT N'Test seed for /learning-requests/25/suggested-tutors inserted.';
PRINT N'Tutors 901, 902 are ACTIVE, có capability Tiếng Anh Lớp 11, có lịch OFFLINE T3 18:30-20:30, KHÔNG có assignment nào.';
USE TutorCenterDB;
GO

SET ANSI_NULLS ON;
GO

SET QUOTED_IDENTIFIER ON;
GO

/*
    Full demo dataset for SmartTutor Platform.
    Scope:
    - Multiple staff, students, tutors
    - Multiple subjects and tutor capabilities
    - Rich request pipeline:
      LEARNING_REQUEST -> TUTOR_ASSIGNMENT -> STUDY_CLASS
    - Enough schedules, sessions, invoices, and payments for end-to-end UI/API testing

    Default demo passwords by role:
    - STAFF   : staff123
    - STUDENT : student123
    - TUTOR   : tutor123

    Important:
    - Run this file with UTF-8 input.
    - Recommended:
      powershell -ExecutionPolicy Bypass -File .\sql\reset_demo_utf8.ps1 -Seed sample
*/

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

/* Password hashes
   staff123   -> 10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6
   student123 -> 703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b
   tutor123   -> 537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf
*/

SET IDENTITY_INSERT USER_ACCOUNT ON;
INSERT INTO USER_ACCOUNT (account_id, email, username, password_hash, role, status)
VALUES
    (1,  N'staff1@smarttutor.local',       N'staff1',        N'10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6', 'STAFF',   'ACTIVE'),
    (2,  N'staff2@smarttutor.local',       N'staff2',        N'10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6', 'STAFF',   'ACTIVE'),
    (3,  N'staff3@smarttutor.local',       N'staff3',        N'10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6', 'STAFF',   'ACTIVE'),
    (4,  N'lam.pham@student.local',        N'lam.pham',      N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),
    (5,  N'linh.nguyen@student.local',     N'linh.nguyen',   N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),
    (6,  N'minh.tran@student.local',       N'minh.tran',     N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),
    (7,  N'an.do@student.local',           N'an.do',         N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),
    (8,  N'hoa.le@student.local',          N'hoa.le',        N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),
    (9,  N'khanh.vo@student.local',        N'khanh.vo',      N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),
    (10, N'phuc.bui@student.local',        N'phuc.bui',      N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'INACTIVE'),
    (11, N'bao.ngo@tutor.local',           N'bao.ngo',       N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR',   'ACTIVE'),
    (12, N'trang.pham@tutor.local',        N'trang.pham',    N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR',   'ACTIVE'),
    (13, N'vu.hoang@tutor.local',          N'vu.hoang',      N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR',   'ACTIVE'),
    (14, N'mai.nguyen@tutor.local',        N'mai.nguyen',    N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR',   'ACTIVE'),
    (15, N'linh.do@tutor.local',           N'linh.do',       N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR',   'ACTIVE'),
    (16, N'quan.trinh@tutor.local',        N'quan.trinh',    N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR',   'ACTIVE'),
    (17, N'anh.vu@tutor.local',            N'anh.vu',        N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR',   'INACTIVE');
SET IDENTITY_INSERT USER_ACCOUNT OFF;
GO

SET IDENTITY_INSERT STAFF ON;
INSERT INTO STAFF (staff_id, account_id, full_name, phone, contact_email, position, status)
VALUES
    (1, 1, N'Trần Thu Hà',       N'0901000001', N'staff1@smarttutor.local', N'Điều phối viên',      'ACTIVE'),
    (2, 2, N'Lê Minh Quân',      N'0901000002', N'staff2@smarttutor.local', N'Tư vấn tuyển sinh',   'ACTIVE'),
    (3, 3, N'Nguyễn Hoài Nam',   N'0901000003', N'staff3@smarttutor.local', N'Kế toán học phí',     'ACTIVE');
SET IDENTITY_INSERT STAFF OFF;
GO

SET IDENTITY_INSERT STUDENT ON;
INSERT INTO STUDENT (student_id, account_id, full_name, phone, contact_email, address, area, current_level, grade_level, status)
VALUES
    (1,  4,  N'Phạm Gia Lâm',      N'0987000001', N'lam.pham@student.local',   N'Cầu Giấy, Hà Nội',             N'Cầu Giấy',      N'Lớp 12', N'Lớp 12', 'ACTIVE'),
    (2,  5,  N'Nguyễn Ngọc Linh',  N'0987000002', N'linh.nguyen@student.local',N'Đống Đa, Hà Nội',             N'Đống Đa',       N'Lớp 11', N'Lớp 11', 'ACTIVE'),
    (3,  6,  N'Trần Đức Minh',     N'0987000003', N'minh.tran@student.local',  N'Hà Đông, Hà Nội',             N'Hà Đông',       N'Lớp 10', N'Lớp 10', 'ACTIVE'),
    (4,  7,  N'Đỗ Hoàng An',       N'0987000004', N'an.do@student.local',      N'Thanh Xuân, Hà Nội',         N'Thanh Xuân',    N'Lớp 9',  N'Lớp 9',  'ACTIVE'),
    (5,  8,  N'Lê Thu Hòa',        N'0987000005', N'hoa.le@student.local',     N'Nam Từ Liêm, Hà Nội',        N'Nam Từ Liêm',   N'Lớp 8',  N'Lớp 8',  'ACTIVE'),
    (6,  9,  N'Võ Gia Khánh',      N'0987000006', N'khanh.vo@student.local',   N'Long Biên, Hà Nội',          N'Long Biên',     N'Lớp 7',  N'Lớp 7',  'ACTIVE'),
    (7, 10,  N'Bùi Hồng Phúc',     N'0987000007', N'phuc.bui@student.local',   N'Ba Đình, Hà Nội',            N'Ba Đình',       N'Lớp 6',  N'Lớp 6',  'INACTIVE');
SET IDENTITY_INSERT STUDENT OFF;
GO

SET IDENTITY_INSERT TUTOR ON;
INSERT INTO TUTOR (tutor_id, account_id, full_name, phone, contact_email, university, major, experience_years, area, status)
VALUES
    (1, 11, N'Ngô Quốc Bảo',       N'0903000001', N'bao.ngo@tutor.local',    N'Đại học Sư phạm Hà Nội',      N'Sư phạm Toán',        5, N'Cầu Giấy, Hà Nội',   'ACTIVE'),
    (2, 12, N'Phạm Khánh Trang',   N'0903000002', N'trang.pham@tutor.local', N'Đại học Quốc gia Hà Nội',     N'Ngôn ngữ Anh',        4, N'Đống Đa, Hà Nội',    'ACTIVE'),
    (3, 13, N'Hoàng Đức Vũ',       N'0903000003', N'vu.hoang@tutor.local',   N'Đại học Bách khoa Hà Nội',    N'Vật lý kỹ thuật',     3, N'Hà Đông, Hà Nội',    'ACTIVE'),
    (4, 14, N'Nguyễn Thu Mai',     N'0903000004', N'mai.nguyen@tutor.local', N'Đại học Sư phạm Hà Nội 2',    N'Ngữ văn',             6, N'Thanh Xuân, Hà Nội', 'ACTIVE'),
    (5, 15, N'Đỗ Mỹ Linh',         N'0903000005', N'linh.do@tutor.local',    N'Đại học Khoa học Tự nhiên',   N'Hóa học',             2, N'Nam Từ Liêm',        'PAUSED'),
    (6, 16, N'Trịnh Hải Quân',     N'0903000006', N'quan.trinh@tutor.local', N'Đại học Ngoại ngữ',           N'Sư phạm Tiếng Anh',   7, N'Long Biên',          'ACTIVE'),
    (7, 17, N'Vũ Phương Anh',      N'0903000007', N'anh.vu@tutor.local',     N'Đại học Sư phạm Hà Nội',      N'Sinh học',            1, N'Ba Đình',            'INACTIVE');
SET IDENTITY_INSERT TUTOR OFF;
GO

SET IDENTITY_INSERT SUBJECT ON;
INSERT INTO SUBJECT (subject_id, subject_name, subject_group, grade_level, description, status)
VALUES
    (1,  N'Toán',        N'STEM',      N'Lớp 12', N'Luyện thi THPT Quốc gia môn Toán',         'ACTIVE'),
    (2,  N'Toán',        N'STEM',      N'Lớp 10', N'Bổ trợ Toán trung học phổ thông',          'ACTIVE'),
    (3,  N'Vật lý',      N'STEM',      N'Lớp 10', N'Củng cố nền tảng và nâng cao',             'ACTIVE'),
    (4,  N'Vật lý',      N'STEM',      N'Lớp 12', N'Luyện đề và giải nhanh',                   'ACTIVE'),
    (5,  N'Hóa học',     N'STEM',      N'Lớp 11', N'Lý thuyết và bài tập hóa học',             'ACTIVE'),
    (6,  N'Ngữ văn',     N'Social',    N'Lớp 9',  N'Rèn kỹ năng đọc hiểu và nghị luận',        'ACTIVE'),
    (7,  N'Ngữ văn',     N'Social',    N'Lớp 12', N'Luyện thi tốt nghiệp THPT',                'ACTIVE'),
    (8,  N'Tiếng Anh',   N'Language',  N'Lớp 8',  N'Ngữ pháp và giao tiếp cơ bản',             'ACTIVE'),
    (9,  N'Tiếng Anh',   N'Language',  N'Lớp 11', N'Luyện kỹ năng nghe nói đọc viết',          'ACTIVE'),
    (10, N'Sinh học',    N'STEM',      N'Lớp 12', N'Ôn thi Sinh học theo chuyên đề',           'ACTIVE'),
    (11, N'Tin học',     N'Technology',N'Lớp 10', N'Tin học cơ bản và tư duy thuật toán',      'ACTIVE'),
    (12, N'Lịch sử',     N'Social',    N'Lớp 11', N'Hệ thống hóa kiến thức theo mốc thời gian','ACTIVE'),
    (13, N'Địa lý',      N'Social',    N'Lớp 12', N'Rèn kỹ năng Atlat và xử lý số liệu',       'ACTIVE'),
    (14, N'Toán',        N'STEM',      N'Lớp 7',  N'Bồi dưỡng Toán trung học cơ sở',           'ACTIVE'),
    (15, N'Tiếng Anh',   N'Language',  N'Lớp 6',  N'Xây nền tảng từ vựng và phát âm',          'INACTIVE');
SET IDENTITY_INSERT SUBJECT OFF;
GO

SET IDENTITY_INSERT TUTOR_CAPABILITY ON;
INSERT INTO TUTOR_CAPABILITY (capability_id, tutor_id, subject_id, teaching_level, years_experience, note)
VALUES
    (1,  1,  1,  N'Lớp 12', N'5', N'Chuyên luyện thi khối A'),
    (2,  1,  2,  N'Lớp 10', N'4', N'Củng cố nền tảng đại số'),
    (3,  1, 14,  N'Lớp 7',  N'3', N'Dạy bồi dưỡng học sinh khá giỏi'),
    (4,  2,  8,  N'Lớp 8',  N'4', N'Giao tiếp và ngữ pháp'),
    (5,  2,  9,  N'Lớp 11', N'4', N'Luyện kiểm tra định kỳ'),
    (6,  3,  3,  N'Lớp 10', N'3', N'Dạy offline khu Hà Đông'),
    (7,  3,  4,  N'Lớp 12', N'2', N'Luyện đề mức khá'),
    (8,  4,  6,  N'Lớp 9',  N'6', N'Rèn viết nghị luận'),
    (9,  4,  7,  N'Lớp 12', N'6', N'Luyện thi môn Văn'),
    (10, 5,  5,  N'Lớp 11', N'2', N'Cần lịch linh hoạt'),
    (11, 6,  8,  N'Lớp 8',  N'7', N'Học online rất tốt'),
    (12, 6,  9,  N'Lớp 11', N'7', N'Luyện chứng chỉ nền tảng'),
    (13, 7, 10,  N'Lớp 12', N'1', N'Hiện đã ngưng nhận lớp');
SET IDENTITY_INSERT TUTOR_CAPABILITY OFF;
GO

SET IDENTITY_INSERT TUTOR_AVAILABILITY ON;
INSERT INTO TUTOR_AVAILABILITY (availability_id, tutor_id, day_of_week, start_time, end_time, teaching_mode, area, status)
VALUES
    (1,  1, 1, '19:00', '21:00', 'OFFLINE', N'Cầu Giấy',      'AVAILABLE'),
    (2,  1, 3, '19:00', '21:00', 'OFFLINE', N'Cầu Giấy',      'AVAILABLE'),
    (3,  1, 6, '08:00', '10:00', 'ONLINE',  N'Cầu Giấy',      'AVAILABLE'),
    (4,  2, 2, '18:30', '20:00', 'ONLINE',  N'Đống Đa',       'AVAILABLE'),
    (5,  2, 5, '18:30', '20:00', 'BOTH',    N'Đống Đa',       'AVAILABLE'),
    (6,  3, 2, '19:00', '20:30', 'OFFLINE', N'Hà Đông',       'AVAILABLE'),
    (7,  3, 4, '19:00', '20:30', 'OFFLINE', N'Hà Đông',       'AVAILABLE'),
    (8,  4, 1, '18:00', '20:00', 'OFFLINE', N'Thanh Xuân',    'AVAILABLE'),
    (9,  4, 4, '18:00', '20:00', 'OFFLINE', N'Thanh Xuân',    'AVAILABLE'),
    (10, 5, 3, '18:30', '20:00', 'OFFLINE', N'Nam Từ Liêm',   'UNAVAILABLE'),
    (11, 6, 6, '09:00', '11:00', 'ONLINE',  N'Long Biên',     'AVAILABLE'),
    (12, 6, 7, '19:00', '21:00', 'ONLINE',  N'Long Biên',     'AVAILABLE'),
    (13, 7, 2, '17:30', '19:00', 'OFFLINE', N'Ba Đình',       'UNAVAILABLE');
SET IDENTITY_INSERT TUTOR_AVAILABILITY OFF;
GO

SET IDENTITY_INSERT LEARNING_REQUEST ON;
INSERT INTO LEARNING_REQUEST (
    request_id, student_id, subject_id, requested_level, learning_goal,
    preferred_area, preferred_mode, preferred_schedule, expected_fee, status
)
VALUES
    (1,  1,  1, N'Lớp 12', N'Ôn thi đại học khối A, cần luyện đề đều mỗi tuần',                    N'Cầu Giấy',      'OFFLINE', N'T2, T4 tối',       300000, 'ASSIGNED'),
    (2,  3,  3, N'Lớp 10', N'Củng cố nền tảng Vật lý học kỳ 1',                                    N'Hà Đông',       'OFFLINE', N'T3, T5 tối',       220000, 'ASSIGNED'),
    (3,  4,  6, N'Lớp 9',  N'Rèn kỹ năng viết nghị luận để thi vào 10',                            N'Thanh Xuân',    'OFFLINE', N'T2, T5 tối',       250000, 'ASSIGNED'),
    (4,  2,  9, N'Lớp 11', N'Luyện tiếng Anh giao tiếp kết hợp ngữ pháp',                          N'Đống Đa',       'ONLINE',  N'T3, T6 tối',       200000, 'ASSIGNED'),
    (5,  5,  8, N'Lớp 8',  N'Cần gia sư tiếng Anh kèm sát chương trình trên lớp',                  N'Nam Từ Liêm',   'BOTH',    N'T7 sáng',          180000, 'ASSIGNED'),
    (6,  6, 14, N'Lớp 7',  N'Bồi dưỡng Toán cho học sinh khá, ưu tiên cuối tuần',                  N'Long Biên',     'ONLINE',  N'CN tối',           170000, 'ASSIGNED'),
    (7,  2,  5, N'Lớp 11', N'Học thêm Hóa để chuẩn bị kiểm tra học kỳ',                             N'Đống Đa',       'OFFLINE', N'T4, T7 chiều',     210000, 'PENDING'),
    (8,  3,  4, N'Lớp 12', N'Luyện Vật lý nâng cao, cần gia sư có kinh nghiệm',                    N'Hà Đông',       'OFFLINE', N'T3, T5 tối',       320000, 'PENDING'),
    (9,  4, 12, N'Lớp 11', N'Hệ thống lại kiến thức Lịch sử trước kỳ thi',                         N'Thanh Xuân',    'ONLINE',  N'CN sáng',          160000, 'PENDING'),
    (10, 5, 11, N'Lớp 10', N'Học Tin học cơ bản và làm quen thuật toán',                            N'Nam Từ Liêm',   'ONLINE',  N'T7 tối',           190000, 'PENDING'),
    (11, 6, 13, N'Lớp 12', N'Cần học Địa lý luyện Atlat và phần biểu đồ',                          N'Long Biên',     'OFFLINE', N'T2, T6 chiều',     210000, 'CANCELED'),
    (12, 1,  2, N'Lớp 10', N'Em trai cần học lại căn bản Toán 10 trong hè',                        N'Cầu Giấy',      'OFFLINE', N'T3, T7 chiều',     200000, 'PENDING');
SET IDENTITY_INSERT LEARNING_REQUEST OFF;
GO

SET IDENTITY_INSERT TUTOR_ASSIGNMENT ON;
INSERT INTO TUTOR_ASSIGNMENT (assignment_id, request_id, tutor_id, staff_id, assigned_at, status, note)
VALUES
    (1, 1, 1, 1, DATEADD(DAY, -40, SYSUTCDATETIME()), 'ASSIGNED', N'Gia sư phù hợp mục tiêu luyện thi đại học'),
    (2, 2, 3, 1, DATEADD(DAY, -30, SYSUTCDATETIME()), 'ASSIGNED', N'Gia sư ở gần khu vực Hà Đông'),
    (3, 3, 4, 2, DATEADD(DAY, -25, SYSUTCDATETIME()), 'ASSIGNED', N'Ưu tiên kinh nghiệm luyện thi vào 10'),
    (4, 4, 2, 2, DATEADD(DAY, -20, SYSUTCDATETIME()), 'ASSIGNED', N'Có thể dạy online vào buổi tối'),
    (5, 5, 6, 3, DATEADD(DAY, -15, SYSUTCDATETIME()), 'ASSIGNED', N'Gia sư mạnh phần tiếng Anh online'),
    (6, 6, 1, 3, DATEADD(DAY, -10, SYSUTCDATETIME()), 'ASSIGNED', N'Tạm ghép với gia sư Toán có lịch cuối tuần');
SET IDENTITY_INSERT TUTOR_ASSIGNMENT OFF;
GO

SET IDENTITY_INSERT STUDY_CLASS ON;
INSERT INTO STUDY_CLASS (
    class_id, assignment_id, class_code, tuition_fee_per_session, teaching_mode,
    location, start_date, end_date, status
)
VALUES
    (1, 1, N'CLS-TOAN12-001', 300000, 'OFFLINE', N'Nhà học viên tại Cầu Giấy',        '2026-04-15', NULL,         'ACTIVE'),
    (2, 2, N'CLS-LY10-001',   220000, 'OFFLINE', N'Phòng học cộng đồng Hà Đông',      '2026-05-01', NULL,         'ACTIVE'),
    (3, 3, N'CLS-VAN9-001',   250000, 'OFFLINE', N'Nhà học viên tại Thanh Xuân',      '2026-05-05', '2026-06-20', 'COMPLETED'),
    (4, 4, N'CLS-ENG11-001',  200000, 'ONLINE',  N'Google Meet',                       '2026-05-10', NULL,         'ACTIVE'),
    (5, 5, N'CLS-ENG8-001',   180000, 'ONLINE',  N'Zoom',                              '2026-06-01', NULL,         'ACTIVE'),
    (6, 6, N'CLS-TOAN7-001',  170000, 'ONLINE',  N'Google Meet',                       '2026-06-05', NULL,         'ACTIVE');
SET IDENTITY_INSERT STUDY_CLASS OFF;
GO

SET IDENTITY_INSERT CLASS_SCHEDULE ON;
INSERT INTO CLASS_SCHEDULE (
    schedule_id, class_id, day_of_week, start_time, end_time,
    effective_from, effective_to, status, note
)
VALUES
    (1,  1, 1, '19:00', '21:00', '2026-04-15', NULL,         'ACTIVE',   N'Ca tối thứ 2'),
    (2,  1, 3, '19:00', '21:00', '2026-04-15', NULL,         'ACTIVE',   N'Ca tối thứ 4'),
    (3,  2, 2, '19:00', '20:30', '2026-05-01', NULL,         'ACTIVE',   N'Ca tối thứ 3'),
    (4,  2, 4, '19:00', '20:30', '2026-05-01', NULL,         'ACTIVE',   N'Ca tối thứ 5'),
    (5,  3, 1, '18:00', '20:00', '2026-05-05', '2026-06-20', 'INACTIVE', N'Ca tối thứ 2 đã kết thúc'),
    (6,  3, 4, '18:00', '20:00', '2026-05-05', '2026-06-20', 'INACTIVE', N'Ca tối thứ 5 đã kết thúc'),
    (7,  4, 2, '20:00', '21:30', '2026-05-10', NULL,         'ACTIVE',   N'Online thứ 3'),
    (8,  4, 5, '20:00', '21:30', '2026-05-10', NULL,         'ACTIVE',   N'Online thứ 6'),
    (9,  5, 6, '09:00', '10:30', '2026-06-01', NULL,         'ACTIVE',   N'Sáng thứ 7'),
    (10, 6, 7, '19:30', '21:00', '2026-06-05', NULL,         'ACTIVE',   N'Tối chủ nhật');
SET IDENTITY_INSERT CLASS_SCHEDULE OFF;
GO

SET IDENTITY_INSERT LESSON_SESSION ON;
INSERT INTO LESSON_SESSION (
    session_id, class_id, schedule_id, session_number, lesson_date,
    start_time, end_time, status, content_note
)
VALUES
    (1,  1,  1, 1,  '2026-04-20', '19:00', '21:00', 'COMPLETED',      N'Khảo sát đầu vào và lập kế hoạch học tập'),
    (2,  1,  2, 2,  '2026-04-22', '19:00', '21:00', 'COMPLETED',      N'Chuyên đề hàm số và đồ thị'),
    (3,  1,  1, 3,  '2026-04-27', '19:00', '21:00', 'COMPLETED',      N'Cực trị và bài toán biến thiên'),
    (4,  1,  2, 4,  '2026-04-29', '19:00', '21:00', 'COMPLETED',      N'Bài tập ứng dụng đạo hàm'),
    (5,  1,  1, 5,  '2026-05-04', '19:00', '21:00', 'COMPLETED',      N'Hàm mũ và logarit'),
    (6,  1,  2, 6,  '2026-05-06', '19:00', '21:00', 'COMPLETED',      N'Luyện đề số 1'),
    (7,  1,  1, 7,  '2026-06-16', '19:00', '21:00', 'SCHEDULED',      NULL),
    (8,  1,  2, 8,  '2026-06-18', '19:00', '21:00', 'SCHEDULED',      NULL),
    (9,  2,  3, 1,  '2026-05-05', '19:00', '20:30', 'COMPLETED',      N'Ôn tập chuyển động thẳng đều'),
    (10, 2,  4, 2,  '2026-05-07', '19:00', '20:30', 'COMPLETED',      N'Gia tốc và phương trình chuyển động'),
    (11, 2,  3, 3,  '2026-05-12', '19:00', '20:30', 'COMPLETED',      N'Luyện tập tổng hợp'),
    (12, 2,  4, 4,  '2026-06-17', '19:00', '20:30', 'SCHEDULED',      NULL),
    (13, 2,  3, 5,  '2026-06-19', '19:00', '20:30', 'SCHEDULED',      NULL),
    (14, 3,  5, 1,  '2026-05-11', '18:00', '20:00', 'COMPLETED',      N'Kỹ năng mở bài và kết bài'),
    (15, 3,  6, 2,  '2026-05-14', '18:00', '20:00', 'COMPLETED',      N'Nghị luận xã hội'),
    (16, 3,  5, 3,  '2026-05-18', '18:00', '20:00', 'COMPLETED',      N'Nghị luận văn học'),
    (17, 3,  6, 4,  '2026-05-21', '18:00', '20:00', 'COMPLETED',      N'Phân tích tác phẩm trọng tâm'),
    (18, 3,  5, 5,  '2026-05-25', '18:00', '20:00', 'COMPLETED',      N'Chữa đề minh họa'),
    (19, 3,  6, 6,  '2026-05-28', '18:00', '20:00', 'COMPLETED',      N'Tổng ôn trước kỳ thi'),
    (20, 4,  7, 1,  '2026-05-12', '20:00', '21:30', 'COMPLETED',      N'Kiểm tra năng lực và chia mục tiêu'),
    (21, 4,  8, 2,  '2026-05-15', '20:00', '21:30', 'COMPLETED',      N'Ôn thì hiện tại và quá khứ'),
    (22, 4,  7, 3,  '2026-05-19', '20:00', '21:30', 'COMPLETED',      N'Luyện kỹ năng nghe'),
    (23, 4,  8, 4,  '2026-06-17', '20:00', '21:30', 'SCHEDULED',      NULL),
    (24, 4,  7, 5,  '2026-06-20', '20:00', '21:30', 'SCHEDULED',      NULL),
    (25, 5,  9, 1,  '2026-06-07', '09:00', '10:30', 'COMPLETED',      N'Ngữ pháp cơ bản và từ vựng chủ đề trường học'),
    (26, 5,  9, 2,  '2026-06-14', '09:00', '10:30', 'COMPLETED',      N'Luyện nghe nói chủ đề gia đình'),
    (27, 5,  9, 3,  '2026-06-21', '09:00', '10:30', 'SCHEDULED',      NULL),
    (28, 6, 10, 1,  '2026-06-08', '19:30', '21:00', 'COMPLETED',      N'Số hữu tỉ và biểu thức đại số'),
    (29, 6, 10, 2,  '2026-06-15', '19:30', '21:00', 'SCHEDULED',      NULL),
    (30, 6, 10, 3,  '2026-06-22', '19:30', '21:00', 'SCHEDULED',      NULL);
SET IDENTITY_INSERT LESSON_SESSION OFF;
GO

SET IDENTITY_INSERT TUITION_INVOICE ON;
INSERT INTO TUITION_INVOICE (
    invoice_id, class_id, period_start, period_end, completed_sessions,
    tuition_fee_per_session, amount_due, amount_paid, status
)
VALUES
    (1, 1, '2026-04-01', '2026-04-30', 4, 300000, 1200000, 1200000, 'PAID'),
    (2, 1, '2026-05-01', '2026-05-31', 2, 300000, 600000, 300000,  'PARTIALLY_PAID'),
    (3, 2, '2026-05-01', '2026-05-31', 3, 220000, 660000, 660000,  'PAID'),
    (4, 3, '2026-05-01', '2026-05-31', 6, 250000, 1500000,1500000, 'PAID'),
    (5, 4, '2026-05-01', '2026-05-31', 3, 200000, 600000, 600000,  'PAID'),
    (6, 5, '2026-06-01', '2026-06-30', 2, 180000, 360000, 180000,  'PARTIALLY_PAID'),
    (7, 6, '2026-06-01', '2026-06-30', 1, 170000, 170000, 0,       'UNPAID');
SET IDENTITY_INSERT TUITION_INVOICE OFF;
GO

SET IDENTITY_INSERT TUITION_PAYMENT ON;
INSERT INTO TUITION_PAYMENT (
    payment_id, invoice_id, staff_id, payment_date, amount_paid, payment_method, note, status
)
VALUES
    (1, 1, 3, DATEADD(DAY, -40, SYSUTCDATETIME()), 600000, N'BANK_TRANSFER', N'Thanh toán đợt 1 tháng 4', 'SUCCESS'),
    (2, 1, 3, DATEADD(DAY, -35, SYSUTCDATETIME()), 600000, N'CASH',          N'Thanh toán đợt 2 tháng 4', 'SUCCESS'),
    (3, 2, 3, DATEADD(DAY, -15, SYSUTCDATETIME()), 300000, N'BANK_TRANSFER', N'Tạm thu tháng 5',          'SUCCESS'),
    (4, 3, 3, DATEADD(DAY, -18, SYSUTCDATETIME()), 660000, N'BANK_TRANSFER', N'Thanh toán đủ tháng 5',    'SUCCESS'),
    (5, 4, 3, DATEADD(DAY, -12, SYSUTCDATETIME()), 1500000,N'CASH',          N'Thanh toán trọn khóa',      'SUCCESS'),
    (6, 5, 3, DATEADD(DAY, -10, SYSUTCDATETIME()), 600000, N'BANK_TRANSFER', N'Thanh toán tháng 5',       'SUCCESS'),
    (7, 6, 3, DATEADD(DAY, -2,  SYSUTCDATETIME()), 180000, N'EWALLET',       N'Thanh toán 1 buổi đầu',    'SUCCESS'),
    (8, 6, 3, DATEADD(DAY, -1,  SYSUTCDATETIME()), 50000,  N'EWALLET',       N'Giao dịch hoàn lại',        'REFUNDED');
SET IDENTITY_INSERT TUITION_PAYMENT OFF;
GO

/* Quick verification snapshots */
SELECT role, status, COUNT(*) AS total_accounts
FROM USER_ACCOUNT
GROUP BY role, status
ORDER BY role, status;
GO

SELECT status, COUNT(*) AS total_requests
FROM LEARNING_REQUEST
GROUP BY status
ORDER BY status;
GO

SELECT status, COUNT(*) AS total_classes
FROM STUDY_CLASS
GROUP BY status
ORDER BY status;
GO

SELECT status, COUNT(*) AS total_invoices
FROM TUITION_INVOICE
GROUP BY status
ORDER BY status;
GO

SELECT status, COUNT(*) AS total_payments
FROM TUITION_PAYMENT
GROUP BY status
ORDER BY status;
GO

SELECT *
FROM VW_STUDY_CLASS_DETAIL
ORDER BY class_id;
GO

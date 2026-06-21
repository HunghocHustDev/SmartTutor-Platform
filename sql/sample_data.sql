-- ============================================================
-- SEED DATA MỞ RỘNG – SmartTutor Platform
-- Mục đích: Test luồng phân công gia sư & tạo lớp
-- ============================================================
USE TutorCenterDB;
GO

-- Xoá dữ liệu cũ để tránh trùng lặp
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

/* Password hashes (giữ nguyên)
   staff123   -> 10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6
   student123 -> 703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b
   tutor123   -> 537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf
*/

-- ========== USER ACCOUNTS ==========
SET IDENTITY_INSERT USER_ACCOUNT ON;
INSERT INTO USER_ACCOUNT (account_id, email, username, password_hash, role, status) VALUES
(1, N'staff1@smarttutor.local', N'staff1', N'10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6', 'STAFF', 'ACTIVE'),
(2, N'staff2@smarttutor.local', N'staff2', N'10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6', 'STAFF', 'ACTIVE'),

-- Students
(10, N'pham.lam@student.local',    N'lam.pham',   N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),
(11, N'linh.nguyen@student.local', N'linh.nguyen',N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),
(12, N'minh.tran@student.local',   N'minh.tran',  N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),
(13, N'an.do@student.local',       N'an.do',      N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),
(14, N'hoa.le@student.local',      N'hoa.le',     N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),
(15, N'khanh.vo@student.local',    N'khanh.vo',   N'703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b', 'STUDENT', 'ACTIVE'),

-- Tutors (mở rộng)
(20, N'bao.ngo@tutor.local',       N'bao.ngo',    N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE'),
(21, N'trang.pham@tutor.local',    N'trang.pham', N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE'),
(22, N'vu.hoang@tutor.local',      N'vu.hoang',   N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE'),
(23, N'mai.nguyen@tutor.local',    N'mai.nguyen', N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE'),
(24, N'linh.do@tutor.local',       N'linh.do',    N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE'),
(25, N'quan.trinh@tutor.local',    N'quan.trinh', N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE'),
(26, N'anh.vu@tutor.local',        N'anh.vu',     N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'INACTIVE'),
-- Tutor mới để test đa dạng
(27, N'huy.le@tutor.local',        N'huy.le',     N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE'),
(28, N'thao.tran@tutor.local',     N'thao.tran',  N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE'),
(29, N'nam.pham@tutor.local',      N'nam.pham',   N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE'),
(30, N'ha.nguyen@tutor.local',     N'ha.nguyen',  N'537d26965fd30bf9ebe78b86a8b56ca954cd886ed6d57e43fd37924f1dc2fcbf', 'TUTOR', 'ACTIVE');
SET IDENTITY_INSERT USER_ACCOUNT OFF;
GO

-- ========== STAFF ==========
SET IDENTITY_INSERT STAFF ON;
INSERT INTO STAFF (staff_id, account_id, full_name, phone, contact_email, position, status) VALUES
(1, 1, N'Trần Thu Hà',     N'0901000001', N'staff1@smarttutor.local', N'Điều phối viên',    'ACTIVE'),
(2, 2, N'Lê Minh Quân',    N'0901000002', N'staff2@smarttutor.local', N'Tư vấn tuyển sinh', 'ACTIVE');
SET IDENTITY_INSERT STAFF OFF;
GO

-- ========== STUDENTS ==========
SET IDENTITY_INSERT STUDENT ON;
INSERT INTO STUDENT (student_id, account_id, full_name, phone, contact_email, address, area, current_level, grade_level, status) VALUES
(1, 10, N'Phạm Gia Lâm',     N'0987000001', N'pham.lam@student.local',    N'Cầu Giấy, Hà Nội',       N'Cầu Giấy',    N'Lớp 12', N'Lớp 12', 'ACTIVE'),
(2, 11, N'Nguyễn Ngọc Linh', N'0987000002', N'linh.nguyen@student.local', N'Đống Đa, Hà Nội',        N'Đống Đa',     N'Lớp 11', N'Lớp 11', 'ACTIVE'),
(3, 12, N'Trần Đức Minh',    N'0987000003', N'minh.tran@student.local',   N'Hà Đông, Hà Nội',        N'Hà Đông',     N'Lớp 10', N'Lớp 10', 'ACTIVE'),
(4, 13, N'Đỗ Hoàng An',      N'0987000004', N'an.do@student.local',       N'Thanh Xuân, Hà Nội',    N'Thanh Xuân',  N'Lớp 9',  N'Lớp 9',  'ACTIVE'),
(5, 14, N'Lê Thu Hòa',       N'0987000005', N'hoa.le@student.local',      N'Nam Từ Liêm, Hà Nội',   N'Nam Từ Liêm', N'Lớp 8',  N'Lớp 8',  'ACTIVE'),
(6, 15, N'Võ Gia Khánh',     N'0987000006', N'khanh.vo@student.local',    N'Long Biên, Hà Nội',     N'Long Biên',   N'Lớp 7',  N'Lớp 7',  'ACTIVE');
SET IDENTITY_INSERT STUDENT OFF;
GO

-- ========== TUTORS ==========
SET IDENTITY_INSERT TUTOR ON;
INSERT INTO TUTOR (tutor_id, account_id, full_name, phone, contact_email, university, major, experience_years, area, status) VALUES
(1, 20, N'Ngô Quốc Bảo',       N'0903000001', N'bao.ngo@tutor.local',    N'Đại học Sư phạm Hà Nội',   N'Sư phạm Toán',         5, N'Cầu Giấy',    'ACTIVE'),
(2, 21, N'Phạm Khánh Trang',   N'0903000002', N'trang.pham@tutor.local', N'Đại học Quốc gia Hà Nội',  N'Ngôn ngữ Anh',         4, N'Đống Đa',     'ACTIVE'),
(3, 22, N'Hoàng Đức Vũ',       N'0903000003', N'vu.hoang@tutor.local',   N'Đại học Bách khoa Hà Nội', N'Vật lý kỹ thuật',      3, N'Hà Đông',     'ACTIVE'),
(4, 23, N'Nguyễn Thu Mai',     N'0903000004', N'mai.nguyen@tutor.local', N'Đại học Sư phạm Hà Nội 2', N'Ngữ văn',              6, N'Thanh Xuân',  'ACTIVE'),
(5, 24, N'Đỗ Mỹ Linh',         N'0903000005', N'linh.do@tutor.local',    N'Đại học Khoa học Tự nhiên',N'Hóa học',              2, N'Nam Từ Liêm', 'ACTIVE'),   -- đổi từ PAUSED thành ACTIVE để test
(6, 25, N'Trịnh Hải Quân',     N'0903000006', N'quan.trinh@tutor.local', N'Đại học Ngoại ngữ',        N'Sư phạm Tiếng Anh',    7, N'Long Biên',   'ACTIVE'),
(7, 26, N'Vũ Phương Anh',      N'0903000007', N'anh.vu@tutor.local',     N'Đại học Sư phạm Hà Nội',   N'Sinh học',             1, N'Ba Đình',     'INACTIVE'),
-- Gia sư mới để test matching
(8, 27, N'Lê Quang Huy',       N'0903000008', N'huy.le@tutor.local',     N'Đại học Sư phạm Hà Nội',   N'Toán',                 4, N'Cầu Giấy',    'ACTIVE'),
(9, 28, N'Trần Minh Thảo',     N'0903000009', N'thao.tran@tutor.local',  N'Đại học Hà Nội',           N'Tiếng Anh',            5, N'Đống Đa',     'ACTIVE'),
(10,29, N'Phạm Văn Nam',       N'0903000010', N'nam.pham@tutor.local',   N'Đại học Bách khoa',        N'Vật lý',               2, N'Hà Đông',     'ACTIVE'),
(11,30, N'Nguyễn Thu Hà',      N'0903000011', N'ha.nguyen@tutor.local',  N'Đại học Sư phạm',         N'Ngữ văn',              6, N'Thanh Xuân',  'ACTIVE');
SET IDENTITY_INSERT TUTOR OFF;
GO

-- ========== SUBJECTS ==========
SET IDENTITY_INSERT SUBJECT ON;
INSERT INTO SUBJECT (subject_id, subject_name, subject_group, grade_level, description, status) VALUES
(1, N'Toán',        N'STEM',     N'Lớp 12', N'Luyện thi THPT Quốc gia môn Toán',        'ACTIVE'),
(2, N'Toán',        N'STEM',     N'Lớp 10', N'Bổ trợ Toán trung học phổ thông',         'ACTIVE'),
(3, N'Vật lý',      N'STEM',     N'Lớp 10', N'Củng cố nền tảng và nâng cao',            'ACTIVE'),
(4, N'Vật lý',      N'STEM',     N'Lớp 12', N'Luyện đề và giải nhanh',                  'ACTIVE'),
(5, N'Hóa học',     N'STEM',     N'Lớp 11', N'Lý thuyết và bài tập hóa học',            'ACTIVE'),
(6, N'Ngữ văn',     N'Social',   N'Lớp 9',  N'Rèn kỹ năng đọc hiểu và nghị luận',       'ACTIVE'),
(7, N'Ngữ văn',     N'Social',   N'Lớp 12', N'Luyện thi tốt nghiệp THPT',               'ACTIVE'),
(8, N'Tiếng Anh',   N'Language', N'Lớp 8',  N'Ngữ pháp và giao tiếp cơ bản',            'ACTIVE'),
(9, N'Tiếng Anh',   N'Language', N'Lớp 11', N'Luyện kỹ năng nghe nói đọc viết',         'ACTIVE'),
(10,N'Sinh học',    N'STEM',     N'Lớp 12', N'Ôn thi Sinh học theo chuyên đề',          'ACTIVE'),
(11,N'Tin học',     N'Technology',N'Lớp 10', N'Tin học cơ bản và tư duy thuật toán',     'ACTIVE'),
(12,N'Lịch sử',     N'Social',   N'Lớp 11', N'Hệ thống hóa kiến thức theo mốc thời gian','ACTIVE'),
(13,N'Địa lý',      N'Social',   N'Lớp 12', N'Rèn kỹ năng Atlat và xử lý số liệu',      'ACTIVE'),
(14,N'Toán',        N'STEM',     N'Lớp 7',  N'Bồi dưỡng Toán trung học cơ sở',          'ACTIVE');
SET IDENTITY_INSERT SUBJECT OFF;
GO

-- ========== TUTOR CAPABILITIES (đa dạng) ==========
SET IDENTITY_INSERT TUTOR_CAPABILITY ON;
INSERT INTO TUTOR_CAPABILITY (capability_id, tutor_id, subject_id, teaching_level, years_experience, note) VALUES
-- Tutor 1: Toán 12, Toán 10, Toán 7
(1, 1, 1, N'Lớp 12', 5, N'Chuyên luyện thi'),
(2, 1, 2, N'Lớp 10', 4, N'Củng cố đại số'),
(3, 1, 14,N'Lớp 7',  3, N'Bồi dưỡng HSG'),
-- Tutor 2: Tiếng Anh 8, 11
(4, 2, 8, N'Lớp 8',  4, N'Giao tiếp'),
(5, 2, 9, N'Lớp 11', 4, N'Luyện thi'),
-- Tutor 3: Vật lý 10, 12
(6, 3, 3, N'Lớp 10', 3, N'Cơ bản'),
(7, 3, 4, N'Lớp 12', 2, N'Nâng cao'),
-- Tutor 4: Văn 9, 12
(8, 4, 6, N'Lớp 9',  6, N'NLXH'),
(9, 4, 7, N'Lớp 12', 6, N'Luyện thi'),
-- Tutor 5: Hóa 11
(10,5, 5, N'Lớp 11', 2, N'Cơ bản'),
-- Tutor 6: Tiếng Anh 8, 11 (trùng môn tutor 2 nhưng online mạnh)
(11,6, 8, N'Lớp 8',  7, N'Online'),
(12,6, 9, N'Lớp 11', 7, N'Online'),
-- Tutor 7: Sinh 12 (INACTIVE)
(13,7, 10,N'Lớp 12', 1, N'Ngưng nhận lớp'),
-- Tutor 8 (Huy): Toán 12, Toán 10
(14,8, 1, N'Lớp 12', 4, N'Luyện thi THPT'),
(15,8, 2, N'Lớp 10', 4, N'Cơ bản'),
-- Tutor 9 (Thảo): Tiếng Anh 8, Tiếng Anh 11
(16,9, 8, N'Lớp 8',  5, N'Phát âm'),
(17,9, 9, N'Lớp 11', 5, N'IELTS'),
-- Tutor 10 (Nam): Vật lý 10, 12
(18,10,3, N'Lớp 10', 2, N'Thực hành'),
(19,10,4, N'Lớp 12', 2, N'Luyện đề'),
-- Tutor 11 (Hà): Văn 9, Văn 12
(20,11,6, N'Lớp 9',  6, N'Viết văn'),
(21,11,7, N'Lớp 12', 6, N'Ôn thi');
SET IDENTITY_INSERT TUTOR_CAPABILITY OFF;
GO

-- ========== TUTOR AVAILABILITIES (đa dạng để test schedule matching) ==========
SET IDENTITY_INSERT TUTOR_AVAILABILITY ON;
INSERT INTO TUTOR_AVAILABILITY (availability_id, tutor_id, day_of_week, start_time, end_time, teaching_mode, area, status) VALUES
-- Tutor 1: T2(19-21 offline), T4(19-21 offline), T7(8-10 online)
(1, 1, 1, '19:00', '21:00', 'OFFLINE', N'Cầu Giấy', 'AVAILABLE'),
(2, 1, 3, '19:00', '21:00', 'OFFLINE', N'Cầu Giấy', 'AVAILABLE'),
(3, 1, 6, '08:00', '10:00', 'ONLINE',  N'Cầu Giấy', 'AVAILABLE'),

-- Tutor 2: T3(18:30-20 online), T6(18:30-20 BOTH)
(4, 2, 2, '18:30', '20:00', 'ONLINE',  N'Đống Đa', 'AVAILABLE'),
(5, 2, 5, '18:30', '20:00', 'BOTH',    N'Đống Đa', 'AVAILABLE'),

-- Tutor 3: T3(19-20:30 offline), T5(19-20:30 offline)
(6, 3, 2, '19:00', '20:30', 'OFFLINE', N'Hà Đông', 'AVAILABLE'),
(7, 3, 4, '19:00', '20:30', 'OFFLINE', N'Hà Đông', 'AVAILABLE'),

-- Tutor 4: T2(18-20 offline), T5(18-20 offline)
(8, 4, 1, '18:00', '20:00', 'OFFLINE', N'Thanh Xuân', 'AVAILABLE'),
(9, 4, 4, '18:00', '20:00', 'OFFLINE', N'Thanh Xuân', 'AVAILABLE'),

-- Tutor 5: T4(18:30-20 offline)
(10,5, 3, '18:30', '20:00', 'OFFLINE', N'Nam Từ Liêm', 'AVAILABLE'),

-- Tutor 6: T7(9-11 online), CN(19-21 online)
(11,6, 6, '09:00', '11:00', 'ONLINE', N'Long Biên', 'AVAILABLE'),
(12,6, 7, '19:00', '21:00', 'ONLINE', N'Long Biên', 'AVAILABLE'),

-- Tutor 8 (Huy): T2(19-21 offline), T3(19-21 online), T4(19-21 offline) – nhiều khung giờ
(13,8, 1, '19:00', '21:00', 'OFFLINE', N'Cầu Giấy', 'AVAILABLE'),
(14,8, 2, '19:00', '21:00', 'ONLINE',  N'Cầu Giấy', 'AVAILABLE'),
(15,8, 3, '19:00', '21:00', 'OFFLINE', N'Cầu Giấy', 'AVAILABLE'),

-- Tutor 9 (Thảo): T3(18:30-20 BOTH), T5(18:30-20 BOTH)
(16,9, 2, '18:30', '20:00', 'BOTH', N'Đống Đa', 'AVAILABLE'),
(17,9, 4, '18:30', '20:00', 'BOTH', N'Đống Đa', 'AVAILABLE'),

-- Tutor 10 (Nam): T3(19-20:30 offline), T5(19-20:30 offline)
(18,10,2, '19:00', '20:30', 'OFFLINE', N'Hà Đông', 'AVAILABLE'),
(19,10,4, '19:00', '20:30', 'OFFLINE', N'Hà Đông', 'AVAILABLE'),

-- Tutor 11 (Hà): T2(18-20 offline), T5(18-20 offline)
(20,11,1, '18:00', '20:00', 'OFFLINE', N'Thanh Xuân', 'AVAILABLE'),
(21,11,4, '18:00', '20:00', 'OFFLINE', N'Thanh Xuân', 'AVAILABLE');
SET IDENTITY_INSERT TUTOR_AVAILABILITY OFF;
GO

-- ========== LEARNING REQUESTS (đa dạng trạng thái & yêu cầu) ==========
SET IDENTITY_INSERT LEARNING_REQUEST ON;
INSERT INTO LEARNING_REQUEST (request_id, student_id, subject_id, requested_level, learning_goal, preferred_area, preferred_mode, preferred_schedule, expected_fee, status) VALUES
-- Nhóm đã ASSIGNED nhưng chưa có class (để test tạo class)
(1, 1, 1, N'Lớp 12', N'Ôn thi đại học Toán',          N'Cầu Giấy',   'OFFLINE', N'T2, T4 tối',       300000, 'ASSIGNED'),
(2, 3, 3, N'Lớp 10', N'Củng cố Vật lý 10',             N'Hà Đông',    'OFFLINE', N'T3, T5 tối',       220000, 'ASSIGNED'),
(3, 4, 6, N'Lớp 9',  N'Luyện văn thi vào 10',          N'Thanh Xuân', 'OFFLINE', N'T2, T5 tối',       250000, 'ASSIGNED'),
(4, 2, 9, N'Lớp 11', N'Tiếng Anh giao tiếp',           N'Đống Đa',    'ONLINE',  N'T3, T6 tối',       200000, 'ASSIGNED'),
(5, 5, 8, N'Lớp 8',  N'Tiếng Anh cơ bản',              N'Nam Từ Liêm','BOTH',    N'T7 sáng',          180000, 'ASSIGNED'),
(6, 6,14, N'Lớp 7',  N'Toán nâng cao cuối tuần',       N'Long Biên',  'ONLINE',  N'CN tối',           170000, 'ASSIGNED'),

-- Nhóm PENDING – dùng để test suggest & phân công mới
-- Request khớp hoàn hảo với Tutor 1 (Toán 12, Cầu Giấy, T2+T4 19-21 offline)
(7, 1, 1, N'Lớp 12', N'Luyện đề Toán nâng cao',        N'Cầu Giấy',   'OFFLINE', N'T2, T4 19:00-21:00', 300000, 'PENDING'),
-- Request khớp với Tutor 8 (Toán 12, Cầu Giấy, lịch T2+T4 19-21 offline)
(8, 1, 1, N'Lớp 12', N'Toán tổng ôn',                  N'Cầu Giấy',   'OFFLINE', N'T2, T4 19:00-21:00', 280000, 'PENDING'),
-- Request sai khu vực (Cầu Giấy nhưng tutor 8 ở Cầu Giấy vẫn khớp) – nhưng thêm yêu cầu ONLINE để test mode
(9, 2, 9, N'Lớp 11', N'Tiếng Anh học online',          N'Đống Đa',    'ONLINE',  N'T3, T6 18:30-20:00', 200000, 'PENDING'),
-- Request OFFLINE nhưng tutor phù hợp lại chỉ có ONLINE -> sẽ không khớp mode
(10,3, 4, N'Lớp 12', N'Vật lý 12 offline Hà Đông',     N'Hà Đông',    'OFFLINE', N'T3, T5 19:00-20:30', 300000, 'PENDING'),
-- Request không có lịch cụ thể -> chỉ khớp theo môn & khu vực
(11,4, 6, N'Lớp 9',  N'Văn 9 không rõ lịch',           N'Thanh Xuân', 'OFFLINE', NULL,                  250000, 'PENDING'),
-- Request có lịch nhưng không trùng với bất kỳ tutor nào (T7 18-19) -> điểm schedule thấp
(12,5, 5, N'Lớp 11', N'Hóa 11 lịch lẻ',                N'Nam Từ Liêm','OFFLINE', N'T7 18:00-19:00',     210000, 'PENDING'),
-- Request đã có class nhưng để test dashboard (giữ nguyên 1 vài cái)
(13,2, 9, N'Lớp 11', N'Tiếng Anh duy trì',             N'Đống Đa',    'ONLINE',  N'T3, T6 tối',       200000, 'ASSIGNED'), -- sẽ gán class sau
(14,6,14, N'Lớp 7',  N'Toán 7 online',                 N'Long Biên',  'ONLINE',  N'CN tối',           170000, 'ASSIGNED'); -- sẽ gán class sau
SET IDENTITY_INSERT LEARNING_REQUEST OFF;
GO

-- ========== TUTOR ASSIGNMENTS (gán sẵn cho 6 request đầu + 2 request mới) ==========
SET IDENTITY_INSERT TUTOR_ASSIGNMENT ON;
INSERT INTO TUTOR_ASSIGNMENT (assignment_id, request_id, tutor_id, staff_id, assigned_at, status, note) VALUES
(1, 1, 1, 1, DATEADD(DAY, -40, SYSUTCDATETIME()), 'ASSIGNED', N'Gia sư Toán 12 phù hợp'),
(2, 2, 3, 1, DATEADD(DAY, -30, SYSUTCDATETIME()), 'ASSIGNED', N'Gia sư Vật lý gần Hà Đông'),
(3, 3, 4, 2, DATEADD(DAY, -25, SYSUTCDATETIME()), 'ASSIGNED', N'Gia sư Văn luyện thi vào 10'),
(4, 4, 2, 2, DATEADD(DAY, -20, SYSUTCDATETIME()), 'ASSIGNED', N'Tiếng Anh online'),
(5, 5, 6, 1, DATEADD(DAY, -15, SYSUTCDATETIME()), 'ASSIGNED', N'Tiếng Anh 8 online'),
(6, 6, 1, 1, DATEADD(DAY, -10, SYSUTCDATETIME()), 'ASSIGNED', N'Toán 7 online'),
(7,13, 2, 2, DATEADD(DAY, -5,  SYSUTCDATETIME()), 'ASSIGNED', N'Tiếng Anh 11 gán thêm'),
(8,14, 1, 2, DATEADD(DAY, -3,  SYSUTCDATETIME()), 'ASSIGNED', N'Toán 7 gán thêm');
SET IDENTITY_INSERT TUTOR_ASSIGNMENT OFF;
GO

-- ========== STUDY CLASSES (tạo sẵn vài lớp để test các bước tiếp theo) ==========
SET IDENTITY_INSERT STUDY_CLASS ON;
INSERT INTO STUDY_CLASS (class_id, assignment_id, class_code, tuition_fee_per_session, teaching_mode, location, start_date, end_date, status) VALUES
(1, 1, N'CLS-TOAN12-001', 300000, 'OFFLINE', N'Nhà học viên Cầu Giấy',   '2026-04-15', NULL,         'ACTIVE'),
(2, 2, N'CLS-LY10-001',   220000, 'OFFLINE', N'Phòng học Hà Đông',      '2026-05-01', NULL,         'ACTIVE'),
(3, 3, N'CLS-VAN9-001',   250000, 'OFFLINE', N'Nhà học viên Thanh Xuân', '2026-05-05', '2026-06-20', 'COMPLETED'),
(4, 4, N'CLS-ENG11-001',  200000, 'ONLINE',  N'Google Meet',             '2026-05-10', NULL,         'ACTIVE');
SET IDENTITY_INSERT STUDY_CLASS OFF;
GO

-- ========== CLASS SCHEDULES (mỗi lớp 1-2 buổi/tuần) ==========
SET IDENTITY_INSERT CLASS_SCHEDULE ON;
INSERT INTO CLASS_SCHEDULE (schedule_id, class_id, day_of_week, start_time, end_time, effective_from, effective_to, status, note) VALUES
-- Class 1 (Toán 12, offline Cầu Giấy, T2+T4 19h-21h)
(1, 1, 1, '19:00', '21:00', '2026-04-15', NULL, 'ACTIVE', N'Tối thứ 2'),
(2, 1, 3, '19:00', '21:00', '2026-04-15', NULL, 'ACTIVE', N'Tối thứ 4'),

-- Class 2 (Lý 10, offline Hà Đông, T3+T5 19h-20h30)
(3, 2, 2, '19:00', '20:30', '2026-05-01', NULL, 'ACTIVE', N'Tối thứ 3'),
(4, 2, 4, '19:00', '20:30', '2026-05-01', NULL, 'ACTIVE', N'Tối thứ 5'),

-- Class 3 (Văn 9, offline Thanh Xuân, T2+T5 18h-20h) – đã kết thúc
(5, 3, 1, '18:00', '20:00', '2026-05-05', '2026-06-20', 'INACTIVE', N'Thứ 2'),
(6, 3, 4, '18:00', '20:00', '2026-05-05', '2026-06-20', 'INACTIVE', N'Thứ 5'),

-- Class 4 (Anh 11, online, T3+T6 20h-21h30)
(7, 4, 2, '20:00', '21:30', '2026-05-10', NULL, 'ACTIVE', N'Thứ 3 online'),
(8, 4, 5, '20:00', '21:30', '2026-05-10', NULL, 'ACTIVE', N'Thứ 6 online');
SET IDENTITY_INSERT CLASS_SCHEDULE OFF;
GO

-- ========== LESSON SESSIONS (mỗi lớp có 4-8 buổi, xen kẽ quá khứ & tương lai) ==========
SET IDENTITY_INSERT LESSON_SESSION ON;
INSERT INTO LESSON_SESSION (session_id, class_id, schedule_id, session_number, lesson_date, start_time, end_time, status, content_note) VALUES
-- === Class 1 (Toán 12) ===
(1, 1, 1, 1, '2026-04-20', '19:00', '21:00', 'COMPLETED', N'Khảo sát & lập kế hoạch'),
(2, 1, 2, 2, '2026-04-22', '19:00', '21:00', 'COMPLETED', N'Hàm số & đồ thị'),
(3, 1, 1, 3, '2026-04-27', '19:00', '21:00', 'COMPLETED', N'Cực trị'),
(4, 1, 2, 4, '2026-04-29', '19:00', '21:00', 'COMPLETED', N'Đạo hàm ứng dụng'),
(5, 1, 1, 5, '2026-05-04', '19:00', '21:00', 'COMPLETED', N'Hàm mũ & logarit'),
(6, 1, 2, 6, '2026-05-06', '19:00', '21:00', 'COMPLETED', N'Luyện đề số 1'),
(7, 1, 1, 7, '2026-06-16', '19:00', '21:00', 'SCHEDULED', NULL),
(8, 1, 2, 8, '2026-06-18', '19:00', '21:00', 'SCHEDULED', NULL),
(9, 1, 1, 9, '2026-06-23', '19:00', '21:00', 'SCHEDULED', NULL),
(10,1, 2,10, '2026-06-25', '19:00', '21:00', 'SCHEDULED', NULL),

-- === Class 2 (Lý 10) ===
(11,2, 3, 1, '2026-05-05', '19:00', '20:30', 'COMPLETED', N'Chuyển động thẳng đều'),
(12,2, 4, 2, '2026-05-07', '19:00', '20:30', 'COMPLETED', N'Gia tốc & pt chuyển động'),
(13,2, 3, 3, '2026-05-12', '19:00', '20:30', 'COMPLETED', N'Bài tập tổng hợp'),
(14,2, 4, 4, '2026-06-17', '19:00', '20:30', 'SCHEDULED', NULL),
(15,2, 3, 5, '2026-06-19', '19:00', '20:30', 'SCHEDULED', NULL),
(16,2, 4, 6, '2026-06-24', '19:00', '20:30', 'SCHEDULED', NULL),

-- === Class 3 (Văn 9) – tất cả COMPLETED ===
(17,3, 5, 1, '2026-05-11', '18:00', '20:00', 'COMPLETED', N'Mở bài & kết bài'),
(18,3, 6, 2, '2026-05-14', '18:00', '20:00', 'COMPLETED', N'NLXH'),
(19,3, 5, 3, '2026-05-18', '18:00', '20:00', 'COMPLETED', N'NLVH'),
(20,3, 6, 4, '2026-05-21', '18:00', '20:00', 'COMPLETED', N'Phân tích tác phẩm'),
(21,3, 5, 5, '2026-05-25', '18:00', '20:00', 'COMPLETED', N'Chữa đề minh họa'),
(22,3, 6, 6, '2026-05-28', '18:00', '20:00', 'COMPLETED', N'Tổng ôn'),
(23,3, 5, 7, '2026-06-01', '18:00', '20:00', 'COMPLETED', N'Thi thử lần 1'),
(24,3, 6, 8, '2026-06-04', '18:00', '20:00', 'COMPLETED', N'Chữa đề thi thử'),

-- === Class 4 (Anh 11) ===
(25,4, 7, 1, '2026-05-12', '20:00', '21:30', 'COMPLETED', N'Kiểm tra năng lực'),
(26,4, 8, 2, '2026-05-15', '20:00', '21:30', 'COMPLETED', N'Thì hiện tại & quá khứ'),
(27,4, 7, 3, '2026-05-19', '20:00', '21:30', 'COMPLETED', N'Luyện nghe'),
(28,4, 8, 4, '2026-06-16', '20:00', '21:30', 'SCHEDULED', NULL),
(29,4, 7, 5, '2026-06-19', '20:00', '21:30', 'SCHEDULED', NULL),
(30,4, 8, 6, '2026-06-23', '20:00', '21:30', 'SCHEDULED', NULL);
SET IDENTITY_INSERT LESSON_SESSION OFF;
GO

-- ========== INVOICES (dựa trên buổi COMPLETED) ==========
SET IDENTITY_INSERT TUITION_INVOICE ON;
INSERT INTO TUITION_INVOICE (invoice_id, class_id, period_start, period_end, completed_sessions, tuition_fee_per_session, amount_due, amount_paid, status) VALUES
-- Class 1: 6 buổi hoàn thành (tháng 4+5), 300k/buổi => 1.800.000
(1, 1, '2026-04-01', '2026-05-31', 6, 300000, 1800000, 1200000, 'PARTIALLY_PAID'),
-- Class 2: 3 buổi hoàn thành (tháng 5), 220k/buổi => 660.000
(2, 2, '2026-05-01', '2026-05-31', 3, 220000, 660000, 660000, 'PAID'),
-- Class 3: 8 buổi (tháng 5+6), 250k/buổi => 2.000.000
(3, 3, '2026-05-01', '2026-06-30', 8, 250000, 2000000, 2000000, 'PAID'),
-- Class 4: 3 buổi (tháng 5+6), 200k/buổi => 600.000
(4, 4, '2026-05-01', '2026-06-30', 3, 200000, 600000, 400000, 'PARTIALLY_PAID');
SET IDENTITY_INSERT TUITION_INVOICE OFF;
GO

-- ========== PAYMENTS (một vài giao dịch mẫu) ==========
SET IDENTITY_INSERT TUITION_PAYMENT ON;
INSERT INTO TUITION_PAYMENT (payment_id, invoice_id, staff_id, payment_date, amount_paid, payment_method, note, status) VALUES
(1, 1, 1, DATEADD(DAY, -20, SYSUTCDATETIME()), 800000,  N'BANK_TRANSFER', N'Thanh toán đợt 1', 'SUCCESS'),
(2, 1, 2, DATEADD(DAY, -5,  SYSUTCDATETIME()), 400000,  N'CASH',          N'Thanh toán đợt 2', 'SUCCESS'),
(3, 2, 2, DATEADD(DAY, -15, SYSUTCDATETIME()), 660000,  N'BANK_TRANSFER', N'Thanh toán đủ',    'SUCCESS'),
(4, 3, 1, DATEADD(DAY, -10, SYSUTCDATETIME()), 2000000, N'CASH',          N'Thanh toán trọn gói','SUCCESS'),
(5, 4, 2, DATEADD(DAY, -3,  SYSUTCDATETIME()), 400000,  N'EWALLET',       N'Thanh toán 2 buổi', 'SUCCESS'),
-- Một giao dịch refund để test
(6, 4, 1, DATEADD(DAY, -1,  SYSUTCDATETIME()), 50000,   N'EWALLET',       N'Hoàn lại thừa',    'REFUNDED');
SET IDENTITY_INSERT TUITION_PAYMENT OFF;
GO

-- ========== VERIFICATION ==========
SELECT '--- USERS ---' AS Info;
SELECT role, status, COUNT(*) FROM USER_ACCOUNT GROUP BY role, status;

SELECT '--- REQUESTS ---' AS Info;
SELECT status, COUNT(*) FROM LEARNING_REQUEST GROUP BY status;

SELECT '--- ASSIGNMENTS ---' AS Info;
SELECT a.assignment_id, r.preferred_schedule, t.full_name, a.status
FROM TUTOR_ASSIGNMENT a
JOIN LEARNING_REQUEST r ON a.request_id = r.request_id
JOIN TUTOR t ON a.tutor_id = t.tutor_id;

SELECT '--- PENDING REQUESTS (test phân công) ---' AS Info;
SELECT request_id, subject_id, preferred_area, preferred_schedule, preferred_mode
FROM LEARNING_REQUEST WHERE status = 'PENDING';
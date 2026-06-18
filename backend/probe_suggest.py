# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\uni\2025.2\Database\SmartTutor-Platform\backend")
from app.database import create_session
from sqlalchemy import text
db = create_session()

# get all PENDING requests
print("=== PENDING LEARNING_REQUEST ===")
for r in db.execute(text("""
    SELECT lr.request_id, lr.student_id, lr.subject_id, lr.preferred_area,
           lr.preferred_mode, lr.preferred_schedule, lr.status
    FROM LEARNING_REQUEST lr
    WHERE lr.status = 'PENDING'
    ORDER BY lr.request_id
""")).fetchall():
    print(f"  {r}")

# get request #116 details (from the screenshot - Lý 10, Thanh Xuân, OFFLINE)
print("\n=== Request 116 detail ===")
for r in db.execute(text("""
    SELECT lr.request_id, lr.student_id, s.full_name, st.full_name AS student_name,
           lr.subject_id, su.subject_name, su.grade_level,
           lr.preferred_area, lr.preferred_mode, lr.preferred_schedule,
           lr.expected_fee, lr.status
    FROM LEARNING_REQUEST lr
    JOIN SUBJECT su ON su.subject_id = lr.subject_id
    JOIN STUDENT st ON st.student_id = lr.student_id
    LEFT JOIN STAFF s ON s.staff_id = lr.student_id
    WHERE lr.request_id IN (116, 110, 107, 105)
    ORDER BY lr.request_id
""")).fetchall():
    print(f"  {r}")

# which tutors have Vật lý Lớp 10 capability?
print("\n=== Tutors with Vật lý Lớp 10 (subject 3) ===")
for r in db.execute(text("""
    SELECT t.tutor_id, t.full_name, t.status, t.area, t.experience_years
    FROM TUTOR_CAPABILITY tc
    JOIN TUTOR t ON t.tutor_id = tc.tutor_id
    WHERE tc.subject_id = 3
    ORDER BY t.tutor_id
""")).fetchall():
    print(f"  {r}")

# their availability (day/time)
print("\n=== Availability of those tutors ===")
for r in db.execute(text("""
    SELECT ta.tutor_id, t.full_name, ta.day_of_week, ta.start_time, ta.end_time, ta.teaching_mode, ta.area, ta.status
    FROM TUTOR_AVAILABILITY ta
    JOIN TUTOR t ON t.tutor_id = ta.tutor_id
    WHERE ta.tutor_id IN (
        SELECT DISTINCT tc.tutor_id FROM TUTOR_CAPABILITY tc WHERE tc.subject_id = 3
    )
    ORDER BY ta.tutor_id, ta.day_of_week
""")).fetchall():
    print(f"  {r}")

# tutors with active assignments (busy)
print("\n=== Tutors with ASSIGNED assignments (busy) ===")
for r in db.execute(text("""
    SELECT t.tutor_id, t.full_name, t.status, COUNT(ta.assignment_id) AS busy_count
    FROM TUTOR t
    JOIN TUTOR_ASSIGNMENT ta ON ta.tutor_id = t.tutor_id AND ta.status = 'ASSIGNED'
    GROUP BY t.tutor_id, t.full_name, t.status
    ORDER BY t.tutor_id
""")).fetchall():
    print(f"  {r}")

db.close()

# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\uni\2025.2\Database\SmartTutor-Platform\backend")
from app.database import create_session
from sqlalchemy import text
db = create_session()

print("=== ACTIVE subjects ===")
for r in db.execute(text("SELECT subject_id, subject_name, grade_level FROM SUBJECT WHERE status='ACTIVE' ORDER BY subject_id")).fetchall():
    print(f"  {r}")

print("\n=== ACTIVE tutors with subject 3 (Vật lý Lớp 10), their availabilities ===")
for r in db.execute(text("""
    SELECT t.tutor_id, t.full_name, t.status, t.area, t.experience_years,
           ta.day_of_week, ta.start_time, ta.end_time, ta.teaching_mode, ta.status AS ta_status
    FROM TUTOR t
    JOIN TUTOR_CAPABILITY tc ON tc.tutor_id = t.tutor_id
    JOIN TUTOR_AVAILABILITY ta ON ta.tutor_id = t.tutor_id
    WHERE tc.subject_id = 3 AND t.status = 'ACTIVE'
    ORDER BY t.tutor_id, ta.day_of_week
""")).fetchall():
    print(f"  {r}")

print("\n=== All PENDING requests ===")
for r in db.execute(text("""
    SELECT lr.request_id, lr.student_id, lr.subject_id, su.subject_name, su.grade_level,
           lr.preferred_area, lr.preferred_mode, lr.preferred_schedule, lr.status
    FROM LEARNING_REQUEST lr
    JOIN SUBJECT su ON su.subject_id = lr.subject_id
    WHERE lr.status = 'PENDING'
    ORDER BY lr.request_id
""")).fetchall():
    print(f"  {r}")

print("\n=== Busy tutors (with ASSIGNED, not busy in Gò Vấp) ===")
for r in db.execute(text("""
    SELECT t.tutor_id, t.full_name, t.area, ta.assignment_id
    FROM TUTOR t
    JOIN TUTOR_ASSIGNMENT ta ON ta.tutor_id = t.tutor_id AND ta.status='ASSIGNED'
    WHERE t.area = N'Gò Vấp'
    ORDER BY t.tutor_id
""")).fetchall():
    print(f"  {r}")

db.close()

# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\uni\2025.2\Database\SmartTutor-Platform\backend")
from app.database import create_session
from sqlalchemy import text
db = create_session()

print("=== USER_ACCOUNT ===")
for r in db.execute(text("SELECT account_id, email, role, status FROM USER_ACCOUNT WHERE account_id <= 30 OR account_id >= 900 ORDER BY account_id")).fetchall():
    print(f"  {r}")

print("\n=== STAFF ===")
for r in db.execute(text("SELECT staff_id, full_name, contact_email, status FROM STAFF ORDER BY staff_id")).fetchall():
    print(f"  {r}")

print("\n=== STUDENT ===")
for r in db.execute(text("SELECT student_id, full_name, contact_email, status, area FROM STUDENT ORDER BY student_id")).fetchall():
    print(f"  {r}")

print("\n=== TUTOR (first 30) ===")
for r in db.execute(text("SELECT tutor_id, full_name, contact_email, status, area, experience_years FROM TUTOR ORDER BY tutor_id OFFSET 0 ROWS FETCH NEXT 30 ROWS ONLY")).fetchall():
    print(f"  {r}")

print("\n=== SUBJECT (first 15) ===")
for r in db.execute(text("SELECT subject_id, subject_name, grade_level, status FROM SUBJECT ORDER BY subject_id OFFSET 0 ROWS FETCH NEXT 15 ROWS ONLY")).fetchall():
    print(f"  {r}")

print("\n=== LEARNING_REQUEST ===")
for r in db.execute(text("SELECT request_id, student_id, subject_id, status, created_at FROM LEARNING_REQUEST ORDER BY request_id")).fetchall():
    print(f"  {r}")

print("\n=== TUTOR_ASSIGNMENT ===")
for r in db.execute(text("SELECT assignment_id, request_id, tutor_id, staff_id, status FROM TUTOR_ASSIGNMENT ORDER BY assignment_id")).fetchall():
    print(f"  {r}")

print("\n=== STUDY_CLASS ===")
for r in db.execute(text("SELECT class_id, assignment_id, class_code, teaching_mode, status FROM STUDY_CLASS ORDER BY class_id")).fetchall():
    print(f"  {r}")

print("\n=== CLASS_SCHEDULE (first 10) ===")
for r in db.execute(text("SELECT schedule_id, class_id, day_of_week, start_time, end_time, status FROM CLASS_SCHEDULE ORDER BY schedule_id OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY")).fetchall():
    print(f"  {r}")

print("\n=== LESSON_SESSION (first 10) ===")
for r in db.execute(text("SELECT session_id, class_id, session_number, lesson_date, status FROM LESSON_SESSION ORDER BY session_id OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY")).fetchall():
    print(f"  {r}")

print("\n=== TUITION_INVOICE ===")
for r in db.execute(text("SELECT invoice_id, class_id, amount_due, amount_paid, status FROM TUITION_INVOICE ORDER BY invoice_id")).fetchall():
    print(f"  {r}")

print("\n=== TUITION_PAYMENT ===")
for r in db.execute(text("SELECT payment_id, invoice_id, amount_paid, status FROM TUITION_PAYMENT ORDER BY payment_id")).fetchall():
    print(f"  {r}")

db.close()

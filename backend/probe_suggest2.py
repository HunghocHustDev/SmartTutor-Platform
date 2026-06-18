# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\uni\2025.2\Database\SmartTutor-Platform\backend")
from app.database import create_session
from sqlalchemy import text
db = create_session()

# request from screenshot: CN chiều, OFFLINE, Gò Vấp
# Let's check what request matches this description
print("=== Requests matching CN chiều + OFFLINE + Gò Vấp ===")
for r in db.execute(text("""
    SELECT lr.request_id, lr.student_id, lr.subject_id, lr.preferred_area,
           lr.preferred_mode, lr.preferred_schedule, lr.status
    FROM LEARNING_REQUEST lr
    WHERE lr.preferred_schedule LIKE '%CN%'
      AND lr.preferred_mode = 'OFFLINE'
      AND lr.preferred_area LIKE '%Gò Vấp%'
    ORDER BY lr.request_id
""")).fetchall():
    print(f"  REQUEST: {r}")

# Check subject 116
print("\n=== Subject 116 ===")
for r in db.execute(text("SELECT subject_id, subject_name, grade_level, status FROM SUBJECT WHERE subject_id = 116")).fetchall():
    print(f"  {r}")

# Check what tutors have capability for subject 116 or equivalent
print("\n=== Tutors with subject 116 capability ===")
for r in db.execute(text("""
    SELECT tc.tutor_id, tc.subject_id, t.full_name, t.status, t.area
    FROM TUTOR_CAPABILITY tc
    JOIN TUTOR t ON t.tutor_id = tc.tutor_id
    WHERE tc.subject_id = 116
    ORDER BY t.tutor_id
""")).fetchall():
    print(f"  {r}")

# Check EquivalentSubjects logic - what subjects would match subject 116?
print("\n=== Subjects equivalent to 116 ===")
for r in db.execute(text("""
    SELECT s2.subject_id, s2.subject_name, s2.grade_level, s2.status
    FROM SUBJECT s2
    CROSS JOIN (SELECT subject_id, subject_name AS req_name, grade_level AS req_level FROM SUBJECT WHERE subject_id = 116) rs
    WHERE s2.status <> 'INACTIVE'
      AND (
        s2.subject_id = rs.subject_id
        OR LOWER(LTRIM(RTRIM(ISNULL(s2.subject_name,'')))) = LOWER(LTRIM(RTRIM(ISNULL(rs.req_name,''))))
      )
    ORDER BY s2.subject_id
""")).fetchall():
    print(f"  {r}")

# Check subjects named "Vật lý" that exist
print("\n=== All 'Vật lý' subjects ===")
for r in db.execute(text("""
    SELECT subject_id, subject_name, grade_level, status FROM SUBJECT
    WHERE subject_name LIKE '%Vật lý%' OR subject_name LIKE '%vat ly%'
    ORDER BY subject_id
""")).fetchall():
    print(f"  {r}")

# Check if request #124 has subject_id that's in TUTOR_CAPABILITY
print("\n=== Request 124 subject_id and matching capabilities ===")
r = db.execute(text("SELECT request_id, subject_id, preferred_area, preferred_mode, preferred_schedule FROM LEARNING_REQUEST WHERE request_id = 124")).fetchone()
print(f"  REQ 124: {r}")
if r:
    sid = r[1]
    caps = db.execute(text("""
        SELECT tc.tutor_id, t.full_name, t.status, t.area
        FROM TUTOR_CAPABILITY tc
        JOIN TUTOR t ON t.tutor_id = tc.tutor_id
        WHERE tc.subject_id = :sid AND t.status = 'ACTIVE'
        ORDER BY t.tutor_id
    """), {"sid": sid}).fetchall()
    print(f"  Tutors with subject {sid}: {len(caps)}")
    for c in caps[:10]:
        print(f"    {c}")

db.close()

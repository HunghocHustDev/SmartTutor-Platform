# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\uni\2025.2\Database\SmartTutor-Platform\backend")
from app.database import create_session
from sqlalchemy import text
db = create_session()

print("=== ACTIVE Gò Vấp tutors with Vật lý Lớp 10 (subject 3), CN chiều, OFFLINE, not busy ===")
rows = db.execute(text("""
    SELECT t.tutor_id, t.full_name, t.area, t.experience_years,
           ta.day_of_week, ta.start_time, ta.end_time, ta.teaching_mode,
           (SELECT COUNT(*) FROM TUTOR_ASSIGNMENT ta2 WHERE ta2.tutor_id=t.tutor_id AND ta2.status='ASSIGNED') AS busy
    FROM TUTOR t
    JOIN TUTOR_CAPABILITY tc ON tc.tutor_id = t.tutor_id
    JOIN TUTOR_AVAILABILITY ta ON ta.tutor_id = t.tutor_id
    WHERE tc.subject_id = 3
      AND t.status = 'ACTIVE'
      AND ta.status = 'AVAILABLE'
      AND ta.teaching_mode IN ('BOTH', 'OFFLINE')
      AND ta.day_of_week = 7
      AND NOT EXISTS (
          SELECT 1 FROM TUTOR_ASSIGNMENT ta2
          WHERE ta2.tutor_id = t.tutor_id AND ta2.status = 'ASSIGNED'
      )
    ORDER BY t.experience_years DESC
""")).fetchall()
print(f"  Found: {len(rows)}")
for r in rows:
    print(f"  {r}")

print("\n=== TUTOR total ===")
print("  ", db.execute(text("SELECT COUNT(*) FROM TUTOR")).scalar())
print("  Last 5 tutors:")
for r in db.execute(text("SELECT TOP 5 tutor_id, full_name, status, area FROM TUTOR ORDER BY tutor_id DESC")).fetchall():
    print(f"    {r}")

db.close()

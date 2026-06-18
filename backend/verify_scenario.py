# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\uni\2025.2\Database\SmartTutor-Platform\backend")
from app.database import create_session
from sqlalchemy import text
from app.services.schedule_parser import parse_preferred_schedule, check_time_overlap

db = create_session()

print("=== Request #122 ===")
r = db.execute(text("""
    SELECT lr.request_id, lr.subject_id, su.subject_name, su.grade_level,
           lr.preferred_area, lr.preferred_mode, lr.preferred_schedule, lr.status
    FROM LEARNING_REQUEST lr
    JOIN SUBJECT su ON su.subject_id = lr.subject_id
    WHERE lr.request_id = 122
""")).fetchone()
print(f"  {r}")
parsed = parse_preferred_schedule(r[6])
print(f"  Parsed: days={parsed.days} start={parsed.start_time} end={parsed.end_time}")

print("\n  Matching tutors:")
rows = db.execute(text("""
    SELECT t.tutor_id, t.full_name, t.area, t.experience_years,
           ta.day_of_week, ta.start_time, ta.end_time, ta.teaching_mode
    FROM TUTOR t
    JOIN TUTOR_CAPABILITY tc ON tc.tutor_id = t.tutor_id
    JOIN TUTOR_AVAILABILITY ta ON ta.tutor_id = t.tutor_id
    WHERE tc.subject_id = :sid
      AND t.status = 'ACTIVE'
      AND ta.status = 'AVAILABLE'
      AND ta.teaching_mode IN ('BOTH', 'OFFLINE')
      AND NOT EXISTS (SELECT 1 FROM TUTOR_ASSIGNMENT ta2 WHERE ta2.tutor_id=t.tutor_id AND ta2.status='ASSIGNED')
    ORDER BY t.tutor_id
"""), {"sid": r[1]}).fetchall()
for row in rows:
    tid, name, area, exp, dow, st, et, mode = row
    if dow not in parsed.days:
        continue
    has_ov, mins = check_time_overlap(parsed.start_time, parsed.end_time, st, et)
    if not has_ov:
        continue
    score = exp * 10
    if area == r[4]: score += 20
    if mode == 'BOTH': score += 10
    if mins >= 90: score += 20
    elif mins >= 60: score += 10
    print(f"    Tutor #{tid} {name} | {area} | {exp}y | T{dow} {st}-{et} | {mode} | score={score}")

print("\n=== Request #124 ===")
r = db.execute(text("""
    SELECT lr.request_id, lr.subject_id, su.subject_name, su.grade_level,
           lr.preferred_area, lr.preferred_mode, lr.preferred_schedule, lr.status
    FROM LEARNING_REQUEST lr
    JOIN SUBJECT su ON su.subject_id = lr.subject_id
    WHERE lr.request_id = 124
""")).fetchone()
print(f"  {r}")
parsed = parse_preferred_schedule(r[6])
print(f"  Parsed: days={parsed.days} start={parsed.start_time} end={parsed.end_time}")

print("\n  Matching tutors:")
rows = db.execute(text("""
    SELECT t.tutor_id, t.full_name, t.area, t.experience_years,
           ta.day_of_week, ta.start_time, ta.end_time, ta.teaching_mode
    FROM TUTOR t
    JOIN TUTOR_CAPABILITY tc ON tc.tutor_id = t.tutor_id
    JOIN TUTOR_AVAILABILITY ta ON ta.tutor_id = t.tutor_id
    WHERE tc.subject_id = :sid
      AND t.status = 'ACTIVE'
      AND ta.status = 'AVAILABLE'
      AND ta.teaching_mode IN ('BOTH', 'OFFLINE')
      AND NOT EXISTS (SELECT 1 FROM TUTOR_ASSIGNMENT ta2 WHERE ta2.tutor_id=t.tutor_id AND ta2.status='ASSIGNED')
    ORDER BY t.tutor_id
"""), {"sid": r[1]}).fetchall()
for row in rows:
    tid, name, area, exp, dow, st, et, mode = row
    if dow not in parsed.days:
        continue
    has_ov, mins = check_time_overlap(parsed.start_time, parsed.end_time, st, et)
    if not has_ov:
        continue
    score = exp * 10
    if area == r[4]: score += 20
    if mode == 'BOTH': score += 10
    print(f"    Tutor #{tid} {name} | {area} | {exp}y | CN {st}-{et} | {mode} | score={score}")

db.close()
print("\n✅ Done")

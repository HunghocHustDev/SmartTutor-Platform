# -*- coding: utf-8 -*-
"""Check which PENDING requests have matching tutors."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\uni\2025.2\Database\SmartTutor-Platform\backend")
from app.database import create_session
from sqlalchemy import text
from app.services.schedule_parser import parse_preferred_schedule, check_time_overlap

db = create_session()

# For each PENDING request, check if there's at least 1 ACTIVE tutor
# with matching subject, not busy, with schedule overlap
pending = db.execute(text("""
    SELECT lr.request_id, lr.student_id, lr.subject_id, lr.preferred_area,
           lr.preferred_mode, lr.preferred_schedule, lr.status
    FROM LEARNING_REQUEST lr
    WHERE lr.status = 'PENDING'
    ORDER BY lr.request_id
""")).fetchall()

for req in pending:
    rid, sid, area, mode, sched = req[0], req[2], req[3], req[4], req[5]
    parsed = parse_preferred_schedule(sched)

    # Find matching tutors
    rows = db.execute(text("""
        SELECT t.tutor_id, t.full_name, t.status, t.area,
               ta.day_of_week, ta.start_time, ta.end_time, ta.teaching_mode
        FROM TUTOR t
        JOIN TUTOR_CAPABILITY tc ON tc.tutor_id = t.tutor_id
        JOIN TUTOR_AVAILABILITY ta ON ta.tutor_id = t.tutor_id
        WHERE tc.subject_id = :sid
          AND t.status = 'ACTIVE'
          AND ta.status = 'AVAILABLE'
          AND ta.teaching_mode IN ('BOTH', COALESCE(:mode, 'OFFLINE'))
          AND NOT EXISTS (
              SELECT 1 FROM TUTOR_ASSIGNMENT ta2
              WHERE ta2.tutor_id = t.tutor_id AND ta2.status = 'ASSIGNED'
          )
    """), {"sid": sid, "mode": mode}).fetchall()

    matching = []
    for r in rows:
        if parsed.has_time() and parsed.days:
            if r[4] not in parsed.days:
                continue
            has_ov, _ = check_time_overlap(parsed.start_time, parsed.end_time, r[5], r[6])
            if not has_ov:
                continue
        matching.append(r)

    status = f"✓ {len(matching)} matches" if matching else "✗ 0 matches"
    print(f"  Req#{rid}: subject={sid} area={area} mode={mode} sched='{sched}' → {status}")
    for m in matching[:3]:
        print(f"    Tutor #{m[0]} {m[1]} | {m[3]} | day={m[4]} {m[5]}-{m[6]} mode={m[7]}")

db.close()

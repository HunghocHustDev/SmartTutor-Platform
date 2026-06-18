# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from app.database import create_session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

db = create_session()
conn = db.connection()

# Find an assignment_id not in STUDY_CLASS
row = conn.execute(text("""
    SELECT ta.assignment_id FROM TUTOR_ASSIGNMENT ta
    LEFT JOIN STUDY_CLASS sc ON sc.assignment_id = ta.assignment_id
    WHERE sc.class_id IS NULL
""")).fetchone()
print('Test assignment_id:', row[0] if row else 'NONE')

if row:
    try:
        conn.execute(text("""
            INSERT INTO STUDY_CLASS (assignment_id, class_code, tuition_fee_per_session,
                teaching_mode, location, start_date, end_date, status, created_at)
            VALUES (:aid, :cc, :fee, :tm, :loc, :sd, :ed, :st, :ts)
        """), {
            "aid": row[0], "cc": "CLS-TEST-INSERT",
            "fee": 200000, "tm": "OFFLINE",
            "loc": "Hà Nội", "sd": "2025-06-01", "ed": "2025-08-01",
            "st": "ACTIVE", "ts": "2025-01-01 10:00:00"
        })
        conn.commit()
        print('INSERT OK')
    except IntegrityError as e:
        conn.rollback()
        print('INTEGRITY ERROR:', str(e)[:300])
    except Exception as e:
        conn.rollback()
        print('ERROR:', str(e)[:300])

db.close()

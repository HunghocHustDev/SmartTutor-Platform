# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from app.database import create_session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

db = create_session()
conn = db.connection()

# Query the actual constraint definition
row = conn.execute(text("""
    SELECT cc.name, cc.definition
    FROM sys.check_constraints cc
    JOIN sys.tables t ON t.object_id = cc.parent_object_id
    WHERE t.name = 'STUDY_CLASS' AND cc.name = 'CK_STUDY_CLASS_MODE'
""")).fetchone()
print('CK_STUDY_CLASS_MODE definition:', row[1] if row else 'NOT FOUND')

# Show existing STUDY_CLASS rows to see what's there
print('\nExisting STUDY_CLASS rows:')
for r in conn.execute(text('SELECT class_id, assignment_id, teaching_mode FROM STUDY_CLASS ORDER BY class_id')).fetchall():
    print(' ', r)

# Try inserting just 'OFFLINE' first to confirm basic insert works
row2 = conn.execute(text("""
    SELECT ta.assignment_id FROM TUTOR_ASSIGNMENT ta
    LEFT JOIN STUDY_CLASS sc ON sc.assignment_id = ta.assignment_id
    WHERE sc.class_id IS NULL
""")).fetchone()
if row2:
    try:
        conn.execute(text("""
            INSERT INTO STUDY_CLASS (assignment_id, class_code, tuition_fee_per_session,
                teaching_mode, location, start_date, end_date, status, created_at)
            VALUES (:aid, :cc, :fee, :tm, :loc, :sd, :ed, :st, :ts)
        """), {
            "aid": row2[0], "cc": "CLS-TEST-OFFLINE",
            "fee": 200000, "tm": "OFFLINE",
            "loc": "Hà Nội", "sd": "2025-06-01", "ed": "2025-08-01",
            "st": "ACTIVE", "ts": "2025-01-01 10:00:00"
        })
        conn.commit()
        print('\nINSERT OFFLINE OK')
    except Exception as e:
        conn.rollback()
        print('OFFLINE INSERT ERROR:', str(e)[:300])

db.close()

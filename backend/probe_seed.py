# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from app.database import create_session
from sqlalchemy import text
db = create_session()
print('STUDY_CLASS total:', db.execute(text('SELECT COUNT(*) FROM STUDY_CLASS')).scalar())
print('SEED class codes:', db.execute(text("SELECT COUNT(*) FROM STUDY_CLASS WHERE class_code LIKE 'CLS-SEED%'")).scalar())
print('ASSIGNED without class:')
rows = db.execute(text("""
    SELECT ta.assignment_id FROM TUTOR_ASSIGNMENT ta
    LEFT JOIN STUDY_CLASS sc ON sc.assignment_id=ta.assignment_id
    WHERE ta.status='ASSIGNED' AND sc.class_id IS NULL
""")).fetchall()
print(' ', len(rows), [r[0] for r in rows[:5]])
print('Last 5 STUDY_CLASS:')
for row in db.execute(text('SELECT TOP 5 class_id, assignment_id, class_code, teaching_mode FROM STUDY_CLASS ORDER BY class_id DESC')).fetchall():
    print(' ', row)
db.close()

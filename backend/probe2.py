# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from app.database import create_session
from sqlalchemy import text
db = create_session()

# existing classes
for r in db.execute(text('SELECT assignment_id, class_code, teaching_mode FROM STUDY_CLASS ORDER BY assignment_id')).fetchall():
    print('EXIST', r)

# available assignments (no class yet)
print('\nAvailable assignments:')
for r in db.execute(text("""
    SELECT ta.assignment_id, ta.status FROM TUTOR_ASSIGNMENT ta
    LEFT JOIN STUDY_CLASS sc ON sc.assignment_id = ta.assignment_id
    WHERE sc.class_id IS NULL ORDER BY ta.assignment_id
""")).fetchall():
    print(' ', r)

db.close()

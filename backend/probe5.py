# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from app.database import create_session
from sqlalchemy import text
db = create_session()
# check assignments without class
rows = db.execute(text("""
    SELECT ta.assignment_id, ta.status, ta.request_id
    FROM TUTOR_ASSIGNMENT ta
    LEFT JOIN STUDY_CLASS sc ON sc.assignment_id = ta.assignment_id
    WHERE sc.class_id IS NULL
    ORDER BY ta.assignment_id
""")).fetchall()
print('Assignments without class:', len(rows))
for r in rows:
    print(' ', r)
db.close()

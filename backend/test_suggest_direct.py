# -*- coding: utf-8 -*-
"""Call actual suggest_tutors_for_request service directly."""
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\uni\2025.2\Database\SmartTutor-Platform\backend")
from app.database import create_session
from app.services.request_flow_service import suggest_tutors_for_request

db = create_session()
try:
    for req_id in [122, 124]:
        print(f"\n=== Request #{req_id} ===")
        result = suggest_tutors_for_request(db, req_id)
        sugs = result.get('suggestions', [])
        print(f"  Subject: {result.get('subject_id')}")
        print(f"  Schedule: {result.get('request_schedule')}")
        print(f"  → {len(sugs)} suggestions")
        for s in sugs[:5]:
            print(f"    Tutor #{s['tutor_id']} {s['full_name']} | score={s['score']} | {s['area']} | {s['experience_years']}y | classes={s['current_classes']}/{s['max_classes']}")
            print(f"      reasons: {s['match_reasons']}")
            print(f"      availability: {s['availability'][:3]}")
finally:
    db.close()

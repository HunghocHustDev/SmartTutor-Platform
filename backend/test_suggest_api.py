# -*- coding: utf-8 -*-
import sys, io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\uni\2025.2\Database\SmartTutor-Platform\backend")
from app.database import create_session
from app.services.request_flow_service import suggest_tutors_for_request
from sqlalchemy.orm import Session

db = create_session()
try:
    for req_id in [122, 124]:
        print(f"\n=== Request #{req_id} suggestions ===")
        result = suggest_tutors_for_request(db, req_id)
        sugs = result.get('suggestions', []) if isinstance(result, dict) else []
        print(f"  → {len(sugs)} suggestions")
        for s in sugs[:5]:
            print(f"    Tutor #{s.get('tutor_id')} {s.get('full_name')} | score={s.get('score')} | {s.get('area')} | {s.get('experience_years')}y")
            print(f"      reasons: {s.get('match_reasons', [])}")
finally:
    db.close()

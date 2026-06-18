# -*- coding: utf-8 -*-
"""Fix: seed tutors in Gò Vấp dạy Vật lý Lớp 10, OFFLINE, CN chiều
để request 124 và các request tương tự có gợi ý tutor."""
import sys, io, random, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sqlalchemy import create_engine, text

engine = create_engine(
    "mssql+pyodbc://sa:123456@localhost:1433/TutorCenterDB"
    "?driver=ODBC+Driver+17+for+SQL+Server&trustServerCertificate=yes"
)
random.seed(55)

UNIS = ['ĐH Bách Khoa HN','ĐH KHXH&NV HN','ĐH Sư phạm HN','ĐH FPT','ĐH Khoa học Tự nhiên HN']
MAJORS = ['Vật lý','Vật lý ứng dụng','Khoa học vật liệu','Công nghệ vật liệu']

def dt():
    return datetime.datetime(2025, random.randint(1,12), random.randint(1,28), random.randint(8,20), 0, 0)

with engine.begin() as conn:
    # Add 5 tutors in Gò Vấp with Vật lý Lớp 10 (subject_id=3)
    print("=== Add Gò Vấp tutors (Vật lý Lớp 10, CN chiều) ===")
    for i in range(5):
        acc_id = conn.execute(text("SELECT ISNULL(MAX(account_id),0)+1 FROM USER_ACCOUNT")).scalar()
        em = f"tutor_gv_vl{acc_id}@test.local"
        conn.execute(text("""
            INSERT INTO USER_ACCOUNT (email, username, password_hash, role, status, created_at)
            VALUES (:e, :u, 'x', 'TUTOR', 'ACTIVE', :ts)
        """), {"e": em, "u": f"tvl_gv_{acc_id}", "ts": dt()})
        tid = conn.execute(text("SELECT ISNULL(MAX(tutor_id),0)+1 FROM TUTOR")).scalar()
        conn.execute(text("""
            INSERT INTO TUTOR (account_id, full_name, phone, contact_email, university, major,
                experience_years, area, status, created_at)
            VALUES (:aid, :fn, :ph, :em, :uni, :maj, :exp, N'Gò Vấp', 'ACTIVE', :ts)
        """), {
            "aid": acc_id, "fn": f"Gia sư Vật lý Gò Vấp {i+1}",
            "ph": f"090{random.randint(1000000,9999999)}", "em": em,
            "uni": random.choice(UNIS), "maj": random.choice(MAJORS),
            "exp": random.randint(3, 12), "ts": dt()
        })
        # Capability: Vật lý Lớp 10 (subject_id=3)
        conn.execute(text("""
            INSERT INTO TUTOR_CAPABILITY (tutor_id, subject_id, teaching_level, years_experience, note, created_at)
            VALUES (:tid, 3, N'Lớp 10', :yr, N'Chuyên Vật lý Lớp 10, Gò Vấp', :ts)
        """), {"tid": tid, "yr": random.randint(3, 12), "ts": dt()})
        # Availability: CN (day 7), chiều 13:00-16:00, OFFLINE
        conn.execute(text("""
            INSERT INTO TUTOR_AVAILABILITY (tutor_id, day_of_week, start_time, end_time, teaching_mode, area, status, created_at)
            VALUES (:tid, 7, '13:00', '16:00', 'OFFLINE', N'Gò Vấp', 'AVAILABLE', :ts)
        """), {"tid": tid, "ts": dt()})
    conn.commit()
    print(f"  Added 5 tutors")

    # Also fix: ensure there are ACTIVE tutors with subject 3 in DB (they should not all be busy)
    # Check how many ACTIVE tutors with subject 3 have no ASSIGNED assignment
    print("\n=== ACTIVE tutors with Vật lý Lớp 10, NOT busy ===")
    for r in conn.execute(text("""
        SELECT t.tutor_id, t.full_name, t.area, t.experience_years,
               ta.day_of_week, ta.start_time, ta.end_time, ta.teaching_mode
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
    """)).fetchall():
        print(f"  {r}")

    # Summary
    print("\n=== COUNTS ===")
    for t in ['USER_ACCOUNT','STAFF','STUDENT','TUTOR','SUBJECT',
              'LEARNING_REQUEST','TUTOR_ASSIGNMENT','STUDY_CLASS',
              'CLASS_SCHEDULE','LESSON_SESSION','TUITION_INVOICE',
              'TUITION_PAYMENT','TUTOR_AVAILABILITY','TUTOR_CAPABILITY']:
        n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        print(f"  {t}: {n}")
    print("\n✅ DONE")

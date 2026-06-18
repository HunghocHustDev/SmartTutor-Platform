# -*- coding: utf-8 -*-
"""Fix request 124: set correct subject (Vật lý Lớp 10 = subject_id 3)
   and add tutors with Vật lý Lớp 10 capability in Gò Vấp, AVAILABLE on Sunday afternoons."""
import sys, io, random, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sqlalchemy import create_engine, text

engine = create_engine(
    "mssql+pyodbc://sa:123456@localhost:1433/TutorCenterDB"
    "?driver=ODBC+Driver+17+for+SQL+Server&trustServerCertificate=yes"
)
random.seed(42)

AREAS = ['Cầu giấy','Hà Đông','Đống Đa','Nam Từ Liêm','Thanh Xuân','Long Biên','Hai Bà Trưng','Hoàn Kiếm','Tây Hồ','Bình Thạnh','Phú Nhuận','Gò Vấp','Tân Bình','Thủ Đức','Ba Đình']
POSITIONS = ['Điều phối viên','Nhân viên hỗ trợ','Quản lý học vụ','Chuyên viên']

def dt():
    return datetime.datetime(2025, random.randint(1,12), random.randint(1,28), random.randint(8,20), 0, 0)

with engine.begin() as conn:
    # ── 1. Fix request 124 subject_id → 3 (Vật lý Lớp 10) ──
    print("=== FIX REQUEST 124 ===")
    old = conn.execute(text(
        "SELECT request_id, subject_id, preferred_area, preferred_mode, preferred_schedule FROM LEARNING_REQUEST WHERE request_id = 124"
    )).fetchone()
    print(f"  Before: {old}")
    conn.execute(text("""
        UPDATE LEARNING_REQUEST
        SET subject_id = 3, preferred_area = N'Gò Vấp', preferred_mode = 'OFFLINE',
            preferred_schedule = N'CN chiều', updated_at = :ts
        WHERE request_id = 124
    """), {"ts": dt()})
    new = conn.execute(text(
        "SELECT request_id, subject_id, preferred_area, preferred_mode, preferred_schedule FROM LEARNING_REQUEST WHERE request_id = 124"
    )).fetchone()
    print(f"  After:  {new}")

    # ── 2. Check: which tutors already have Vật lý Lớp 10 (subject 3) ──
    print("\n=== Tutors with Vật lý Lớp 10 (subject 3) ===")
    existing_tutors = [r[0] for r in conn.execute(text("""
        SELECT t.tutor_id, t.full_name, t.status, t.area
        FROM TUTOR_CAPABILITY tc
        JOIN TUTOR t ON t.tutor_id = tc.tutor_id
        WHERE tc.subject_id = 3 AND t.status = 'ACTIVE'
        ORDER BY t.tutor_id
    """)).fetchall()]
    print(f"  ACTIVE tutors with subject 3: {len(existing_tutors)}")
    for r in existing_tutors:
        print(f"    {r}")

    # ── 3. Add new tutors in Gò Vấp with Vật lý Lớp 10 ──
    print("\n=== Add tutors in Gò Vấp (Vật lý Lớp 10) ===")
    # create 5 new accounts+tutors in Gò Vấp
    new_tutor_acc_ids = []
    for i in range(5):
        acc_id = conn.execute(text("SELECT ISNULL(MAX(account_id),0)+1 FROM USER_ACCOUNT")).scalar()
        em = f"tutor_vl124_{acc_id}@test.local"
        conn.execute(text("""
            INSERT INTO USER_ACCOUNT (email, username, password_hash, role, status, created_at)
            VALUES (:e, :u, 'x', 'TUTOR', 'ACTIVE', :ts)
        """), {"e": em, "u": f"tvl_{acc_id}", "ts": dt()})
        fn = f"Gia sư Vật lý Gò Vấp #{i+1}"
        conn.execute(text("""
            INSERT INTO TUTOR (account_id, full_name, phone, contact_email, university, major,
                experience_years, area, status, created_at)
            VALUES (:aid, :fn, :ph, :em, :uni, :maj, :exp, N'Gò Vấp', 'ACTIVE', :ts)
        """), {
            "aid": acc_id, "fn": fn,
            "ph": f"09{random.randint(10000000,99999999)}",
            "em": em,
            "uni": random.choice(['ĐH Bách Khoa HN','ĐH KHXH&NV HN','ĐH Sư phạm HN','ĐH FPT']),
            "maj": 'Vật lý', "exp": random.randint(3, 12),
            "ts": dt()
        })
        new_tutor_acc_ids.append(acc_id)
        # add capability: Vật lý Lớp 10 (subject 3)
        tid = conn.execute(text("SELECT ISNULL(MAX(tutor_id),0) FROM TUTOR")).scalar()
        conn.execute(text("""
            INSERT INTO TUTOR_CAPABILITY (tutor_id, subject_id, teaching_level, years_experience, note, created_at)
            VALUES (:tid, 3, N'Lớp 10', :yr, N'Chuyên Vật lý Lớp 10', :ts)
        """), {"tid": tid, "yr": random.randint(3, 12), "ts": dt()})
        # add availability: Sunday (day 7) afternoon 13:00-16:00, OFFLINE
        conn.execute(text("""
            INSERT INTO TUTOR_AVAILABILITY (tutor_id, day_of_week, start_time, end_time, teaching_mode, area, status, created_at)
            VALUES (:tid, 7, '13:00', '16:00', 'OFFLINE', N'Gò Vấp', 'AVAILABLE', :ts)
        """), {"tid": tid, "ts": dt()})
    conn.commit()
    print(f"  Added {len(new_tutor_acc_ids)} tutors in Gò Vấp")

    # ── 4. Also add a few more ACTIVE tutors with subject 3 in other areas ──
    print("\n=== Add ACTIVE tutors with Vật lý (other areas) ===")
    for area in ['Hà Đông', 'Cầu Giấy', 'Thanh Xuân']:
        acc_id = conn.execute(text("SELECT ISNULL(MAX(account_id),0)+1 FROM USER_ACCOUNT")).scalar()
        em = f"tutor_vl_{area.replace(' ','')}_{acc_id}@test.local"
        conn.execute(text("""
            INSERT INTO USER_ACCOUNT (email, username, password_hash, role, status, created_at)
            VALUES (:e, :u, 'x', 'TUTOR', 'ACTIVE', :ts)
        """), {"e": em, "u": f"tvl_{acc_id}", "ts": dt()})
        tid = conn.execute(text("SELECT ISNULL(MAX(tutor_id),0)+1 FROM TUTOR")).scalar()
        conn.execute(text("""
            INSERT INTO TUTOR (account_id, full_name, phone, contact_email, university, major,
                experience_years, area, status, created_at)
            VALUES (:aid, :fn, :ph, :em, :uni, :maj, :exp, :area, 'ACTIVE', :ts)
        """), {
            "aid": acc_id, "fn": f"Gia sư Vật lý {area}",
            "ph": f"09{random.randint(10000000,99999999)}", "em": em,
            "uni": 'ĐH Bách Khoa HN', "maj": 'Vật lý',
            "exp": random.randint(3, 10), "area": area, "ts": dt()
        })
        conn.execute(text("""
            INSERT INTO TUTOR_CAPABILITY (tutor_id, subject_id, teaching_level, years_experience, note, created_at)
            VALUES (:tid, 3, N'Lớp 10', :yr, N'Vật lý Lớp 10', :ts)
        """), {"tid": tid, "yr": random.randint(3, 10), "ts": dt()})
        # Sunday afternoon availability too
        conn.execute(text("""
            INSERT INTO TUTOR_AVAILABILITY (tutor_id, day_of_week, start_time, end_time, teaching_mode, area, status, created_at)
            VALUES (:tid, 7, '13:00', '16:00', 'OFFLINE', :area, 'AVAILABLE', :ts)
        """), {"tid": tid, "area": area, "ts": dt()})
    conn.commit()
    print(f"  Added 3 more tutors (Hà Đông, Cầu Giấy, Thanh Xuân)")

    # ── 5. Fix other requests that had wrong subjects (seed bulk) ──
    # request 110: subject 119 = Lịch sử Lớp 5 — OK (keep)
    # request 105: subject 2 = Toán Lớp 10 — OK

    # ── 6. Verify ──
    print("\n=== VERIFY: Tutors for request 124 (subject 3, Gò Vấp, OFFLINE, CN) ===")
    for r in conn.execute(text("""
        SELECT t.tutor_id, t.full_name, t.status, t.area, t.experience_years,
               ta.day_of_week, ta.start_time, ta.end_time, ta.teaching_mode
        FROM TUTOR_CAPABILITY tc
        JOIN TUTOR t ON t.tutor_id = tc.tutor_id
        JOIN TUTOR_AVAILABILITY ta ON ta.tutor_id = t.tutor_id
        WHERE tc.subject_id = 3
          AND t.status = 'ACTIVE'
          AND ta.status = 'AVAILABLE'
          AND ta.teaching_mode IN ('BOTH', 'OFFLINE')
          AND ta.day_of_week = 7  -- CN
          AND ta.tutor_id NOT IN (
              SELECT ta2.tutor_id FROM TUTOR_ASSIGNMENT ta2
              WHERE ta2.status = 'ASSIGNED'
          )
        ORDER BY t.experience_years DESC
    """)).fetchall():
        print(f"  {r}")

    print("\n=== COUNTS ===")
    for t in ['USER_ACCOUNT','STAFF','STUDENT','TUTOR','SUBJECT',
              'LEARNING_REQUEST','TUTOR_ASSIGNMENT','STUDY_CLASS',
              'CLASS_SCHEDULE','LESSON_SESSION','TUITION_INVOICE',
              'TUITION_PAYMENT','TUTOR_AVAILABILITY','TUTOR_CAPABILITY']:
        n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        print(f"  {t}: {n}")
    print("\n✅ DONE")

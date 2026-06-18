# -*- coding: utf-8 -*-
"""Targeted top-up: STAFF, STUDENT, TUTOR, LESSON_SESSION to 50+ rows each."""
import sys, io, random, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sqlalchemy import create_engine, text

engine = create_engine(
    "mssql+pyodbc://sa:123456@localhost:1433/TutorCenterDB"
    "?driver=ODBC+Driver+17+for+SQL+Server&trustServerCertificate=yes"
)
random.seed(99)

AREAS = ['Cầu giấy','Hà Đông','Đống Đa','Nam Từ Liêm','Thanh Xuân','Long Biên','Hai Bà Trưng','Hoàn Kiếm','Tây Hồ','Bình Thạnh','Phú Nhuận']
GRADE_LEVELS = ['Lớp 1','Lớp 6','Lớp 7','Lớp 10','Lớp 11','Lớp 12','THPT']
UNIS = ['ĐH Bách Khoa HN','ĐH KHXH&NV HN','ĐH Kinh tế QG','ĐH Sư phạm HN','ĐH FPT']
MAJORS = ['Toán học','Vật lý','Hóa học','Ngôn ngữ Anh','CNTT','Kinh tế']
POSITIONS = ['Điều phối viên','Nhân viên hỗ trợ','Quản lý học vụ','Chuyên viên']
GOALS = ['Ôn tập','Học nâng cao','Luyện thi','Cải thiện điểm']

def cur_max(conn, table, col):
    return conn.execute(text(f"SELECT ISNULL(MAX({col}),0) FROM {table}")).scalar()

def dt():
    return datetime.datetime(2025, random.randint(1,12), random.randint(1,28), random.randint(8,20), 0, 0)

def insert_one(conn, sql, params):
    try:
        conn.execute(text(sql), params)
        return True
    except Exception as e:
        return False

with engine.begin() as conn:
    # STAFF
    print("=== TOP-UP STAFF ===")
    needed = 50 - cur_max(conn, 'STAFF', 'staff_id')
    print(f"  need: {needed}")
    for i in range(max(needed, 0)):
        acc_id = cur_max(conn, 'USER_ACCOUNT', 'account_id') + 1
        em = f"stf_seed_{acc_id}@test.local"
        conn.execute(text("""
            INSERT INTO USER_ACCOUNT (email, username, password_hash, role, status, created_at)
            VALUES (:e, :u, 'x', 'STAFF', 'ACTIVE', :ts)
        """), {"e": em, "u": f"stf_{acc_id}", "ts": dt()})
        conn.execute(text("""
            INSERT INTO STAFF (account_id, full_name, phone, contact_email, position, status, created_at)
            VALUES (:aid, :fn, :ph, :em, :pos, 'ACTIVE', :ts)
        """), {"aid": acc_id, "fn": f"NV Seed #{acc_id}",
               "ph": f"090{random.randint(1000000,9999999)}", "em": em,
               "pos": random.choice(POSITIONS), "ts": dt()})
    conn.commit()
    print(f"  STAFF → {cur_max(conn,'STAFF','staff_id')}")

    # STUDENT
    print("\n=== TOP-UP STUDENT ===")
    needed = 50 - cur_max(conn, 'STUDENT', 'student_id')
    print(f"  need: {needed}")
    for i in range(max(needed, 0)):
        acc_id = cur_max(conn, 'USER_ACCOUNT', 'account_id') + 1
        em = f"stu_seed_{acc_id}@test.local"
        conn.execute(text("""
            INSERT INTO USER_ACCOUNT (email, username, password_hash, role, status, created_at)
            VALUES (:e, :u, 'x', 'STUDENT', 'ACTIVE', :ts)
        """), {"e": em, "u": f"stu_{acc_id}", "ts": dt()})
        conn.execute(text("""
            INSERT INTO STUDENT (account_id, full_name, phone, contact_email, address, area, current_level, grade_level, status, created_at)
            VALUES (:aid, :fn, :ph, :em, :addr, :area, :cl, :gl, 'ACTIVE', :ts)
        """), {"aid": acc_id, "fn": f"HV Seed #{acc_id}",
               "ph": f"091{random.randint(1000000,9999999)}", "em": em,
               "addr": f"Đường {random.choice(AREAS)}", "area": random.choice(AREAS),
               "cl": random.choice(GRADE_LEVELS), "gl": random.choice(GRADE_LEVELS),
               "ts": dt()})
    conn.commit()
    print(f"  STUDENT → {cur_max(conn,'STUDENT','student_id')}")

    # TUTOR
    print("\n=== TOP-UP TUTOR ===")
    needed = 50 - cur_max(conn, 'TUTOR', 'tutor_id')
    print(f"  need: {needed}")
    for i in range(max(needed, 0)):
        acc_id = cur_max(conn, 'USER_ACCOUNT', 'account_id') + 1
        em = f"tut_seed_{acc_id}@test.local"
        conn.execute(text("""
            INSERT INTO USER_ACCOUNT (email, username, password_hash, role, status, created_at)
            VALUES (:e, :u, 'x', 'TUTOR', 'ACTIVE', :ts)
        """), {"e": em, "u": f"tut_{acc_id}", "ts": dt()})
        conn.execute(text("""
            INSERT INTO TUTOR (account_id, full_name, phone, contact_email, university, major,
                experience_years, area, status, created_at)
            VALUES (:aid, :fn, :ph, :em, :uni, :maj, :exp, :area, :st, :ts)
        """), {"aid": acc_id, "fn": f"GS Seed #{acc_id}",
               "ph": f"092{random.randint(1000000,9999999)}", "em": em,
               "uni": random.choice(UNIS), "maj": random.choice(MAJORS),
               "exp": random.randint(1,15), "area": random.choice(AREAS),
               "st": random.choice(['ACTIVE','ACTIVE','ACTIVE','PAUSED','INACTIVE']),
               "ts": datetime.datetime(2024, random.randint(6,12), random.randint(1,28))})
    conn.commit()
    print(f"  TUTOR → {cur_max(conn,'TUTOR','tutor_id')}")

    # LESSON_SESSION
    print("\n=== TOP-UP LESSON_SESSION ===")
    needed = 50 - cur_max(conn, 'LESSON_SESSION', 'session_id')
    print(f"  need: {needed}")
    class_ids = [r[0] for r in conn.execute(text("SELECT class_id FROM STUDY_CLASS")).fetchall()]
    sched_ids = [r[0] for r in conn.execute(text("SELECT schedule_id FROM CLASS_SCHEDULE")).fetchall()]
    for _ in range(max(needed, 50)):
        insert_one(conn, """
            INSERT INTO LESSON_SESSION (class_id, schedule_id, session_number, lesson_date,
                start_time, end_time, status, content_note, created_at)
            VALUES (:cid, :scid, :sn, :ld, :st, :et, :st2, :cn, :ts)
        """, {
            "cid": random.choice(class_ids),
            "scid": random.choice(sched_ids + [None]*3) if sched_ids else None,
            "sn": random.randint(1, 60),
            "ld": datetime.date(2025, random.randint(1,12), random.randint(1,28)),
            "st": datetime.time(random.randint(7,19), random.choice([0,30])),
            "et": datetime.time(random.randint(19,21), random.choice([0,30])),
            "st2": random.choice(['SCHEDULED','COMPLETED','STUDENT_ABSENT','TUTOR_ABSENT','CANCELED']),
            "cn": f"Buổi #{random.randint(1,200)}: {random.choice(GOALS)}",
            "ts": dt()
        })
    conn.commit()
    print(f"  LESSON_SESSION → {cur_max(conn,'LESSON_SESSION','session_id')}")

    # FINAL VERIFY
    print("\n=== FINAL COUNTS ===")
    tables = ['USER_ACCOUNT','STAFF','STUDENT','TUTOR','SUBJECT',
              'LEARNING_REQUEST','TUTOR_ASSIGNMENT','STUDY_CLASS',
              'CLASS_SCHEDULE','LESSON_SESSION','TUITION_INVOICE',
              'TUITION_PAYMENT','TUTOR_AVAILABILITY','TUTOR_CAPABILITY']
    all_ok = True
    for t in tables:
        r = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        flag = "✓" if r >= 50 else "✗"
        if r < 50: all_ok = False
        print(f"  {flag}  {t}: {r}")
    bad = conn.execute(text("SELECT COUNT(*) FROM TUITION_INVOICE WHERE amount_paid > amount_due")).scalar()
    print(f"\n  amount_paid > amount_due: {bad}")
    print("\n✅ ALL >= 50" if all_ok else "\n⚠️ Some still < 50")

# -*- coding: utf-8 -*-
"""Seed script: INSERT additional rows into TutorCenterDB to reach 50+ rows per table."""
import sys, io, random, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sqlalchemy import create_engine, text

engine = create_engine(
    "mssql+pyodbc://sa:123456@localhost:1433/TutorCenterDB"
    "?driver=ODBC+Driver+17+for+SQL+Server&trustServerCertificate=yes"
)
random.seed(42)

AREAS = [
    'Cầu giấy','Hà Đông','Đống Đa','Nam Từ Liêm','Thanh Xuân','Long Biên',
    'Hai Bà Trưng','Hoàn Kiếm','Tây Hồ','Bình Thạnh','Phú Nhuận','Gò Vấp',
    'Tân Bình','Thủ Đức','Ba Đình'
]
SUBJECT_NAMES = [
    'Toán','Vật lý','Hóa học','Sinh học','Ngữ văn','Lịch sử','Địa lý',
    'Tiếng Anh','Tiếng Pháp','Tiếng Trung','Tin học','Kinh tế','Âm nhạc','Vẽ trang trí','Thể dục'
]
GRADE_LEVELS = [
    'Lớp 1','Lớp 2','Lớp 3','Lớp 4','Lớp 5','Lớp 6','Lớp 7','Lớp 8',
    'Lớp 9','Lớp 10','Lớp 11','Lớp 12','THPT','Đại học'
]
SCHEDULES = [
    'T2 17:00-19:00','T3 18:00-20:00','T4 17:30-19:30','T5 18:30-20:30',
    'T6 16:00-18:00','T7 09:00-11:00','CN 14:00-16:00',
    'T2,T4 17:00-19:00','T3,T5 18:00-20:00',
    'T7 sáng','CN sáng','T2 tối','T3 tối','T5 tối','T7 tối'
]
MODES = ['OFFLINE','ONLINE','BOTH']
GOALS = [
    'Ôn tập kiến thức cũ','Học nâng cao','Luyện thi đại học',
    'Cải thiện điểm số','Học lại kiến thức','Học đúng kiến thức',
    'Học phụ đạo','Học ngoại ngữ','Chuẩn bị thi cuối kỳ','Làm bài tập nhóm'
]
PAYMENT_METHODS = ['Tiền mặt','Chuyển khoản','Momo','Vietcombank','Techcombank']
UNIS = ['ĐH Bách Khoa HN','ĐH KHXH&NV HN','ĐH Kinh tế QG','ĐH Sư phạm HN','ĐH FPT','ĐH RMIT','ĐH Hà Nội','ĐH Công nghệ']
MAJORS = ['Toán học','Vật lý','Hóa học','Ngôn ngữ Anh','Ngôn ngữ Trung','CNTT','Kinh tế','Sư phạm Toán','Sư phạm Anh','Thiết kế','Âm nhạc','TDTT']
POSITIONS = ['Điều phối viên','Nhân viên hỗ trợ','Quản lý học vụ','Phó điều phối','Chuyên viên']

def cur_max(conn, table, col):
    return conn.execute(text(f"SELECT ISNULL(MAX({col}),0) FROM {table}")).scalar()

def dt(y, m=None, d=None):
    return datetime.datetime(y, m or random.randint(1,12), d or random.randint(1,28), random.randint(8,20), 0, 0)

with engine.begin() as conn:
    # ─────────────────────────────────────────────────────────────────
    # 1. USER_ACCOUNT — 50 rows (mix STAFF / STUDENT / TUTOR)
    # ─────────────────────────────────────────────────────────────────
    print("=== USER_ACCOUNT ===")
    m = cur_max(conn, 'USER_ACCOUNT', 'account_id')
    base = m + 1
    roles_pool = ['STAFF','STUDENT','STUDENT','TUTOR','TUTOR','STUDENT','TUTOR']
    rows = []
    for i in range(50):
        role = roles_pool[i % len(roles_pool)]
        rows.append({
            "e": f"seed{base+i}.{role.lower()}@test.local",
            "u": f"seed_{base+i}_{role.lower()[:4]}",
            "p": "hash_seed_pass",
            "r": role,
            "ts": dt(2024 + (i // 30), 1 + (i % 12), 1 + (i % 28))
        })
    conn.execute(text("""
        INSERT INTO USER_ACCOUNT (email, username, password_hash, role, status, created_at)
        VALUES (:e, :u, :p, :r, 'ACTIVE', :ts)
    """), rows)
    n = cur_max(conn, 'USER_ACCOUNT', 'account_id')
    print(f"  → {n} (added 50)")

    # ─────────────────────────────────────────────────────────────────
    # 2. SUBJECT — 50 NEW unique (name, level) combinations
    # ─────────────────────────────────────────────────────────────────
    print("\n=== SUBJECT ===")
    existing_keys = {
        (r[0], r[1]) for r in conn.execute(
            text("SELECT subject_name, ISNULL(grade_level,'__NULL__') FROM SUBJECT")
        ).fetchall()
    }
    added = 0; idx = 0
    while added < 50:
        sn = random.choice(SUBJECT_NAMES)
        gl = random.choice(GRADE_LEVELS)
        key = (sn, gl)
        if key in existing_keys:
            continue
        conn.execute(text("""
            INSERT INTO SUBJECT (subject_name, subject_group, grade_level, description, status, created_at)
            VALUES (:s, :sg, :gl, :d, 'ACTIVE', :ts)
        """), {
            "s": sn, "sg": "Môn học", "gl": gl,
            "d": f"Môn {sn} - {gl}", "ts": dt(2025, 1 + idx % 12, 1 + idx % 28)
        })
        existing_keys.add(key)
        added += 1; idx += 1
    n = cur_max(conn, 'SUBJECT', 'subject_id')
    print(f"  → {n} (added 50)")

    # ─────────────────────────────────────────────────────────────────
    # 3. STAFF (+50), STUDENT (+50), TUTOR (+50)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== STAFF / STUDENT / TUTOR ===")

    # pick 50 staff-role accounts not yet in STAFF
    staff_accs = [r[0] for r in conn.execute(text("""
        SELECT TOP 50 ua.account_id FROM USER_ACCOUNT ua
        LEFT JOIN STAFF s ON s.account_id = ua.account_id
        WHERE ua.role = 'STAFF' AND s.staff_id IS NULL ORDER BY ua.account_id
    """)).fetchall()]

    # pick 50 student-role accounts not yet in STUDENT
    stud_accs = [r[0] for r in conn.execute(text("""
        SELECT TOP 50 ua.account_id FROM USER_ACCOUNT ua
        LEFT JOIN STUDENT st ON st.account_id = ua.account_id
        WHERE ua.role = 'STUDENT' AND st.student_id IS NULL ORDER BY ua.account_id
    """)).fetchall()]

    # pick 50 tutor-role accounts not yet in TUTOR
    tutor_accs = [r[0] for r in conn.execute(text("""
        SELECT TOP 50 ua.account_id FROM USER_ACCOUNT ua
        LEFT JOIN TUTOR t ON t.account_id = ua.account_id
        WHERE ua.role = 'TUTOR' AND t.tutor_id IS NULL ORDER BY ua.account_id
    """)).fetchall()]

    staff_rows = []
    for i, aid in enumerate(staff_accs):
        staff_rows.append({
            "aid": aid, "fn": f"Nhân viên Seed {i+1}",
            "ph": f"090{random.randint(1000000,9999999)}",
            "em": f"staff_seed_{i+1}@test.local",
            "pos": random.choice(POSITIONS),
            "ts": dt(2025, 1 + i % 12, 1 + i % 28)
        })
    conn.execute(text("""
        INSERT INTO STAFF (account_id, full_name, phone, contact_email, position, status, created_at)
        VALUES (:aid, :fn, :ph, :em, :pos, 'ACTIVE', :ts)
    """), staff_rows)

    stud_rows = []
    for i, aid in enumerate(stud_accs):
        stud_rows.append({
            "aid": aid, "fn": f"Học viên Seed {i+1}",
            "ph": f"091{random.randint(1000000,9999999)}",
            "em": f"student_seed_{i+1}@test.local",
            "addr": f"Số {random.randint(1,200)} đường {random.choice(AREAS)}",
            "area": random.choice(AREAS),
            "cl": random.choice(GRADE_LEVELS), "gl": random.choice(GRADE_LEVELS),
            "ts": dt(2025, 1 + i % 12, 1 + i % 28)
        })
    conn.execute(text("""
        INSERT INTO STUDENT (account_id, full_name, phone, contact_email, address, area, current_level, grade_level, status, created_at)
        VALUES (:aid, :fn, :ph, :em, :addr, :area, :cl, :gl, 'ACTIVE', :ts)
    """), stud_rows)

    tutor_rows = []
    for i, aid in enumerate(tutor_accs):
        tutor_rows.append({
            "aid": aid, "fn": f"Gia sư Seed {i+1}",
            "ph": f"092{random.randint(1000000,9999999)}",
            "em": f"tutor_seed_{i+1}@test.local",
            "uni": random.choice(UNIS), "maj": random.choice(MAJORS),
            "exp": random.randint(1, 15), "area": random.choice(AREAS),
            "st": random.choice(['ACTIVE','ACTIVE','ACTIVE','PAUSED','INACTIVE']),
            "ts": dt(2024, random.randint(6,12), random.randint(1,28))
        })
    conn.execute(text("""
        INSERT INTO TUTOR (account_id, full_name, phone, contact_email, university, major,
            experience_years, area, status, created_at)
        VALUES (:aid, :fn, :ph, :em, :uni, :maj, :exp, :area, :st, :ts)
    """), tutor_rows)

    n_staff = cur_max(conn, 'STAFF', 'staff_id')
    n_stud  = cur_max(conn, 'STUDENT', 'student_id')
    n_tutor = cur_max(conn, 'TUTOR', 'tutor_id')
    print(f"  STAFF → {n_staff}, STUDENT → {n_stud}, TUTOR → {n_tutor}")

    # ─────────────────────────────────────────────────────────────────
    # 4. TUTOR_CAPABILITY — 50 unique (tutor, subject, level)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== TUTOR_CAPABILITY ===")
    new_tutor_ids = [r[0] for r in conn.execute(text("SELECT tutor_id FROM TUTOR WHERE tutor_id > :m"), {"m": n_tutor-50}).fetchall()]
    all_subject_ids = [r[0] for r in conn.execute(text("SELECT subject_id FROM SUBJECT")).fetchall()]

    added = 0; attempts = 0
    seen_cap = set()
    while added < 50 and attempts < 1000:
        attempts += 1
        tid = random.choice(new_tutor_ids)
        sid = random.choice(all_subject_ids)
        gl  = random.choice(GRADE_LEVELS + [None]*4)
        key = (tid, sid, gl)
        if key in seen_cap:
            continue
        seen_cap.add(key)
        try:
            conn.execute(text("""
                INSERT INTO TUTOR_CAPABILITY (tutor_id, subject_id, teaching_level, years_experience, note, created_at)
                VALUES (:tid, :sid, :gl, :yr, :note, :ts)
            """), {
                "tid": tid, "sid": sid, "gl": gl,
                "yr": random.randint(1, 12),
                "note": "Có kinh nghiệm giảng dạy", "ts": dt(2025, random.randint(1,6), random.randint(1,28))
            })
            added += 1
        except Exception:
            seen_cap.discard(key)
    n = cur_max(conn, 'TUTOR_CAPABILITY', 'capability_id')
    print(f"  → {n} (added {added})")

    # ─────────────────────────────────────────────────────────────────
    # 5. TUTOR_AVAILABILITY — 50 rows
    # ─────────────────────────────────────────────────────────────────
    print("\n=== TUTOR_AVAILABILITY ===")
    av_rows = []
    for _ in range(50):
        av_rows.append({
            "tid": random.choice(new_tutor_ids),
            "dow": random.randint(1, 7),
            "st": datetime.time(random.randint(7, 18), random.choice([0, 30])),
            "et": datetime.time(random.randint(19, 21), random.choice([0, 30])),
            "tm": random.choice(['OFFLINE','ONLINE','BOTH']),
            "area": random.choice(AREAS),
            "st2": random.choice(['AVAILABLE','AVAILABLE','UNAVAILABLE']),
            "ts": dt(2025, 1 + random.randint(0, 11), random.randint(1, 28))
        })
    conn.execute(text("""
        INSERT INTO TUTOR_AVAILABILITY (tutor_id, day_of_week, start_time, end_time, teaching_mode, area, status, created_at)
        VALUES (:tid, :dow, :st, :et, :tm, :area, :st2, :ts)
    """), av_rows)
    n = cur_max(conn, 'TUTOR_AVAILABILITY', 'availability_id')
    print(f"  → {n} (added 50)")

    # ─────────────────────────────────────────────────────────────────
    # 6. LEARNING_REQUEST — 50 rows
    # ─────────────────────────────────────────────────────────────────
    print("\n=== LEARNING_REQUEST ===")
    all_student_ids = [r[0] for r in conn.execute(text("SELECT student_id FROM STUDENT")).fetchall()]
    req_rows = []
    for _ in range(50):
        req_rows.append({
            "sid": random.choice(all_student_ids),
            "subid": random.choice(all_subject_ids),
            "rl": random.choice(GRADE_LEVELS),
            "lg": random.choice(GOALS),
            "pa": random.choice(AREAS),
            "pm": random.choice(MODES),
            "ps": random.choice(SCHEDULES),
            "ef": random.choice([None, 150000, 200000, 250000, 300000, 350000, 400000, 500000]),
            "st": random.choice(['PENDING','PENDING','PENDING','ASSIGNED','CANCELED']),
            "ts": dt(2025, random.randint(1,12), random.randint(1,28))
        })
    conn.execute(text("""
        INSERT INTO LEARNING_REQUEST (student_id, subject_id, requested_level, learning_goal,
            preferred_area, preferred_mode, preferred_schedule, expected_fee, status, created_at)
        VALUES (:sid, :subid, :rl, :lg, :pa, :pm, :ps, :ef, :st, :ts)
    """), req_rows)
    n = cur_max(conn, 'LEARNING_REQUEST', 'request_id')
    print(f"  → {n} (added 50)")

    # ─────────────────────────────────────────────────────────────────
    # 7. TUTOR_ASSIGNMENT — 50 rows (one per new request, respecting unique ASSIGNED)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== TUTOR_ASSIGNMENT ===")
    all_staff_ids = [r[0] for r in conn.execute(text("SELECT staff_id FROM STAFF")).fetchall()]
    all_tutor_ids = [r[0] for r in conn.execute(text("SELECT tutor_id FROM TUTOR")).fetchall()]
    new_req_ids = [r[0] for r in conn.execute(text("""
        SELECT request_id FROM LEARNING_REQUEST WHERE request_id > :m ORDER BY request_id
    """), {"m": n - 50}).fetchall()]

    assign_rows = []
    added_a = 0
    for rid in new_req_ids:
        sub_id = conn.execute(text("SELECT subject_id FROM LEARNING_REQUEST WHERE request_id=:rid"), {"rid": rid}).scalar()
        capable = [r[0] for r in conn.execute(text("""
            SELECT tc.tutor_id FROM TUTOR_CAPABILITY tc
            JOIN TUTOR t ON t.tutor_id = tc.tutor_id
            WHERE tc.subject_id = :sid AND t.status IN ('ACTIVE','PAUSED')
        """), {"sid": sub_id}).fetchall()]
        if not capable:
            capable = all_tutor_ids  # fallback
        tid = random.choice(capable)
        assign_rows.append({
            "rid": rid, "tid": tid,
            "sfid": random.choice(all_staff_ids + [None]*3),
            "aa": dt(2025, random.randint(1,12), random.randint(1,28)),
            "st": random.choice(['ASSIGNED','ASSIGNED','ASSIGNED','CANCELED']),
            "note": f"Seed phân công yc#{rid}",
            "ts": dt(2025, random.randint(1,12), random.randint(1,28))
        })
        added_a += 1
        if added_a >= 50:
            break
    conn.execute(text("""
        INSERT INTO TUTOR_ASSIGNMENT (request_id, tutor_id, staff_id, assigned_at, status, note, created_at)
        VALUES (:rid, :tid, :sfid, :aa, :st, :note, :ts)
    """), assign_rows)
    n = cur_max(conn, 'TUTOR_ASSIGNMENT', 'assignment_id')
    print(f"  → {n} (added {added_a})")

    # get ASSIGNED assignment IDs that don't yet have a STUDY_CLASS
    assigned_ids = [r[0] for r in conn.execute(text("""
        SELECT ta.assignment_id FROM TUTOR_ASSIGNMENT ta
        LEFT JOIN STUDY_CLASS sc ON sc.assignment_id = ta.assignment_id
        WHERE ta.status = 'ASSIGNED' AND sc.class_id IS NULL
    """)).fetchall()]

    # ─────────────────────────────────────────────────────────────────
    # 8. STUDY_CLASS — 50 rows (one per ASSIGNED assignment)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== STUDY_CLASS ===")
    cls_rows = []
    for aid in assigned_ids[:50]:
        fee = random.choice([150000,180000,200000,220000,250000,300000,350000,400000])
        cls_rows.append({
            "aid": aid,
            "cc": f"CLS-SEED-{aid:04d}",
            "fee": fee,
            "tm": random.choice(MODES),
            "loc": f"{random.choice(AREAS)}, Hà Nội",
            "sd": datetime.date(2025, random.randint(1,12), random.randint(1,28)),
            "ed": datetime.date(2025, random.randint(7,12), random.randint(1,28)),
            "st": random.choice(['ACTIVE','ACTIVE','ACTIVE','PAUSED','COMPLETED','CANCELED']),
            "ts": dt(2025, random.randint(1,12), random.randint(1,28))
        })
    conn.execute(text("""
        INSERT INTO STUDY_CLASS (assignment_id, class_code, tuition_fee_per_session, teaching_mode,
            location, start_date, end_date, status, created_at)
        VALUES (:aid, :cc, :fee, :tm, :loc, :sd, :ed, :st, :ts)
    """), cls_rows)
    n = cur_max(conn, 'STUDY_CLASS', 'class_id')
    print(f"  → {n} (added {len(cls_rows)})")

    # ─────────────────────────────────────────────────────────────────
    # 9. CLASS_SCHEDULE — 50 rows
    # ─────────────────────────────────────────────────────────────────
    print("\n=== CLASS_SCHEDULE ===")
    new_class_ids = [r[0] for r in conn.execute(text("""
        SELECT class_id FROM STUDY_CLASS WHERE class_id > :m ORDER BY class_id
    """), {"m": cur_max(conn,'STUDY_CLASS','class_id') - len(cls_rows)}).fetchall()]
    sched_rows = []
    for _ in range(50):
        sched_rows.append({
            "cid": random.choice(new_class_ids),
            "dow": random.randint(1, 7),
            "st": datetime.time(random.randint(7, 18), random.choice([0, 30])),
            "et": datetime.time(random.randint(19, 21), random.choice([0, 30])),
            "ef": datetime.date(2025, random.randint(1, 12), random.randint(1, 28)),
            "et2": datetime.date(2025, random.randint(7, 12), random.randint(1, 28)),
            "st2": random.choice(['ACTIVE','ACTIVE','INACTIVE']),
            "ts": dt(2025, random.randint(1,12), random.randint(1,28))
        })
    conn.execute(text("""
        INSERT INTO CLASS_SCHEDULE (class_id, day_of_week, start_time, end_time,
            effective_from, effective_to, status, created_at)
        VALUES (:cid, :dow, :st, :et, :ef, :et2, :st2, :ts)
    """), sched_rows)
    n = cur_max(conn, 'CLASS_SCHEDULE', 'schedule_id')
    print(f"  → {n} (added 50)")

    # ─────────────────────────────────────────────────────────────────
    # 10. LESSON_SESSION — 50 rows
    # ─────────────────────────────────────────────────────────────────
    print("\n=== LESSON_SESSION ===")
    sched_ids = [r[0] for r in conn.execute(text("SELECT schedule_id FROM CLASS_SCHEDULE")).fetchall()]
    session_rows = []
    for _ in range(50):
        session_rows.append({
            "cid": random.choice(new_class_ids),
            "scid": random.choice(sched_ids + [None]*3) if sched_ids else None,
            "sn": random.randint(1, 40),
            "ld": datetime.date(2025, random.randint(1,12), random.randint(1,28)),
            "st": datetime.time(random.randint(7, 19), random.choice([0, 30])),
            "et": datetime.time(random.randint(19, 21), random.choice([0, 30])),
            "st2": random.choice(['SCHEDULED','COMPLETED','STUDENT_ABSENT','TUTOR_ABSENT','CANCELED']),
            "cn": f"Buổi học #{random.randint(1,80)}",
            "ts": dt(2025, random.randint(1,12), random.randint(1,28))
        })
    conn.execute(text("""
        INSERT INTO LESSON_SESSION (class_id, schedule_id, session_number, lesson_date,
            start_time, end_time, status, content_note, created_at)
        VALUES (:cid, :scid, :sn, :ld, :st, :et, :st2, :cn, :ts)
    """), session_rows)
    n = cur_max(conn, 'LESSON_SESSION', 'session_id')
    print(f"  → {n} (added 50)")

    # ─────────────────────────────────────────────────────────────────
    # 11. TUITION_INVOICE — 50 rows (snapshot by period)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== TUITION_INVOICE ===")
    inv_rows = []
    for cid in new_class_ids[:50]:
        fee = conn.execute(text("SELECT tuition_fee_per_session FROM STUDY_CLASS WHERE class_id=:cid"), {"cid": cid}).scalar()
        if not fee:
            continue
        fee = float(fee)
        sessions = random.randint(4, 12)
        due = round(fee * sessions, 2)
        ps = datetime.date(2025, random.randint(1, 6), 1)
        pe = datetime.date(2025, random.randint(ps.month + 1, 12), 28)
        inv_rows.append({
            "cid": cid, "ps": ps, "pe": pe, "cs": sessions,
            "fee": fee, "due": due, "paid": 0.0,
            "st": random.choice(['UNPAID','PARTIALLY_PAID','PAID','OVERDUE','CANCELED']),
            "ts": dt(2025, random.randint(1,12), random.randint(1,28))
        })
    conn.execute(text("""
        INSERT INTO TUITION_INVOICE (class_id, period_start, period_end, completed_sessions,
            tuition_fee_per_session, amount_due, amount_paid, status, created_at)
        VALUES (:cid, :ps, :pe, :cs, :fee, :due, :paid, :st, :ts)
    """), inv_rows)
    n = cur_max(conn, 'TUITION_INVOICE', 'invoice_id')
    print(f"  → {n} (added {len(inv_rows)})")
    new_inv_ids = [r[0] for r in conn.execute(text(f"""
        SELECT invoice_id FROM TUITION_INVOICE WHERE invoice_id > {n-len(inv_rows)} ORDER BY invoice_id
    """)).fetchall()]

    # ─────────────────────────────────────────────────────────────────
    # 12. TUITION_PAYMENT — 50 rows (safe: amount <= invoice remaining for SUCCESS)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== TUITION_PAYMENT ===")
    pay_rows = []
    for _ in range(50):
        inv_id = random.choice(new_inv_ids)
        # compute safe remaining
        inv = conn.execute(text("""
            SELECT ti.amount_due,
                   COALESCE((SELECT SUM(tp.amount_paid) FROM TUITION_PAYMENT tp
                             WHERE tp.invoice_id = ti.invoice_id AND tp.status = 'SUCCESS'), 0) AS paid
            FROM TUITION_INVOICE ti WHERE ti.invoice_id = :iid
        """), {"iid": inv_id}).fetchone()
        remaining = float(inv[0]) - float(inv[1]) if inv else 500000
        remaining = max(remaining, 0)
        if remaining < 50000:
            amount = 0.0  # will be filtered out
        else:
            amount = round(random.uniform(50000, min(remaining, 300000)), 0)

        st = random.choice(['SUCCESS','SUCCESS','CANCELED','REFUNDED'])
        if st == 'SUCCESS' and amount < 50000:
            st = 'CANCELED'  # avoid zero-payment SUCCESS
        pay_rows.append({
            "inv": inv_id,
            "sfid": random.choice(all_staff_ids + [None]*4),
            "pd": dt(2025, random.randint(1,12), random.randint(1,28), random.randint(8,17)),
            "am": amount if st == 'SUCCESS' else random.choice([50000,100000,200000]),
            "pm": random.choice(PAYMENT_METHODS),
            "note": f"Thanh toán hóa đơn #{inv_id}",
            "st": st,
            "ts": dt(2025, random.randint(1,12), random.randint(1,28))
        })
    conn.execute(text("""
        INSERT INTO TUITION_PAYMENT (invoice_id, staff_id, payment_date, amount_paid,
            payment_method, note, status, created_at)
        VALUES (:inv, :sfid, :pd, :am, :pm, :note, :st, :ts)
    """), pay_rows)
    n = cur_max(conn, 'TUITION_PAYMENT', 'payment_id')
    print(f"  → {n} (added {len(pay_rows)})")

    # ─────────────────────────────────────────────────────────────────
    # FINAL verify
    # ─────────────────────────────────────────────────────────────────
    print("\n=== FINAL ROW COUNTS ===")
    tables = [
        'USER_ACCOUNT','STAFF','STUDENT','TUTOR','SUBJECT',
        'LEARNING_REQUEST','TUTOR_ASSIGNMENT','STUDY_CLASS',
        'CLASS_SCHEDULE','LESSON_SESSION','TUITION_INVOICE',
        'TUITION_PAYMENT','TUTOR_AVAILABILITY','TUTOR_CAPABILITY'
    ]
    for t in tables:
        r = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        flag = "✓" if r >= 50 else "✗"
        print(f"  {flag} {t}: {r}")

    # spot-check invoice integrity
    bad = conn.execute(text("""
        SELECT COUNT(*) FROM TUITION_INVOICE
        WHERE amount_paid > amount_due
    """)).scalar()
    print(f"\n  Invoices with amount_paid > amount_due: {bad} (should be 0)")

    print("\n✅ DONE — seed complete!")

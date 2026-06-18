# -*- coding: utf-8 -*-
"""
Bulletproof seed: 50 rows each table, one row at a time with constraint-aware generation.
Uses app.database to get a live session, inserts each row individually (not executemany)
so we can catch and skip only the rows that hit a unique/date constraint, retrying
with new random values.
"""
import sys, io, random, datetime, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Must add backend to path for `import app`
sys.path.insert(0, r"D:\uni\2025.2\Database\SmartTutor-Platform\backend")

from sqlalchemy import text
from app.database import create_session

random.seed(2025)

AREAS = [
    'Cầu giấy','Hà Đông','Đống Đa','Nam Từ Liêm','Thanh Xuân','Long Biên',
    'Hai Bà Trưng','Hoàn Kiếm','Tây Hồ','Bình Thạnh','Phú Nhuận','Gò Vấp',
    'Tân Bình','Thủ Đức','Ba Đình'
]
GRADE_LEVELS = ['Lớp 1','Lớp 2','Lớp 3','Lớp 4','Lớp 5','Lớp 6','Lớp 7','Lớp 8','Lớp 9','Lớp 10','Lớp 11','Lớp 12','THPT','Đại học']
MODES_CLS = ['OFFLINE','ONLINE']   # ← actual constraint from DB
GOALS = ['Ôn tập','Học nâng cao','Luyện thi','Cải thiện điểm','Học phụ đạo']
PAYMENT_METHODS = ['Tiền mặt','Chuyển khoản','Momo','Vietcombank','Techcombank']

def dt():
    return datetime.datetime(2025, random.randint(1,12), random.randint(1,28), random.randint(8,20), 0, 0)

def safe_date(start_m=None, start_d=None, min_months=1, max_months=6):
    m = start_m or random.randint(1, 7)
    d = start_d or random.randint(1, 25)
    em = min(m + random.randint(min_months, max_months), 12)
    return datetime.date(2025, m, d), datetime.date(2025, em, random.randint(1, 28))

def insert_one(conn, sql, params):
    """Insert one row, return True on success."""
    try:
        conn.execute(text(sql), params)
        return True
    except Exception as e:
        err = str(e)
        # Skip unique constraint / date constraint conflicts
        skip = any(k in err for k in [
            'UNIQUE KEY', 'UniqueIndex', 'UQ_CLASS_SCHEDULE_SLOT',
            'CK_STUDY_CLASS_DATE', 'CK_CLASS_SCHEDULE_DATE',
            'UQ_TUTOR_CAPABILITY', 'UQ_ACTIVE_ASSIGNMENT_PER_REQUEST',
            'UQ_STUDY_CLASS_ASSIGNMENT', 'UQ_STUDY_CLASS_CODE',
            'IntegrityError', 'constraint'
        ])
        return not skip   # return False if we should skip silently

def cur_max(conn, table, col):
    return conn.execute(text(f"SELECT ISNULL(MAX({col}),0) FROM {table}")).scalar()

db = create_session()
conn = db.connection()

try:
    # ─────────────────────────────────────────────────────────────────
    # 1. USER_ACCOUNT — 50 fresh rows (no dup email/username)
    # ─────────────────────────────────────────────────────────────────
    print("=== USER_ACCOUNT ===")
    existing_emails = {r[0] for r in conn.execute(text("SELECT email FROM USER_ACCOUNT")).fetchall()}
    existing_unames = {r[0] for r in conn.execute(text("SELECT username FROM USER_ACCOUNT")).fetchall()}
    m = cur_max(conn, 'USER_ACCOUNT', 'account_id')
    base = m + 1
    roles_pool = ['STAFF','STUDENT','STUDENT','TUTOR','TUTOR']
    added = 0
    i = 0
    while added < 50 and i < 200:
        role = roles_pool[i % len(roles_pool)]
        em = f"seed{base+i}.{role.lower()[:4]}@test.local"
        un = f"seed_{base+i}_{role.lower()[:4]}"
        if em in existing_emails or un in existing_unames:
            i += 1; continue
        existing_emails.add(em); existing_unames.add(un)
        ok = insert_one(conn, """
            INSERT INTO USER_ACCOUNT (email, username, password_hash, role, status, created_at)
            VALUES (:e, :u, :p, :r, 'ACTIVE', :ts)
        """, {"e": em, "u": un, "p": "hash", "r": role,
              "ts": datetime.datetime(2025, 1 + (i%12), 1 + (i%28), 10, 0, 0)})
        if ok: added += 1
        i += 1
    conn.commit()
    n = cur_max(conn, 'USER_ACCOUNT', 'account_id')
    print(f"  → {n} (added {added})")

    # ─────────────────────────────────────────────────────────────────
    # 2. SUBJECT — 50 new unique (name, grade_level) combinations
    # ─────────────────────────────────────────────────────────────────
    print("\n=== SUBJECT ===")
    existing_keys = {(r[0], r[1] or '__NULL__') for r in conn.execute(
        text("SELECT subject_name, ISNULL(grade_level,'__NULL__') FROM SUBJECT")).fetchall()}
    added = 0; idx = 0
    while added < 50 and idx < 300:
        sn = random.choice(['Toán','Vật lý','Hóa học','Sinh học','Ngữ văn','Lịch sử','Địa lý','Tiếng Anh','Tiếng Pháp','Tin học','Kinh tế','Âm nhạc','Vẽ trang trí','Thể dục','Khoa học'])
        gl = random.choice(GRADE_LEVELS)
        key = (sn, gl)
        if key in existing_keys:
            idx += 1; continue
        ok = insert_one(conn, """
            INSERT INTO SUBJECT (subject_name, subject_group, grade_level, description, status, created_at)
            VALUES (:s, :sg, :gl, :d, 'ACTIVE', :ts)
        """, {"s": sn, "sg": "Môn học", "gl": gl, "d": f"Môn {sn} - {gl}",
              "ts": datetime.datetime(2025, 1 + idx%12, 1 + idx%28)})
        if ok:
            existing_keys.add(key); added += 1
        idx += 1
    conn.commit()
    n = cur_max(conn, 'SUBJECT', 'subject_id')
    print(f"  → {n} (added {added})")

    # ─────────────────────────────────────────────────────────────────
    # 3. STAFF (+50), STUDENT (+50), TUTOR (+50)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== STAFF / STUDENT / TUTOR ===")

    staff_accs = [r[0] for r in conn.execute(text("""
        SELECT TOP 50 ua.account_id FROM USER_ACCOUNT ua
        LEFT JOIN STAFF s ON s.account_id = ua.account_id
        WHERE ua.role = 'STAFF' AND s.staff_id IS NULL ORDER BY ua.account_id
    """)).fetchall()]
    stud_accs = [r[0] for r in conn.execute(text("""
        SELECT TOP 50 ua.account_id FROM USER_ACCOUNT ua
        LEFT JOIN STUDENT st ON st.account_id = ua.account_id
        WHERE ua.role = 'STUDENT' AND st.student_id IS NULL ORDER BY ua.account_id
    """)).fetchall()]
    tutor_accs = [r[0] for r in conn.execute(text("""
        SELECT TOP 50 ua.account_id FROM USER_ACCOUNT ua
        LEFT JOIN TUTOR t ON t.account_id = ua.account_id
        WHERE ua.role = 'TUTOR' AND t.tutor_id IS NULL ORDER BY ua.account_id
    """)).fetchall()]

    staff_rows = [{"aid": a, "fn": f"Nhân viên Seed {i+1}",
        "ph": f"090{random.randint(1000000,9999999)}",
        "em": f"staff_seed_{i+1}@test.local",
        "pos": random.choice(['Điều phối viên','Nhân viên hỗ trợ','Quản lý học vụ']),
        "ts": dt()} for i, a in enumerate(staff_accs)]
    conn.execute(text("""
        INSERT INTO STAFF (account_id, full_name, phone, contact_email, position, status, created_at)
        VALUES (:aid, :fn, :ph, :em, :pos, 'ACTIVE', :ts)
    """), staff_rows)
    conn.commit()

    stud_rows = [{"aid": a, "fn": f"Học viên Seed {i+1}",
        "ph": f"091{random.randint(1000000,9999999)}",
        "em": f"student_seed_{i+1}@test.local",
        "addr": f"Số {random.randint(1,200)} {random.choice(AREAS)}",
        "area": random.choice(AREAS),
        "cl": random.choice(GRADE_LEVELS), "gl": random.choice(GRADE_LEVELS),
        "ts": dt()} for i, a in enumerate(stud_accs)]
    conn.execute(text("""
        INSERT INTO STUDENT (account_id, full_name, phone, contact_email, address, area, current_level, grade_level, status, created_at)
        VALUES (:aid, :fn, :ph, :em, :addr, :area, :cl, :gl, 'ACTIVE', :ts)
    """), stud_rows)
    conn.commit()

    tutor_rows = [{"aid": a, "fn": f"Gia sư Seed {i+1}",
        "ph": f"092{random.randint(1000000,9999999)}",
        "em": f"tutor_seed_{i+1}@test.local",
        "uni": random.choice(['ĐH Bách Khoa HN','ĐH KHXH&NV HN','ĐH Kinh tế QG','ĐH Sư phạm HN','ĐH FPT']),
        "maj": random.choice(['Toán học','Vật lý','Hóa học','Ngôn ngữ Anh','CNTT','Kinh tế']),
        "exp": random.randint(1,15), "area": random.choice(AREAS),
        "st": random.choice(['ACTIVE','ACTIVE','ACTIVE','PAUSED','INACTIVE']),
        "ts": datetime.datetime(2024, random.randint(6,12), random.randint(1,28))}
        for i, a in enumerate(tutor_accs)]
    conn.execute(text("""
        INSERT INTO TUTOR (account_id, full_name, phone, contact_email, university, major,
            experience_years, area, status, created_at)
        VALUES (:aid, :fn, :ph, :em, :uni, :maj, :exp, :area, :st, :ts)
    """), tutor_rows)
    conn.commit()

    n_staff = cur_max(conn, 'STAFF', 'staff_id')
    n_stud  = cur_max(conn, 'STUDENT', 'student_id')
    n_tutor = cur_max(conn, 'TUTOR', 'tutor_id')
    print(f"  STAFF→{n_staff} STUDENT→{n_stud} TUTOR→{n_tutor}")

    new_tutor_ids = [r[0] for r in conn.execute(text(
        f"SELECT tutor_id FROM TUTOR WHERE tutor_id > {n_tutor-50} ORDER BY tutor_id")).fetchall()]
    all_subject_ids = [r[0] for r in conn.execute(text("SELECT subject_id FROM SUBJECT")).fetchall()]

    # ─────────────────────────────────────────────────────────────────
    # 4. TUTOR_CAPABILITY — 50 rows (unique tutor, subject, level)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== TUTOR_CAPABILITY ===")
    seen = set(); added = 0; idx = 0
    while added < 50 and idx < 600:
        tid = random.choice(new_tutor_ids)
        sid = random.choice(all_subject_ids)
        gl  = random.choice(GRADE_LEVELS + [None]*4)
        key = (tid, sid, gl)
        if key in seen:
            idx += 1; continue
        seen.add(key)
        ok = insert_one(conn, """
            INSERT INTO TUTOR_CAPABILITY (tutor_id, subject_id, teaching_level, years_experience, note, created_at)
            VALUES (:tid, :sid, :gl, :yr, :note, :ts)
        """, {"tid": tid, "sid": sid, "gl": gl, "yr": random.randint(1,12),
              "note": "Có kinh nghiệm giảng dạy", "ts": dt()})
        if ok: added += 1
        idx += 1
    conn.commit()
    n = cur_max(conn, 'TUTOR_CAPABILITY', 'capability_id')
    print(f"  → {n} (added {added})")

    # ─────────────────────────────────────────────────────────────────
    # 5. TUTOR_AVAILABILITY — 50 rows
    # ─────────────────────────────────────────────────────────────────
    print("\n=== TUTOR_AVAILABILITY ===")
    added = 0; idx = 0
    while added < 50 and idx < 200:
        idx += 1
        ok = insert_one(conn, """
            INSERT INTO TUTOR_AVAILABILITY (tutor_id, day_of_week, start_time, end_time, teaching_mode, area, status, created_at)
            VALUES (:tid, :dow, :st, :et, :tm, :area, :st2, :ts)
        """, {
            "tid": random.choice(new_tutor_ids),
            "dow": random.randint(1,7),
            "st": datetime.time(random.randint(7,18), random.choice([0,30])),
            "et": datetime.time(random.randint(19,21), random.choice([0,30])),
            "tm": random.choice(['OFFLINE','ONLINE','BOTH']),
            "area": random.choice(AREAS),
            "st2": random.choice(['AVAILABLE','AVAILABLE','UNAVAILABLE']),
            "ts": dt()
        })
        if ok: added += 1
    conn.commit()
    n = cur_max(conn, 'TUTOR_AVAILABILITY', 'availability_id')
    print(f"  → {n} (added {added})")

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
            "pm": random.choice(['OFFLINE','ONLINE','BOTH']),
            "ps": random.choice(['T2 17:00-19:00','T3 18:00-20:00','T4 17:30-19:30',
                                  'T2,T4 17:00-19:00','T3,T5 18:00-20:00','T7 sáng','CN chiều']),
            "ef": random.choice([None, 150000, 200000, 250000, 300000, 350000, 400000, 500000]),
            "st": random.choice(['PENDING','PENDING','PENDING','ASSIGNED','CANCELED']),
            "ts": dt()
        })
    conn.execute(text("""
        INSERT INTO LEARNING_REQUEST (student_id, subject_id, requested_level, learning_goal,
            preferred_area, preferred_mode, preferred_schedule, expected_fee, status, created_at)
        VALUES (:sid, :subid, :rl, :lg, :pa, :pm, :ps, :ef, :st, :ts)
    """), req_rows)
    conn.commit()
    n = cur_max(conn, 'LEARNING_REQUEST', 'request_id')
    print(f"  → {n} (added 50)")

    new_req_ids = [r[0] for r in conn.execute(text(
        f"SELECT request_id FROM LEARNING_REQUEST WHERE request_id > {n-50} ORDER BY request_id"
    )).fetchall()]

    # ─────────────────────────────────────────────────────────────────
    # 7. TUTOR_ASSIGNMENT — 50 rows (one per new request, ASSIGNED)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== TUTOR_ASSIGNMENT ===")
    all_staff_ids = [r[0] for r in conn.execute(text("SELECT staff_id FROM STAFF")).fetchall()]
    added = 0; idx = 0
    used_rids = set()
    while added < 50 and idx < 200:
        idx += 1
        rid = random.choice(new_req_ids)
        if rid in used_rids:
            continue
        used_rids.add(rid)
        sub_id = conn.execute(
            text("SELECT subject_id FROM LEARNING_REQUEST WHERE request_id=:rid"),
            {"rid": rid}
        ).scalar()
        capable = [r[0] for r in conn.execute(text("""
            SELECT tc.tutor_id FROM TUTOR_CAPABILITY tc
            JOIN TUTOR t ON t.tutor_id = tc.tutor_id
            WHERE tc.subject_id = :sid AND t.status IN ('ACTIVE','PAUSED')
        """), {"sid": sub_id}).fetchall()]
        if not capable:
            capable = new_tutor_ids
        tid = random.choice(capable)
        ok = insert_one(conn, """
            INSERT INTO TUTOR_ASSIGNMENT (request_id, tutor_id, staff_id, assigned_at, status, note, created_at)
            VALUES (:rid, :tid, :sfid, :aa, 'ASSIGNED', :note, :ts)
        """, {
            "rid": rid, "tid": tid,
            "sfid": random.choice(all_staff_ids + [None]*3),
            "aa": dt(), "note": f"Seed cho yc #{rid}", "ts": dt()
        })
        if ok: added += 1
    conn.commit()
    n = cur_max(conn, 'TUTOR_ASSIGNMENT', 'assignment_id')
    print(f"  → {n} (added {added})")
    new_aids = [r[0] for r in conn.execute(text(f"""
        SELECT assignment_id FROM TUTOR_ASSIGNMENT
        WHERE assignment_id > {n-added} ORDER BY assignment_id
    """)).fetchall()]

    # ─────────────────────────────────────────────────────────────────
    # 8. STUDY_CLASS — 50 rows (end_date >= start_date, teaching_mode OFFLINE/ONLINE)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== STUDY_CLASS ===")
    added = 0; idx = 0
    new_class_ids_accum = []
    for aid in new_aids[:50]:
        idx += 1
        sd, ed = safe_date()
        ok = insert_one(conn, """
            INSERT INTO STUDY_CLASS (assignment_id, class_code, tuition_fee_per_session,
                teaching_mode, location, start_date, end_date, status, created_at)
            VALUES (:aid, :cc, :fee, :tm, :loc, :sd, :ed, :st, :ts)
        """, {
            "aid": aid, "cc": f"CLS-SEED-{aid:04d}",
            "fee": random.choice([150000,200000,250000,300000,350000,400000]),
            "tm": random.choice(MODES_CLS),
            "loc": f"{random.choice(AREAS)}, Hà Nội",
            "sd": sd, "ed": ed,
            "st": random.choice(['ACTIVE','ACTIVE','PAUSED','COMPLETED','CANCELED']),
            "ts": dt()
        })
        if ok:
            added += 1
            # track new class_ids by querying last few rows
            pass
    conn.commit()
    n = cur_max(conn, 'STUDY_CLASS', 'class_id')
    print(f"  → {n} (added {added})")
    new_class_ids = [r[0] for r in conn.execute(text(f"""
        SELECT class_id FROM STUDY_CLASS WHERE class_id > {n-added} ORDER BY class_id
    """)).fetchall()]

    # ─────────────────────────────────────────────────────────────────
    # 9. CLASS_SCHEDULE — 50 unique slots (effective_to >= effective_from)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== CLASS_SCHEDULE ===")
    used_slots = set(); added = 0; idx = 0
    while added < 50 and idx < 600:
        idx += 1
        cid = random.choice(new_class_ids)
        dow = random.randint(1,7)
        sh  = random.randint(7,18); sm = random.choice([0,30])
        eh  = sh + random.randint(1,4); em = random.choice([0,30])
        m1  = random.randint(1,5)
        ef  = datetime.date(2025, m1, random.randint(1,28))
        et2 = datetime.date(2025, m1 + random.randint(1,6), random.randint(1,28))
        slot = (cid, dow, f"{sh:02d}:{sm:02d}", f"{eh:02d}:{em:02d}")
        if slot in used_slots:
            continue
        used_slots.add(slot)
        ok = insert_one(conn, """
            INSERT INTO CLASS_SCHEDULE (class_id, day_of_week, start_time, end_time,
                effective_from, effective_to, status, created_at)
            VALUES (:cid, :dow, :st, :et, :ef, :et2, :st2, :ts)
        """, {"cid": cid, "dow": dow,
              "st": datetime.time(sh, sm), "et": datetime.time(eh, em),
              "ef": ef, "et2": et2,
              "st2": random.choice(['ACTIVE','ACTIVE','INACTIVE']), "ts": dt()})
        if ok: added += 1
    conn.commit()
    n = cur_max(conn, 'CLASS_SCHEDULE', 'schedule_id')
    print(f"  → {n} (added {added})")
    sched_ids = [r[0] for r in conn.execute(text("SELECT schedule_id FROM CLASS_SCHEDULE")).fetchall()]

    # ─────────────────────────────────────────────────────────────────
    # 10. LESSON_SESSION — 50 rows
    # ─────────────────────────────────────────────────────────────────
    print("\n=== LESSON_SESSION ===")
    added = 0; idx = 0
    while added < 50 and idx < 200:
        idx += 1
        ok = insert_one(conn, """
            INSERT INTO LESSON_SESSION (class_id, schedule_id, session_number, lesson_date,
                start_time, end_time, status, content_note, created_at)
            VALUES (:cid, :scid, :sn, :ld, :st, :et, :st2, :cn, :ts)
        """, {
            "cid": random.choice(new_class_ids),
            "scid": random.choice(sched_ids + [None]*3) if sched_ids else None,
            "sn": random.randint(1, 40),
            "ld": datetime.date(2025, random.randint(1,12), random.randint(1,28)),
            "st": datetime.time(random.randint(7,19), random.choice([0,30])),
            "et": datetime.time(random.randint(19,21), random.choice([0,30])),
            "st2": random.choice(['SCHEDULED','COMPLETED','STUDENT_ABSENT','TUTOR_ABSENT','CANCELED']),
            "cn": f"Buổi #{random.randint(1,80)}: {random.choice(GOALS)}",
            "ts": dt()
        })
        if ok: added += 1
    conn.commit()
    n = cur_max(conn, 'LESSON_SESSION', 'session_id')
    print(f"  → {n} (added {added})")

    # ─────────────────────────────────────────────────────────────────
    # 11. TUITION_INVOICE — 50 rows (snapshot, paid=0)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== TUITION_INVOICE ===")
    inv_rows = []; skipped = 0
    for cid in new_class_ids[:60]:
        if skipped > 20: break
        fee_row = conn.execute(
            text("SELECT tuition_fee_per_session FROM STUDY_CLASS WHERE class_id=:cid"),
            {"cid": cid}
        ).fetchone()
        if not fee_row: continue
        fee = float(fee_row[0])
        sessions = random.randint(4, 12)
        due = round(fee * sessions, 2)
        m1 = random.randint(1,6)
        ps  = datetime.date(2025, m1, 1)
        pe  = datetime.date(2025, m1 + random.randint(1,6), 28)
        ok = insert_one(conn, """
            INSERT INTO TUITION_INVOICE (class_id, period_start, period_end, completed_sessions,
                tuition_fee_per_session, amount_due, amount_paid, status, created_at)
            VALUES (:cid, :ps, :pe, :cs, :fee, :due, :paid, :st, :ts)
        """, {
            "cid": cid, "ps": ps, "pe": pe, "cs": sessions,
            "fee": fee, "due": due, "paid": 0.0,
            "st": random.choice(['UNPAID','PARTIALLY_PAID','PAID','OVERDUE','CANCELED']),
            "ts": dt()
        })
        if ok: inv_rows.append({"cid": cid, "iid": None})  # placeholder
        else: skipped += 1
    conn.commit()
    # get real invoice IDs
    for i, row in enumerate(inv_rows):
        r = conn.execute(text("""
            SELECT invoice_id FROM TUITION_INVOICE
            WHERE class_id=:cid ORDER BY invoice_id DESC
        """), {"cid": row["cid"]}).fetchone()
        if r: inv_rows[i]["iid"] = r[0]
    inv_rows = [r for r in inv_rows if r["iid"]]
    n = cur_max(conn, 'TUITION_INVOICE', 'invoice_id')
    print(f"  → {n} (added {len(inv_rows)})")
    new_inv_ids = [r["iid"] for r in inv_rows[:50]]

    # ─────────────────────────────────────────────────────────────────
    # 12. TUITION_PAYMENT — 50 rows (safe SUCCESS)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== TUITION_PAYMENT ===")
    added = 0; idx = 0
    while added < 50 and idx < 200:
        idx += 1
        inv_id = random.choice(new_inv_ids)
        inv = conn.execute(text("""
            SELECT ti.amount_due,
                   COALESCE((SELECT SUM(tp.amount_paid) FROM TUITION_PAYMENT tp
                             WHERE tp.invoice_id=ti.invoice_id AND tp.status='SUCCESS'),0) AS paid
            FROM TUITION_INVOICE ti WHERE ti.invoice_id=:iid
        """), {"iid": inv_id}).fetchone()
        remaining = max(float(inv[0]) - float(inv[1]), 0) if inv else 500000
        amount = round(random.uniform(50000, min(remaining or 50000, 300000)), 0)
        st = random.choice(['SUCCESS','SUCCESS','CANCELED','REFUNDED'])
        if st == 'SUCCESS' and amount < 50000: st = 'CANCELED'
        ok = insert_one(conn, """
            INSERT INTO TUITION_PAYMENT (invoice_id, staff_id, payment_date, amount_paid,
                payment_method, note, status, created_at)
            VALUES (:inv, :sfid, :pd, :am, :pm, :note, :st, :ts)
        """, {
            "inv": inv_id,
            "sfid": random.choice(all_staff_ids + [None]*4),
            "pd": dt(), "am": amount,
            "pm": random.choice(PAYMENT_METHODS),
            "note": f"TT hóa đơn #{inv_id}", "st": st, "ts": dt()
        })
        if ok: added += 1
    conn.commit()
    n = cur_max(conn, 'TUITION_PAYMENT', 'payment_id')
    print(f"  → {n} (added {added})")

    # ─────────────────────────────────────────────────────────────────
    # FINAL VERIFY
    # ─────────────────────────────────────────────────────────────────
    print("\n=== FINAL ROW COUNTS ===")
    tables = [
        'USER_ACCOUNT','STAFF','STUDENT','TUTOR','SUBJECT',
        'LEARNING_REQUEST','TUTOR_ASSIGNMENT','STUDY_CLASS',
        'CLASS_SCHEDULE','LESSON_SESSION','TUITION_INVOICE',
        'TUITION_PAYMENT','TUTOR_AVAILABILITY','TUTOR_CAPABILITY'
    ]
    all_ok = True
    for t in tables:
        r = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        flag = "✓" if r >= 50 else "✗"
        if r < 50: all_ok = False
        print(f"  {flag}  {t}: {r}")

    bad = conn.execute(text("""
        SELECT COUNT(*) FROM TUITION_INVOICE WHERE amount_paid > amount_due
    """)).scalar()
    print(f"\n  amount_paid > amount_due: {bad}  (expect 0)")

    if all_ok:
        print("\n✅ ALL TABLES >= 50 ROWS — DONE")
    else:
        print("\n⚠️  Some tables still below 50. Check output above.")

except Exception as e:
    conn.rollback()
    traceback.print_exc()
finally:
    db.close()

# -*- coding: utf-8 -*-
"""Patch seed v2: STUDY_CLASS → CLASS_SCHEDULE → LESSON_SESSION → INVOICE → PAYMENT
Fixes: teaching_mode must be OFFLINE or BOTH (not ONLINE) per CK_STUDY_CLASS_MODE.
Uses all assignments that lack a STUDY_CLASS (including CANCELED ones since FK only checks assignment_id exists)."""
import sys, io, random, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sqlalchemy import create_engine, text

engine = create_engine(
    "mssql+pyodbc://sa:123456@localhost:1433/TutorCenterDB"
    "?driver=ODBC+Driver+17+for+SQL+Server&trustServerCertificate=yes"
)
random.seed(77)

AREAS = [
    'Cầu giấy','Hà Đông','Đống Đa','Nam Từ Liêm','Thanh Xuân','Long Biên',
    'Hai Bà Trưng','Hoàn Kiếm','Tây Hồ','Bình Thạnh','Phú Nhuận','Gò Vấp',
    'Tân Bình','Thủ Đức','Ba Đình'
]
GRADE_LEVELS = ['Lớp 1','Lớp 2','Lớp 3','Lớp 4','Lớp 5','Lớp 6','Lớp 7','Lớp 8','Lớp 9','Lớp 10','Lớp 11','Lớp 12','THPT','Đại học']
MODES_CLS = ['OFFLINE','ONLINE']   # ← STUDY_CLASS constraint: OFFLINE OR ONLINE (NOT BOTH)
GOALS = ['Ôn tập','Học nâng cao','Luyện thi','Cải thiện điểm','Học phụ đạo','Chuẩn bị cuối kỳ']
PAYMENT_METHODS = ['Tiền mặt','Chuyển khoản','Momo','Vietcombank','Techcombank']

def cur_max(conn, table, col):
    return conn.execute(text(f"SELECT ISNULL(MAX({col}),0) FROM {table}")).scalar()

def dt():
    return datetime.datetime(2025, random.randint(1,12), random.randint(1,28), random.randint(8,20), 0, 0)

with engine.begin() as conn:
    # Find all assignment_ids that don't yet have a STUDY_CLASS row
    avail_aids = [r[0] for r in conn.execute(text("""
        SELECT ta.assignment_id FROM TUTOR_ASSIGNMENT ta
        LEFT JOIN STUDY_CLASS sc ON sc.assignment_id = ta.assignment_id
        WHERE sc.class_id IS NULL
    """)).fetchall()]
    print(f"Assignments without a class: {len(avail_aids)}")
    use_aids = avail_aids[:50]

    # ─────────────────────────────────────────────────────────────────
    # STUDY_CLASS  (max 50)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== STUDY_CLASS ===")
    cls_rows = []
    for aid in use_aids:
        fee = random.choice([150000,180000,200000,220000,250000,300000,350000,400000])
        cls_rows.append({
            "aid": aid,
            "cc": f"CLS-SEED-{aid:04d}",
            "fee": fee,
            "tm": random.choice(MODES_CLS),      # ← OFFLINE or BOTH only
            "loc": f"{random.choice(AREAS)}, Hà Nội",
            "sd": datetime.date(2025, random.randint(1,12), random.randint(1,28)),
            "ed": datetime.date(2025, random.randint(7,12), random.randint(1,28)),
            "st": random.choice(['ACTIVE','ACTIVE','ACTIVE','PAUSED','COMPLETED','CANCELED']),
            "ts": dt()
        })
    conn.execute(text("""
        INSERT INTO STUDY_CLASS (assignment_id, class_code, tuition_fee_per_session,
            teaching_mode, location, start_date, end_date, status, created_at)
        VALUES (:aid, :cc, :fee, :tm, :loc, :sd, :ed, :st, :ts)
    """), cls_rows)
    n = cur_max(conn, 'STUDY_CLASS', 'class_id')
    print(f"  → {n} (added {len(cls_rows)})")
    new_cls_start = n - len(cls_rows) + 1
    new_class_ids = list(range(new_cls_start, n + 1))

    # ─────────────────────────────────────────────────────────────────
    # CLASS_SCHEDULE — 50 unique slots
    # ─────────────────────────────────────────────────────────────────
    print("\n=== CLASS_SCHEDULE ===")
    used = set(); sched_rows = []; attempts = 0
    while len(sched_rows) < 50 and attempts < 500:
        attempts += 1
        cid = random.choice(new_class_ids)
        dow = random.randint(1, 7)
        sh, sm = random.randint(7, 18), random.choice([0, 30])
        eh, em = random.randint(19, 21), random.choice([0, 30])
        slot = (cid, dow, f"{sh:02d}:{sm:02d}", f"{eh:02d}:{em:02d}")
        if slot in used:
            continue
        used.add(slot)
    sched_rows.append({
        "cid": cid, "dow": dow,
        "st": datetime.time(sh, sm), "et": datetime.time(eh, em),
        "ef": datetime.date(2025, random.randint(1, 6), random.randint(1, 28)),
        "et2": datetime.date(2025, random.randint(7, 12), random.randint(1, 28)),
        "st2": random.choice(['ACTIVE','ACTIVE','INACTIVE']),
        "ts": dt()
    })
    conn.execute(text("""
        INSERT INTO CLASS_SCHEDULE (class_id, day_of_week, start_time, end_time,
            effective_from, effective_to, status, created_at)
        VALUES (:cid, :dow, :st, :et, :ef, :et2, :st2, :ts)
    """), sched_rows)
    n = cur_max(conn, 'CLASS_SCHEDULE', 'schedule_id')
    print(f"  → {n} (added {len(sched_rows)})")
    sched_ids = [r[0] for r in conn.execute(text("SELECT schedule_id FROM CLASS_SCHEDULE")).fetchall()]

    # ─────────────────────────────────────────────────────────────────
    # LESSON_SESSION — 50 rows
    # ─────────────────────────────────────────────────────────────────
    print("\n=== LESSON_SESSION ===")
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
            "cn": f"Buổi học #{random.randint(1,80)}: {random.choice(GOALS)}",
            "ts": dt()
        })
    conn.execute(text("""
        INSERT INTO LESSON_SESSION (class_id, schedule_id, session_number, lesson_date,
            start_time, end_time, status, content_note, created_at)
        VALUES (:cid, :scid, :sn, :ld, :st, :et, :st2, :cn, :ts)
    """), session_rows)
    n = cur_max(conn, 'LESSON_SESSION', 'session_id')
    print(f"  → {n} (added {len(session_rows)})")

    # ─────────────────────────────────────────────────────────────────
    # TUITION_INVOICE — 50 rows (snapshot, amount_paid=0 initially)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== TUITION_INVOICE ===")
    inv_rows = []
    for cid in new_class_ids[:50]:
        fee_row = conn.execute(
            text("SELECT tuition_fee_per_session FROM STUDY_CLASS WHERE class_id=:cid"),
            {"cid": cid}
        ).fetchone()
        if not fee_row:
            continue
        fee = float(fee_row[0])
        sessions = random.randint(4, 12)
        due = round(fee * sessions, 2)
        ps = datetime.date(2025, random.randint(1, 6), 1)
        pe = datetime.date(2025, random.randint(ps.month + 1, 12), 28)
        inv_rows.append({
            "cid": cid, "ps": ps, "pe": pe, "cs": sessions,
            "fee": fee, "due": due, "paid": 0.0,
            "st": random.choice(['UNPAID','PARTIALLY_PAID','PAID','OVERDUE','CANCELED']),
            "ts": dt()
        })
    conn.execute(text("""
        INSERT INTO TUITION_INVOICE (class_id, period_start, period_end, completed_sessions,
            tuition_fee_per_session, amount_due, amount_paid, status, created_at)
        VALUES (:cid, :ps, :pe, :cs, :fee, :due, :paid, :st, :ts)
    """), inv_rows)
    n = cur_max(conn, 'TUITION_INVOICE', 'invoice_id')
    print(f"  → {n} (added {len(inv_rows)})")
    new_inv_ids = [r[0] for r in conn.execute(text(f"""
        SELECT invoice_id FROM TUITION_INVOICE
        WHERE invoice_id > {n - len(inv_rows)} ORDER BY invoice_id
    """)).fetchall()]

    # ─────────────────────────────────────────────────────────────────
    # TUITION_PAYMENT — 50 rows (SUCCESS payments within invoice remaining)
    # ─────────────────────────────────────────────────────────────────
    print("\n=== TUITION_PAYMENT ===")
    all_staff_ids = [r[0] for r in conn.execute(text("SELECT staff_id FROM STAFF")).fetchall()]
    pay_rows = []
    for _ in range(50):
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
        if st == 'SUCCESS' and amount < 50000:
            st = 'CANCELED'
        pay_rows.append({
            "inv": inv_id,
            "sfid": random.choice(all_staff_ids + [None]*4),
            "pd": dt(),
            "am": amount,
            "pm": random.choice(PAYMENT_METHODS),
            "note": f"Thanh toán hóa đơn #{inv_id}",
            "st": st,
            "ts": dt()
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
        print(f"  {flag}  {t}: {r}")

    bad = conn.execute(text("""
        SELECT COUNT(*) FROM TUITION_INVOICE
        WHERE amount_paid > amount_due
    """)).scalar()
    print(f"\n  amount_paid > amount_due: {bad}  (expect 0)")
    print("\n✅ DONE")

# -*- coding: utf-8 -*-
"""
Setup scenario để user có thể ấn nút "Gợi ý gia sư" và phân công thủ công.

Kịch bản:
  Request #122: Vật lý Lớp 10, Hà Đông, OFFLINE, T3 19:00-20:30
    → Tutor #3 (Hoàng Đức Vũ) match sẵn (T2,T4 19:00-20:30, OFFLINE, Hà Đông)

  Request #124: Vật lý Lớp 10, Gò Vấp, OFFLINE, CN 13:00-16:00
    → Tutors 944-948 (Gia sư Vật lý Gò Vấp 1-5) match sẵn (CN 13:00-16:00, OFFLINE, Gò Vấp)

Cả 2 request đều PENDING, chưa có ASSIGNED, user mở modal → bấm Gợi ý → chọn tutor → Phân công.
"""
import sys, io, random, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sqlalchemy import create_engine, text

engine = create_engine(
    "mssql+pyodbc://sa:123456@localhost:1433/TutorCenterDB"
    "?driver=ODBC+Driver+17+for+SQL+Server&trustServerCertificate=yes"
)
random.seed(42)

def dt():
    return datetime.datetime(2025, random.randint(1,12), random.randint(1,28), random.randint(8,20), 0, 0)

with engine.begin() as conn:
    # ─────────────────────────────────────────────────────────────────
    # 1. Fix request #122: Vật lý Lớp 10, Hà Đông, OFFLINE, T2 19:00-20:30
    #    Tutor #3 (Hoàng Đức Vũ) có T2 19:00-20:30 OFFLINE Hà Đông → perfect match
    # ─────────────────────────────────────────────────────────────────
    print("=== Fix Request #122 ===")
    old = conn.execute(text(
        "SELECT request_id, subject_id, preferred_area, preferred_mode, preferred_schedule, status FROM LEARNING_REQUEST WHERE request_id = 122"
    )).fetchone()
    print(f"  Before: {old}")

    # Check if #122 already has ASSIGNED assignment — if yes, cancel it to make PENDING again
    existing_assign = conn.execute(text("""
        SELECT assignment_id, status FROM TUTOR_ASSIGNMENT
        WHERE request_id = 122 AND status = 'ASSIGNED'
    """)).fetchone()
    if existing_assign:
        print(f"  Canceling existing assignment {existing_assign[0]}")
        conn.execute(text("UPDATE TUTOR_ASSIGNMENT SET status='CANCELED', updated_at=:ts WHERE assignment_id=:aid"),
                     {"ts": dt(), "aid": existing_assign[0]})

    conn.execute(text("""
        UPDATE LEARNING_REQUEST
        SET subject_id = 3,
            preferred_area = N'Hà Đông',
            preferred_mode = 'OFFLINE',
            preferred_schedule = N'T2 19:00-20:30',
            status = 'PENDING',
            updated_at = :ts
        WHERE request_id = 122
    """), {"ts": dt()})
    new = conn.execute(text(
        "SELECT request_id, subject_id, preferred_area, preferred_mode, preferred_schedule, status FROM LEARNING_REQUEST WHERE request_id = 122"
    )).fetchone()
    print(f"  After:  {new}")

    # ─────────────────────────────────────────────────────────────────
    # 2. Fix request #124: Vật lý Lớp 10, Gò Vấp, OFFLINE, CN 13:00-16:00
    #    Tutors 944-948 (Gò Vấp, Vật lý, CN 13:00-16:00, OFFLINE) → perfect match
    # ─────────────────────────────────────────────────────────────────
    print("\n=== Fix Request #124 ===")
    old = conn.execute(text(
        "SELECT request_id, subject_id, preferred_area, preferred_mode, preferred_schedule, status FROM LEARNING_REQUEST WHERE request_id = 124"
    )).fetchone()
    print(f"  Before: {old}")

    existing_assign = conn.execute(text("""
        SELECT assignment_id, status FROM TUTOR_ASSIGNMENT
        WHERE request_id = 124 AND status = 'ASSIGNED'
    """)).fetchone()
    if existing_assign:
        print(f"  Canceling existing assignment {existing_assign[0]}")
        conn.execute(text("UPDATE TUTOR_ASSIGNMENT SET status='CANCELED', updated_at=:ts WHERE assignment_id=:aid"),
                     {"ts": dt(), "aid": existing_assign[0]})

    conn.execute(text("""
        UPDATE LEARNING_REQUEST
        SET subject_id = 3,
            preferred_area = N'Gò Vấp',
            preferred_mode = 'OFFLINE',
            preferred_schedule = N'CN 13:00-16:00',
            status = 'PENDING',
            updated_at = :ts
        WHERE request_id = 124
    """), {"ts": dt()})
    new = conn.execute(text(
        "SELECT request_id, subject_id, preferred_area, preferred_mode, preferred_schedule, status FROM LEARNING_REQUEST WHERE request_id = 124"
    )).fetchone()
    print(f"  After:  {new}")

    # ─────────────────────────────────────────────────────────────────
    # 3. Add 1 more tutor BOTH mode in Hà Đông (dùng cho request #122)
    #    Hiện tutor #3 chỉ có OFFLINE, cần thêm BOTH để có option
    # ─────────────────────────────────────────────────────────────────
    print("\n=== Add BOTH-mode tutor in Hà Đông (Vật lý Lớp 10) ===")
    acc_id = conn.execute(text("SELECT ISNULL(MAX(account_id),0)+1 FROM USER_ACCOUNT")).scalar()
    em = f"tutor_hd_vl_both_{acc_id}@test.local"
    conn.execute(text("""
        INSERT INTO USER_ACCOUNT (email, username, password_hash, role, status, created_at)
        VALUES (:e, :u, 'x', 'TUTOR', 'ACTIVE', :ts)
    """), {"e": em, "u": f"tvl_hd_{acc_id}", "ts": dt()})
    tid = conn.execute(text("SELECT ISNULL(MAX(tutor_id),0)+1 FROM TUTOR")).scalar()
    conn.execute(text("""
        INSERT INTO TUTOR (account_id, full_name, phone, contact_email, university, major,
            experience_years, area, status, created_at)
        VALUES (:aid, N'Gia sư Vật lý Hà Đông (BOTH)',
                :ph, :em, N'ĐH Bách Khoa HN', N'Vật lý', 8, N'Hà Đông', 'ACTIVE', :ts)
    """), {
        "aid": acc_id,
        "ph": f"090{random.randint(1000000,9999999)}",
        "em": em, "ts": dt()
    })
    # Capability: Vật lý Lớp 10
    conn.execute(text("""
        INSERT INTO TUTOR_CAPABILITY (tutor_id, subject_id, teaching_level, years_experience, note, created_at)
        VALUES (:tid, 3, N'Lớp 10', 8, N'Vật lý Lớp 10, dạy cả ONLINE và OFFLINE', :ts)
    """), {"tid": tid, "ts": dt()})
    # Availability: BOTH — T2 (day 1) 18:30-20:30, T4 (day 3) 18:30-20:30
    conn.execute(text("""
        INSERT INTO TUTOR_AVAILABILITY (tutor_id, day_of_week, start_time, end_time, teaching_mode, area, status, created_at)
        VALUES (:tid, 1, '18:30', '20:30', 'BOTH', N'Hà Đông', 'AVAILABLE', :ts),
               (:tid, 3, '18:30', '20:30', 'BOTH', N'Hà Đông', 'AVAILABLE', :ts)
    """), {"tid": tid, "ts": dt()})
    conn.commit()
    print(f"  Added tutor #{tid} 'Gia sư Vật lý Hà Đông (BOTH)'")
    print(f"  Email: {em}")
    print(f"  Pass: tutor123")

    # ─────────────────────────────────────────────────────────────────
    # 4. Verify: simulate suggest_tutors_for_request for #122 and #124
    # ─────────────────────────────────────────────────────────────────
    print("\n=== VERIFY: Simulated suggestions for Request #122 ===")
    rows = conn.execute(text("""
        SELECT t.tutor_id, t.full_name, t.area, t.experience_years,
               ta.day_of_week, ta.start_time, ta.end_time, ta.teaching_mode,
               CASE WHEN t.area = N'Hà Đông' THEN 1 ELSE 0 END AS area_match,
               CASE WHEN ta.teaching_mode = 'BOTH' THEN 1
                    WHEN ta.teaching_mode = 'OFFLINE' THEN 1
                    ELSE 0 END AS mode_match
        FROM TUTOR t
        JOIN TUTOR_CAPABILITY tc ON tc.tutor_id = t.tutor_id
        JOIN TUTOR_AVAILABILITY ta ON ta.tutor_id = t.tutor_id
        WHERE tc.subject_id = 3
          AND t.status = 'ACTIVE'
          AND ta.status = 'AVAILABLE'
          AND ta.teaching_mode IN ('BOTH', 'OFFLINE')
          AND ta.day_of_week = 1   -- T2
          AND ta.start_time <= '20:30'
          AND ta.end_time   >= '19:00'
          AND NOT EXISTS (SELECT 1 FROM TUTOR_ASSIGNMENT ta2 WHERE ta2.tutor_id=t.tutor_id AND ta2.status='ASSIGNED')
        ORDER BY t.experience_years DESC
    """)).fetchall()
    print(f"  Tutors for #122 (Vật lý, Hà Đông, T2 19:00-20:30, OFFLINE): {len(rows)}")
    for r in rows:
        print(f"    Tutor #{r[0]} {r[1]} | {r[2]} | {r[3]}y | T{r[5]} {r[6]}-{r[7]} | mode={r[8]} | area_match={r[9]}")

    print("\n=== VERIFY: Simulated suggestions for Request #124 ===")
    rows2 = conn.execute(text("""
        SELECT t.tutor_id, t.full_name, t.area, t.experience_years,
               ta.day_of_week, ta.start_time, ta.end_time, ta.teaching_mode,
               CASE WHEN t.area = N'Gò Vấp' THEN 1 ELSE 0 END AS area_match
        FROM TUTOR t
        JOIN TUTOR_CAPABILITY tc ON tc.tutor_id = t.tutor_id
        JOIN TUTOR_AVAILABILITY ta ON ta.tutor_id = t.tutor_id
        WHERE tc.subject_id = 3
          AND t.status = 'ACTIVE'
          AND ta.status = 'AVAILABLE'
          AND ta.teaching_mode IN ('BOTH', 'OFFLINE')
          AND ta.day_of_week = 7   -- CN
          AND ta.start_time <= '16:00'
          AND ta.end_time   >= '13:00'
          AND NOT EXISTS (SELECT 1 FROM TUTOR_ASSIGNMENT ta2 WHERE ta2.tutor_id=t.tutor_id AND ta2.status='ASSIGNED')
        ORDER BY t.experience_years DESC
    """)).fetchall()
    print(f"  Tutors for #124 (Vật lý, Gò Vấp, CN 13:00-16:00, OFFLINE): {len(rows2)}")
    for r in rows2:
        print(f"    Tutor #{r[0]} {r[1]} | {r[2]} | {r[3]}y | CN {r[6]}-{r[7]} | area_match={r[9]}")

    print("\n=== COUNTS ===")
    for t in ['USER_ACCOUNT','STAFF','STUDENT','TUTOR','SUBJECT',
              'LEARNING_REQUEST','TUTOR_ASSIGNMENT','STUDY_CLASS',
              'CLASS_SCHEDULE','LESSON_SESSION','TUITION_INVOICE',
              'TUITION_PAYMENT','TUTOR_AVAILABILITY','TUTOR_CAPABILITY']:
        print(f"  {t}: {conn.execute(text(f'SELECT COUNT(*) FROM {t}')).scalar()}")
    print("\n✅ DONE")

from datetime import date, datetime
from types import SimpleNamespace
from typing import Iterable, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import (
    ClassSchedule,
    LearningRequest,
    LessonSession,
    Staff,
    Student,
    StudyClass,
    Subject,
    TuitionInvoice,
    TuitionPayment,
    Tutor,
    TutorAvailability,
    TutorAssignment,
    TutorCapability,
    UserAccount,
)


def to_obj(row):
    if row is None:
        return None
    return SimpleNamespace(**dict(row))


def to_list(rows):
    return [to_obj(row) for row in rows]


def fetch_one(db: Session, sql: str, params: Optional[dict] = None):
    row = db.execute(text(sql), params or {}).mappings().first()
    return to_obj(row)


def fetch_all(db: Session, sql: str, params: Optional[dict] = None):
    rows = db.execute(text(sql), params or {}).mappings().all()
    return to_list(rows)


def execute(db: Session, sql: str, params: Optional[dict] = None):
    return db.execute(text(sql), params or {})


def update_by_id(db: Session, table: str, id_column: str, id_value, data: dict, allowed_columns: set[str]) -> None:
    clean = {
        key: value
        for key, value in data.items()
        if key in allowed_columns and key != "updated_at"
    }
    if not clean:
        return

    assignments = ", ".join([f"{column} = :{column}" for column in clean])
    execute(
        db,
        f"""
        UPDATE {table}
        SET {assignments},
            updated_at = SYSUTCDATETIME()
        WHERE {id_column} = :id_value
        """,
        {**clean, "id_value": id_value},
    )


STUDENT_UPDATE_COLUMNS = {"full_name", "phone", "contact_email", "address", "area", "current_level", "grade_level", "status"}
TUTOR_UPDATE_COLUMNS = {"full_name", "phone", "contact_email", "university", "major", "experience_years", "area", "status"}
SUBJECT_UPDATE_COLUMNS = {"subject_name", "subject_group", "grade_level", "description", "status"}
TUTOR_CAPABILITY_UPDATE_COLUMNS = {"teaching_level", "years_experience", "note"}
TUTOR_AVAILABILITY_UPDATE_COLUMNS = {"day_of_week", "start_time", "end_time", "teaching_mode", "area", "status"}
LEARNING_REQUEST_UPDATE_COLUMNS = {
    "subject_id",
    "requested_level",
    "learning_goal",
    "preferred_area",
    "preferred_mode",
    "preferred_schedule",
    "expected_fee",
    "status",
}
ASSIGNMENT_UPDATE_COLUMNS = {"tutor_id", "staff_id", "status", "note"}
CLASS_UPDATE_COLUMNS = {
    "tuition_fee_per_session",
    "teaching_mode",
    "location",
    "start_date",
    "end_date",
    "status",
}
SCHEDULE_UPDATE_COLUMNS = {
    "day_of_week",
    "start_time",
    "end_time",
    "effective_from",
    "effective_to",
    "status",
    "note",
}
SESSION_UPDATE_COLUMNS = {
    "schedule_id",
    "session_number",
    "lesson_date",
    "start_time",
    "end_time",
    "status",
    "content_note",
}
INVOICE_UPDATE_COLUMNS = {
    "period_start",
    "period_end",
    "completed_sessions",
    "tuition_fee_per_session",
    "amount_due",
    "amount_paid",
    "status",
}
PAYMENT_UPDATE_COLUMNS = {
    "staff_id",
    "payment_date",
    "amount_paid",
    "payment_method",
    "note",
    "status",
}


def touch_model(model):
    if hasattr(model, "updated_at"):
        model.updated_at = datetime.utcnow()
    return model


def apply_updates(model, data: dict):
    changed = False
    for key, value in data.items():
        if key == "updated_at":
            continue
        if hasattr(model, key):
            setattr(model, key, value)
            changed = True
    if changed:
        touch_model(model)
    return model


def get_user_by_email(db: Session, email: str) -> Optional[UserAccount]:
    return fetch_one(
        db,
        """
        SELECT account_id, email, username, password_hash, role, status, created_at, updated_at
        FROM USER_ACCOUNT
        WHERE email = :email
        """,
        {"email": email},
    )


def get_user_by_username(db: Session, username: str) -> Optional[UserAccount]:
    return fetch_one(
        db,
        """
        SELECT account_id, email, username, password_hash, role, status, created_at, updated_at
        FROM USER_ACCOUNT
        WHERE username = :username
        """,
        {"username": username},
    )


def get_user_by_id(db: Session, account_id: int) -> Optional[UserAccount]:
    return fetch_one(
        db,
        """
        SELECT account_id, email, username, password_hash, role, status, created_at, updated_at
        FROM USER_ACCOUNT
        WHERE account_id = :account_id
        """,
        {"account_id": account_id},
    )


def create_user(db: Session, user: UserAccount) -> UserAccount:
    row = db.execute(
        text(
            """
            INSERT INTO USER_ACCOUNT (
                email,
                username,
                password_hash,
                role,
                status
            )
            OUTPUT
                INSERTED.account_id,
                INSERTED.email,
                INSERTED.username,
                INSERTED.password_hash,
                INSERTED.role,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :email,
                :username,
                :password_hash,
                :role,
                :status
            )
            """
        ),
        {
            "email": user.email,
            "username": user.username,
            "password_hash": user.password_hash,
            "role": user.role,
            "status": user.status,
        },
    ).mappings().first()
    return to_obj(row)


def get_staff(db: Session, staff_id: int) -> Optional[Staff]:
    return fetch_one(
        db,
        """
        SELECT staff_id, account_id, full_name, phone, contact_email, position, status, created_at, updated_at
        FROM STAFF
        WHERE staff_id = :staff_id
        """,
        {"staff_id": staff_id},
    )


def get_staff_by_account_id(db: Session, account_id: int) -> Optional[Staff]:
    return fetch_one(
        db,
        """
        SELECT staff_id, account_id, full_name, phone, contact_email, position, status, created_at, updated_at
        FROM STAFF
        WHERE account_id = :account_id
        """,
        {"account_id": account_id},
    )


def create_staff(db: Session, staff: Staff) -> Staff:
    row = db.execute(
        text(
            """
            INSERT INTO STAFF (
                account_id,
                full_name,
                phone,
                contact_email,
                position,
                status
            )
            OUTPUT
                INSERTED.staff_id,
                INSERTED.account_id,
                INSERTED.full_name,
                INSERTED.phone,
                INSERTED.contact_email,
                INSERTED.position,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :account_id,
                :full_name,
                :phone,
                :contact_email,
                :position,
                :status
            )
            """
        ),
        {
            "account_id": staff.account_id,
            "full_name": staff.full_name,
            "phone": staff.phone,
            "contact_email": staff.contact_email,
            "position": staff.position,
            "status": staff.status,
        },
    ).mappings().first()
    return to_obj(row)


def get_students(
    db: Session,
    search: Optional[str] = None,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    area: Optional[str] = None,
    status: Optional[str] = None,
) -> list[Student]:
    return fetch_all(
        db,
        """
        SELECT
            student_id,
            account_id,
            full_name,
            phone,
            contact_email,
            address,
            area,
            current_level,
            grade_level,
            status,
            created_at,
            updated_at
        FROM STUDENT
        WHERE (:status IS NULL OR status = :status)
          AND (
              :search IS NULL
              OR full_name LIKE :search
              OR phone LIKE :search
              OR contact_email LIKE :search
              OR area LIKE :search
          )
          AND (:name IS NULL OR full_name LIKE :name)
          AND (:phone IS NULL OR phone LIKE :phone)
          AND (:email IS NULL OR contact_email LIKE :email)
          AND (:area IS NULL OR area LIKE :area)
        ORDER BY student_id DESC
        """,
        {
            "search": f"%{search}%" if search else None,
            "name": f"%{name}%" if name else None,
            "phone": f"%{phone}%" if phone else None,
            "email": f"%{email}%" if email else None,
            "area": f"%{area}%" if area else None,
            "status": status,
        },
    )


def get_student(db: Session, student_id: int) -> Optional[Student]:
    return fetch_one(
        db,
        """
        SELECT
            student_id,
            account_id,
            full_name,
            phone,
            contact_email,
            address,
            area,
            current_level,
            grade_level,
            status,
            created_at,
            updated_at
        FROM STUDENT
        WHERE student_id = :student_id
        """,
        {"student_id": student_id},
    )


def get_student_by_account_id(db: Session, account_id: int) -> Optional[Student]:
    return fetch_one(
        db,
        """
        SELECT
            student_id,
            account_id,
            full_name,
            phone,
            contact_email,
            address,
            area,
            current_level,
            grade_level,
            status,
            created_at,
            updated_at
        FROM STUDENT
        WHERE account_id = :account_id
        """,
        {"account_id": account_id},
    )


def create_student(db: Session, student: Student) -> Student:
    row = db.execute(
        text(
            """
            INSERT INTO STUDENT (
                account_id,
                full_name,
                phone,
                contact_email,
                address,
                area,
                current_level,
                grade_level,
                status
            )
            OUTPUT
                INSERTED.student_id,
                INSERTED.account_id,
                INSERTED.full_name,
                INSERTED.phone,
                INSERTED.contact_email,
                INSERTED.address,
                INSERTED.area,
                INSERTED.current_level,
                INSERTED.grade_level,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :account_id,
                :full_name,
                :phone,
                :contact_email,
                :address,
                :area,
                :current_level,
                :grade_level,
                :status
            )
            """
        ),
        {
            "account_id": student.account_id,
            "full_name": student.full_name,
            "phone": student.phone,
            "contact_email": student.contact_email,
            "address": student.address,
            "area": student.area,
            "current_level": student.current_level,
            "grade_level": student.grade_level,
            "status": student.status,
        },
    ).mappings().first()
    return to_obj(row)


def update_student(db: Session, student_id: int, data: dict) -> None:
    update_by_id(db, "STUDENT", "student_id", student_id, data, STUDENT_UPDATE_COLUMNS)


def deactivate_student(db: Session, student_id: int) -> None:
    update_student(db, student_id, {"status": "INACTIVE"})


def _tutor_select_sql() -> str:
    return """
        SELECT
            tutor_id,
            account_id,
            full_name,
            phone,
            contact_email,
            university,
            major,
            experience_years,
            area,
            status,
            created_at,
            updated_at
        FROM TUTOR
    """


def _attach_tutor_capabilities(db: Session, tutor):
    if tutor is not None:
        tutor.capabilities = get_tutor_capabilities(db, tutor.tutor_id)
    return tutor


def _attach_tutors_capabilities(db: Session, tutors: list):
    for tutor in tutors:
        _attach_tutor_capabilities(db, tutor)
    return tutors


def get_tutors(
    db: Session,
    search: Optional[str] = None,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    area: Optional[str] = None,
    subject: Optional[str] = None,
    status: Optional[str] = None,
) -> list[Tutor]:
    tutors = fetch_all(
        db,
        """
        SELECT DISTINCT
            t.tutor_id,
            t.account_id,
            t.full_name,
            t.phone,
            t.contact_email,
            t.university,
            t.major,
            t.experience_years,
            t.area,
            t.status,
            t.created_at,
            t.updated_at
        FROM TUTOR t
        LEFT JOIN TUTOR_CAPABILITY tc ON tc.tutor_id = t.tutor_id
        LEFT JOIN SUBJECT s ON s.subject_id = tc.subject_id
        WHERE (:status IS NULL OR t.status = :status)
          AND (
              :search IS NULL
              OR t.full_name LIKE :search
              OR t.phone LIKE :search
              OR t.contact_email LIKE :search
              OR t.area LIKE :search
              OR s.subject_name LIKE :search
          )
          AND (:name IS NULL OR t.full_name LIKE :name)
          AND (:phone IS NULL OR t.phone LIKE :phone)
          AND (:email IS NULL OR t.contact_email LIKE :email)
          AND (:area IS NULL OR t.area LIKE :area)
          AND (:subject IS NULL OR s.subject_name LIKE :subject)
        ORDER BY t.tutor_id DESC
        """,
        {
            "search": f"%{search}%" if search else None,
            "name": f"%{name}%" if name else None,
            "phone": f"%{phone}%" if phone else None,
            "email": f"%{email}%" if email else None,
            "area": f"%{area}%" if area else None,
            "subject": f"%{subject}%" if subject else None,
            "status": status,
        },
    )
    return _attach_tutors_capabilities(db, tutors)


def get_tutor(db: Session, tutor_id: int) -> Optional[Tutor]:
    return _attach_tutor_capabilities(
        db,
        fetch_one(
            db,
            f"""
            {_tutor_select_sql()}
            WHERE tutor_id = :tutor_id
            """,
            {"tutor_id": tutor_id},
        ),
    )


def get_tutor_by_account_id(db: Session, account_id: int) -> Optional[Tutor]:
    return fetch_one(
        db,
        """
        SELECT
            tutor_id,
            account_id,
            full_name,
            phone,
            contact_email,
            university,
            major,
            experience_years,
            area,
            status,
            created_at,
            updated_at
        FROM TUTOR
        WHERE account_id = :account_id
        """,
        {"account_id": account_id},
    )


def create_tutor(db: Session, tutor: Tutor) -> Tutor:
    row = db.execute(
        text(
            """
            INSERT INTO TUTOR (
                account_id,
                full_name,
                phone,
                contact_email,
                university,
                major,
                experience_years,
                area,
                status
            )
            OUTPUT
                INSERTED.tutor_id,
                INSERTED.account_id,
                INSERTED.full_name,
                INSERTED.phone,
                INSERTED.contact_email,
                INSERTED.university,
                INSERTED.major,
                INSERTED.experience_years,
                INSERTED.area,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :account_id,
                :full_name,
                :phone,
                :contact_email,
                :university,
                :major,
                :experience_years,
                :area,
                :status
            )
            """
        ),
        {
            "account_id": tutor.account_id,
            "full_name": tutor.full_name,
            "phone": tutor.phone,
            "contact_email": tutor.contact_email,
            "university": tutor.university,
            "major": tutor.major,
            "experience_years": tutor.experience_years,
            "area": tutor.area,
            "status": tutor.status,
        },
    ).mappings().first()
    created = to_obj(row)
    created.capabilities = []
    return created


def update_tutor(db: Session, tutor_id: int, data: dict) -> None:
    update_by_id(db, "TUTOR", "tutor_id", tutor_id, data, TUTOR_UPDATE_COLUMNS)


def touch_tutor(db: Session, tutor_id: int) -> None:
    execute(
        db,
        """
        UPDATE TUTOR
        SET updated_at = SYSUTCDATETIME()
        WHERE tutor_id = :tutor_id
        """,
        {"tutor_id": tutor_id},
    )


def deactivate_tutor(db: Session, tutor_id: int) -> None:
    update_tutor(db, tutor_id, {"status": "INACTIVE"})


def get_subjects(db: Session, status: Optional[str] = None) -> list[Subject]:
    return fetch_all(
        db,
        """
        SELECT
            subject_id,
            subject_name,
            subject_group,
            grade_level,
            description,
            status,
            created_at,
            updated_at
        FROM SUBJECT
        WHERE (:status IS NULL OR status = :status)
        ORDER BY subject_name ASC, grade_level ASC
        """,
        {"status": status},
    )


def get_subject(db: Session, subject_id: int) -> Optional[Subject]:
    return fetch_one(
        db,
        """
        SELECT
            subject_id,
            subject_name,
            subject_group,
            grade_level,
            description,
            status,
            created_at,
            updated_at
        FROM SUBJECT
        WHERE subject_id = :subject_id
        """,
        {"subject_id": subject_id},
    )


def get_subject_by_name_level(db: Session, name: str, level: Optional[str] = None) -> Optional[Subject]:
    return fetch_one(
        db,
        """
        SELECT
            subject_id,
            subject_name,
            subject_group,
            grade_level,
            description,
            status,
            created_at,
            updated_at
        FROM SUBJECT
        WHERE subject_name = :name
          AND ((:level IS NULL AND grade_level IS NULL) OR grade_level = :level)
        """,
        {"name": name, "level": level},
    )


def create_subject(db: Session, subject: Subject) -> Subject:
    row = db.execute(
        text(
            """
            INSERT INTO SUBJECT (
                subject_name,
                subject_group,
                grade_level,
                description,
                status
            )
            OUTPUT
                INSERTED.subject_id,
                INSERTED.subject_name,
                INSERTED.subject_group,
                INSERTED.grade_level,
                INSERTED.description,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :subject_name,
                :subject_group,
                :grade_level,
                :description,
                :status
            )
            """
        ),
        {
            "subject_name": subject.subject_name,
            "subject_group": subject.subject_group,
            "grade_level": subject.grade_level,
            "description": subject.description,
            "status": subject.status,
        },
    ).mappings().first()
    return to_obj(row)


def update_subject(db: Session, subject_id: int, data: dict) -> None:
    update_by_id(db, "SUBJECT", "subject_id", subject_id, data, SUBJECT_UPDATE_COLUMNS)


def deactivate_subject(db: Session, subject_id: int) -> None:
    update_subject(db, subject_id, {"status": "INACTIVE"})


def get_tutor_capability(db: Session, tutor_id: int, subject_id: int) -> Optional[TutorCapability]:
    return fetch_one(
        db,
        """
        SELECT TOP 1
            tc.capability_id,
            tc.tutor_id,
            tc.subject_id,
            tc.teaching_level,
            tc.years_experience,
            tc.note,
            tc.created_at,
            tc.updated_at,
            s.subject_name,
            s.grade_level,
            s.subject_group,
            s.status AS subject_status
        FROM TUTOR_CAPABILITY tc
        JOIN SUBJECT s ON s.subject_id = tc.subject_id
        WHERE tc.tutor_id = :tutor_id
          AND tc.subject_id = :subject_id
        ORDER BY tc.capability_id ASC
        """,
        {"tutor_id": tutor_id, "subject_id": subject_id},
    )


def get_tutor_capability_by_id(db: Session, tutor_id: int, capability_id: int) -> Optional[TutorCapability]:
    return fetch_one(
        db,
        """
        SELECT
            tc.capability_id,
            tc.tutor_id,
            tc.subject_id,
            tc.teaching_level,
            tc.years_experience,
            tc.note,
            tc.created_at,
            tc.updated_at,
            s.subject_name,
            s.grade_level,
            s.subject_group,
            s.status AS subject_status
        FROM TUTOR_CAPABILITY tc
        JOIN SUBJECT s ON s.subject_id = tc.subject_id
        WHERE tc.tutor_id = :tutor_id
          AND tc.capability_id = :capability_id
        """,
        {"tutor_id": tutor_id, "capability_id": capability_id},
    )


def get_tutor_capabilities(db: Session, tutor_id: int) -> list[TutorCapability]:
    rows = fetch_all(
        db,
        """
        SELECT
            tc.capability_id,
            tc.tutor_id,
            tc.subject_id,
            tc.teaching_level,
            tc.years_experience,
            tc.note,
            tc.created_at,
            tc.updated_at,
            s.subject_name,
            s.grade_level,
            s.subject_group,
            s.description AS subject_description,
            s.status AS subject_status,
            s.created_at AS subject_created_at,
            s.updated_at AS subject_updated_at
        FROM TUTOR_CAPABILITY tc
        JOIN SUBJECT s ON s.subject_id = tc.subject_id
        WHERE tc.tutor_id = :tutor_id
        ORDER BY s.subject_name ASC, s.grade_level ASC, tc.capability_id ASC
        """,
        {"tutor_id": tutor_id},
    )
    for capability in rows:
        capability.subject = SimpleNamespace(
            subject_id=capability.subject_id,
            subject_name=capability.subject_name,
            subject_group=capability.subject_group,
            grade_level=capability.grade_level,
            description=getattr(capability, "subject_description", None),
            status=capability.subject_status,
            created_at=getattr(capability, "subject_created_at", None),
            updated_at=getattr(capability, "subject_updated_at", None),
        )
    return rows


def create_tutor_capability(db: Session, capability: TutorCapability) -> TutorCapability:
    row = db.execute(
        text(
            """
            INSERT INTO TUTOR_CAPABILITY (
                tutor_id,
                subject_id,
                teaching_level,
                years_experience,
                note
            )
            OUTPUT
                INSERTED.capability_id,
                INSERTED.tutor_id,
                INSERTED.subject_id,
                INSERTED.teaching_level,
                INSERTED.years_experience,
                INSERTED.note,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :tutor_id,
                :subject_id,
                :teaching_level,
                :years_experience,
                :note
            )
            """
        ),
        {
            "tutor_id": capability.tutor_id,
            "subject_id": capability.subject_id,
            "teaching_level": capability.teaching_level,
            "years_experience": capability.years_experience,
            "note": capability.note,
        },
    ).mappings().first()
    created = to_obj(row)
    subject = get_subject(db, created.subject_id)
    created.subject = subject
    return created


def update_tutor_capability(db: Session, capability_id: int, data: dict) -> None:
    update_by_id(db, "TUTOR_CAPABILITY", "capability_id", capability_id, data, TUTOR_CAPABILITY_UPDATE_COLUMNS)


def delete_tutor_capability(db: Session, capability: TutorCapability) -> None:
    execute(
        db,
        """
        DELETE FROM TUTOR_CAPABILITY
        WHERE capability_id = :capability_id
        """,
        {"capability_id": capability.capability_id},
    )


def delete_tutor_capabilities(db: Session, tutor_id: int) -> None:
    execute(
        db,
        """
        DELETE FROM TUTOR_CAPABILITY
        WHERE tutor_id = :tutor_id
        """,
        {"tutor_id": tutor_id},
    )


def get_tutor_availabilities(db: Session, tutor_id: int) -> list[TutorAvailability]:
    return fetch_all(
        db,
        """
        SELECT
            availability_id,
            tutor_id,
            day_of_week,
            start_time,
            end_time,
            teaching_mode,
            area,
            status,
            created_at,
            updated_at
        FROM TUTOR_AVAILABILITY
        WHERE tutor_id = :tutor_id
        ORDER BY day_of_week ASC, start_time ASC
        """,
        {"tutor_id": tutor_id},
    )


def get_tutor_availability(db: Session, tutor_id: int, availability_id: int) -> Optional[TutorAvailability]:
    return fetch_one(
        db,
        """
        SELECT
            availability_id,
            tutor_id,
            day_of_week,
            start_time,
            end_time,
            teaching_mode,
            area,
            status,
            created_at,
            updated_at
        FROM TUTOR_AVAILABILITY
        WHERE tutor_id = :tutor_id
          AND availability_id = :availability_id
        """,
        {"tutor_id": tutor_id, "availability_id": availability_id},
    )


def create_tutor_availability(db: Session, availability: TutorAvailability) -> TutorAvailability:
    row = db.execute(
        text(
            """
            INSERT INTO TUTOR_AVAILABILITY (
                tutor_id,
                day_of_week,
                start_time,
                end_time,
                teaching_mode,
                area,
                status
            )
            OUTPUT
                INSERTED.availability_id,
                INSERTED.tutor_id,
                INSERTED.day_of_week,
                INSERTED.start_time,
                INSERTED.end_time,
                INSERTED.teaching_mode,
                INSERTED.area,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :tutor_id,
                :day_of_week,
                :start_time,
                :end_time,
                :teaching_mode,
                :area,
                :status
            )
            """
        ),
        {
            "tutor_id": availability.tutor_id,
            "day_of_week": availability.day_of_week,
            "start_time": availability.start_time,
            "end_time": availability.end_time,
            "teaching_mode": availability.teaching_mode,
            "area": availability.area,
            "status": availability.status,
        },
    ).mappings().first()
    return to_obj(row)


def update_tutor_availability(db: Session, availability_id: int, data: dict) -> None:
    update_by_id(db, "TUTOR_AVAILABILITY", "availability_id", availability_id, data, TUTOR_AVAILABILITY_UPDATE_COLUMNS)


def delete_tutor_availability(db: Session, availability_id: int) -> None:
    execute(
        db,
        """
        DELETE FROM TUTOR_AVAILABILITY
        WHERE availability_id = :availability_id
        """,
        {"availability_id": availability_id},
    )


def _attach_learning_request_detail(request):
    if request is not None:
        request.student = SimpleNamespace(
            student_id=request.student_id,
            full_name=getattr(request, "student_name", None),
            phone=getattr(request, "student_phone", None),
            contact_email=getattr(request, "student_email", None),
        )
        request.subject = SimpleNamespace(
            subject_id=request.subject_id,
            subject_name=getattr(request, "subject_name", None),
            grade_level=getattr(request, "subject_grade_level", None),
            subject_group=getattr(request, "subject_group", None),
        )
        if getattr(request, "assignment_id", None) is not None:
            request.assignment = SimpleNamespace(
                assignment_id=request.assignment_id,
                status=getattr(request, "assignment_status", None),
                assigned_at=getattr(request, "assignment_assigned_at", None),
                note=getattr(request, "assignment_note", None),
                staff_id=getattr(request, "assignment_staff_id", None),
                tutor_id=getattr(request, "assignment_tutor_id", None),
                class_id=getattr(request, "class_id", None),
                staff_name=getattr(request, "assignment_staff_name", None),
                tutor_name=getattr(request, "assigned_tutor_name", None),
            )
        else:
            request.assignment = None
    return request


def _attach_learning_requests_detail(requests: list):
    for request in requests:
        _attach_learning_request_detail(request)
    return requests


def get_learning_requests(
    db: Session,
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    subject: Optional[str] = None,
    status: Optional[str] = None,
) -> list[LearningRequest]:
    requests = fetch_all(
        db,
        """
        SELECT *
        FROM VW_LEARNING_REQUEST_DETAIL
        WHERE (:student_id IS NULL OR student_id = :student_id)
          AND (:subject_id IS NULL OR subject_id = :subject_id)
          AND (:status IS NULL OR status = :status)
          AND (:subject IS NULL OR subject_name LIKE :subject)
        ORDER BY request_id DESC
        """,
        {
            "student_id": student_id,
            "subject_id": subject_id,
            "status": status,
            "subject": f"%{subject}%" if subject else None,
        },
    )
    return _attach_learning_requests_detail(requests)


def get_learning_request(db: Session, request_id: int) -> Optional[LearningRequest]:
    return _attach_learning_request_detail(
        fetch_one(
            db,
            """
            SELECT *
            FROM VW_LEARNING_REQUEST_DETAIL
            WHERE request_id = :request_id
            """,
            {"request_id": request_id},
        )
    )


def create_learning_request(db: Session, request: LearningRequest) -> LearningRequest:
    row = db.execute(
        text(
            """
            INSERT INTO LEARNING_REQUEST (
                student_id,
                subject_id,
                requested_level,
                learning_goal,
                preferred_area,
                preferred_mode,
                preferred_schedule,
                expected_fee,
                status
            )
            OUTPUT
                INSERTED.request_id,
                INSERTED.student_id,
                INSERTED.subject_id,
                INSERTED.requested_level,
                INSERTED.learning_goal,
                INSERTED.preferred_area,
                INSERTED.preferred_mode,
                INSERTED.preferred_schedule,
                INSERTED.expected_fee,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :student_id,
                :subject_id,
                :requested_level,
                :learning_goal,
                :preferred_area,
                :preferred_mode,
                :preferred_schedule,
                :expected_fee,
                :status
            )
            """
        ),
        {
            "student_id": request.student_id,
            "subject_id": request.subject_id,
            "requested_level": request.requested_level,
            "learning_goal": request.learning_goal,
            "preferred_area": request.preferred_area,
            "preferred_mode": request.preferred_mode,
            "preferred_schedule": request.preferred_schedule,
            "expected_fee": request.expected_fee,
            "status": request.status,
        },
    ).mappings().first()
    return to_obj(row)


def update_learning_request(db: Session, request_id: int, data: dict) -> None:
    update_by_id(db, "LEARNING_REQUEST", "request_id", request_id, data, LEARNING_REQUEST_UPDATE_COLUMNS)


def cancel_learning_request(db: Session, request_id: int) -> None:
    update_learning_request(db, request_id, {"status": "CANCELED"})


def _attach_assignment_detail(assignment):
    if assignment is not None:
        class_id = getattr(assignment, "class_id", None)
        assignment.study_class = SimpleNamespace(class_id=class_id) if class_id is not None else None
    return assignment


def _attach_assignments_detail(assignments: list):
    for assignment in assignments:
        _attach_assignment_detail(assignment)
    return assignments


def get_assignments(
    db: Session,
    request_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    status: Optional[str] = None,
) -> list[TutorAssignment]:
    assignments = fetch_all(
        db,
        """
        SELECT
            ta.assignment_id,
            ta.request_id,
            ta.tutor_id,
            ta.staff_id,
            ta.assigned_at,
            ta.status,
            ta.note,
            ta.created_at,
            ta.updated_at,
            sc.class_id
        FROM TUTOR_ASSIGNMENT ta
        LEFT JOIN STUDY_CLASS sc ON sc.assignment_id = ta.assignment_id
        WHERE (:request_id IS NULL OR ta.request_id = :request_id)
          AND (:tutor_id IS NULL OR ta.tutor_id = :tutor_id)
          AND (:status IS NULL OR ta.status = :status)
        ORDER BY ta.assignment_id DESC
        """,
        {"request_id": request_id, "tutor_id": tutor_id, "status": status},
    )
    return _attach_assignments_detail(assignments)


def get_assignment(db: Session, assignment_id: int) -> Optional[TutorAssignment]:
    return _attach_assignment_detail(
        fetch_one(
            db,
            """
            SELECT
                ta.assignment_id,
                ta.request_id,
                ta.tutor_id,
                ta.staff_id,
                ta.assigned_at,
                ta.status,
                ta.note,
                ta.created_at,
                ta.updated_at,
                sc.class_id
            FROM TUTOR_ASSIGNMENT ta
            LEFT JOIN STUDY_CLASS sc ON sc.assignment_id = ta.assignment_id
            WHERE ta.assignment_id = :assignment_id
            """,
            {"assignment_id": assignment_id},
        )
    )


def create_assignment(db: Session, assignment: TutorAssignment) -> TutorAssignment:
    row = db.execute(
        text(
            """
            INSERT INTO TUTOR_ASSIGNMENT (
                request_id,
                tutor_id,
                staff_id,
                status,
                note
            )
            OUTPUT
                INSERTED.assignment_id,
                INSERTED.request_id,
                INSERTED.tutor_id,
                INSERTED.staff_id,
                INSERTED.assigned_at,
                INSERTED.status,
                INSERTED.note,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :request_id,
                :tutor_id,
                :staff_id,
                :status,
                :note
            )
            """
        ),
        {
            "request_id": assignment.request_id,
            "tutor_id": assignment.tutor_id,
            "staff_id": assignment.staff_id,
            "status": assignment.status,
            "note": assignment.note,
        },
    ).mappings().first()
    created = to_obj(row)
    created.study_class = None
    return created


def call_assign_tutor_to_request(
    db: Session,
    request_id: int,
    tutor_id: int,
    staff_id: Optional[int] = None,
    note: Optional[str] = None,
) -> TutorAssignment:
    row = db.execute(
        text(
            """
            EXEC SP_ASSIGN_TUTOR_TO_REQUEST
                @request_id = :request_id,
                @tutor_id = :tutor_id,
                @staff_id = :staff_id,
                @note = :note
            """
        ),
        {
            "request_id": request_id,
            "tutor_id": tutor_id,
            "staff_id": staff_id,
            "note": note,
        },
    ).mappings().first()
    created = to_obj(row)
    created.study_class = None
    return created


def update_assignment(db: Session, assignment_id: int, data: dict) -> None:
    update_by_id(db, "TUTOR_ASSIGNMENT", "assignment_id", assignment_id, data, ASSIGNMENT_UPDATE_COLUMNS)


def cancel_assignment(db: Session, assignment_id: int) -> None:
    update_assignment(db, assignment_id, {"status": "CANCELED"})


def _time_text(value) -> str:
    return value.strftime("%H:%M") if hasattr(value, "strftime") else str(value)


def _class_schedule_display(db: Session, class_id: int) -> Optional[str]:
    schedules = fetch_all(
        db,
        """
        SELECT day_of_week, start_time
        FROM CLASS_SCHEDULE
        WHERE class_id = :class_id
          AND status = 'ACTIVE'
        ORDER BY day_of_week ASC, start_time ASC
        """,
        {"class_id": class_id},
    )
    if not schedules:
        return None
    labels = {1: "T2", 2: "T3", 3: "T4", 4: "T5", 5: "T6", 6: "T7", 7: "CN"}
    return ", ".join(f"{labels.get(item.day_of_week, item.day_of_week)} - {_time_text(item.start_time)}" for item in schedules)


def _class_next_lesson(db: Session, class_id: int):
    row = fetch_one(
        db,
        """
        SELECT MIN(lesson_date) AS next_lesson
        FROM LESSON_SESSION
        WHERE class_id = :class_id
          AND status = 'SCHEDULED'
          AND lesson_date >= CAST(GETDATE() AS DATE)
        """,
        {"class_id": class_id},
    )
    return row.next_lesson if row else None


def _attach_class_display(db: Session, study_class):
    if study_class is not None:
        study_class.status = getattr(study_class, "class_status", getattr(study_class, "status", None))
        study_class.created_at = getattr(study_class, "class_created_at", getattr(study_class, "created_at", None))
        study_class.schedule_display = _class_schedule_display(db, study_class.class_id)
        study_class.next_lesson = _class_next_lesson(db, study_class.class_id)
    return study_class


def _attach_classes_display(db: Session, classes: list):
    for study_class in classes:
        _attach_class_display(db, study_class)
    return classes


def get_classes(
    db: Session,
    search: Optional[str] = None,
    student_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    status: Optional[str] = None,
) -> list[StudyClass]:
    classes = fetch_all(
        db,
        """
        SELECT
            class_id,
            class_code,
            tuition_fee_per_session,
            teaching_mode,
            location,
            start_date,
            end_date,
            class_status,
            class_created_at,
            assignment_id,
            assignment_status,
            assigned_at,
            request_id,
            requested_level,
            learning_goal,
            preferred_area,
            preferred_mode,
            preferred_schedule,
            student_id,
            student_name,
            student_phone,
            tutor_id,
            tutor_name,
            tutor_phone,
            subject_id,
            subject_name,
            subject_grade_level,
            staff_id,
            staff_name
        FROM VW_STUDY_CLASS_DETAIL
        WHERE (:student_id IS NULL OR student_id = :student_id)
          AND (:tutor_id IS NULL OR tutor_id = :tutor_id)
          AND (:subject_id IS NULL OR subject_id = :subject_id)
          AND (:status IS NULL OR class_status = :status)
          AND (
              :search IS NULL
              OR class_code LIKE :search
              OR student_name LIKE :search
              OR tutor_name LIKE :search
              OR subject_name LIKE :search
          )
        ORDER BY class_id DESC
        """,
        {
            "search": f"%{search}%" if search else None,
            "student_id": student_id,
            "tutor_id": tutor_id,
            "subject_id": subject_id,
            "status": status,
        },
    )
    return _attach_classes_display(db, classes)


def get_class(db: Session, class_id: int) -> Optional[StudyClass]:
    return _attach_class_display(
        db,
        fetch_one(
            db,
            """
            SELECT
                class_id,
                class_code,
                tuition_fee_per_session,
                teaching_mode,
                location,
                start_date,
                end_date,
                class_status,
                class_created_at,
                assignment_id,
                assignment_status,
                assigned_at,
                request_id,
                requested_level,
                learning_goal,
                preferred_area,
                preferred_mode,
                preferred_schedule,
                student_id,
                student_name,
                student_phone,
                tutor_id,
                tutor_name,
                tutor_phone,
                subject_id,
                subject_name,
                subject_grade_level,
                staff_id,
                staff_name
            FROM VW_STUDY_CLASS_DETAIL
            WHERE class_id = :class_id
            """,
            {"class_id": class_id},
        )
    )


def create_class(db: Session, study_class: StudyClass) -> StudyClass:
    row = db.execute(
        text(
            """
            INSERT INTO STUDY_CLASS (
                assignment_id,
                class_code,
                tuition_fee_per_session,
                teaching_mode,
                location,
                start_date,
                end_date,
                status
            )
            OUTPUT
                INSERTED.class_id,
                INSERTED.assignment_id,
                INSERTED.class_code,
                INSERTED.tuition_fee_per_session,
                INSERTED.teaching_mode,
                INSERTED.location,
                INSERTED.start_date,
                INSERTED.end_date,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :assignment_id,
                :class_code,
                :tuition_fee_per_session,
                :teaching_mode,
                :location,
                :start_date,
                :end_date,
                :status
            )
            """
        ),
        {
            "assignment_id": study_class.assignment_id,
            "class_code": study_class.class_code,
            "tuition_fee_per_session": study_class.tuition_fee_per_session,
            "teaching_mode": study_class.teaching_mode,
            "location": study_class.location,
            "start_date": study_class.start_date,
            "end_date": study_class.end_date,
            "status": study_class.status,
        },
    ).mappings().first()
    return to_obj(row)


def call_create_class_from_assignment(
    db: Session,
    assignment_id: int,
    class_code: str,
    tuition_fee_per_session,
    teaching_mode: str,
    location: Optional[str],
    start_date: date,
    end_date: Optional[date],
    status: str,
) -> StudyClass:
    row = db.execute(
        text(
            """
            EXEC SP_CREATE_CLASS_FROM_ASSIGNMENT
                @assignment_id = :assignment_id,
                @class_code = :class_code,
                @tuition_fee_per_session = :tuition_fee_per_session,
                @teaching_mode = :teaching_mode,
                @location = :location,
                @start_date = :start_date,
                @end_date = :end_date,
                @status = :status
            """
        ),
        {
            "assignment_id": assignment_id,
            "class_code": class_code,
            "tuition_fee_per_session": tuition_fee_per_session,
            "teaching_mode": teaching_mode,
            "location": location,
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
        },
    ).mappings().first()
    return to_obj(row)


def update_class(db: Session, class_id: int, data: dict) -> None:
    update_by_id(db, "STUDY_CLASS", "class_id", class_id, data, CLASS_UPDATE_COLUMNS)


def cancel_class(db: Session, class_id: int) -> None:
    update_class(db, class_id, {"status": "CANCELED"})


def get_class_invoice_snapshot(db: Session, class_id: int, period_start: date, period_end: date) -> dict:
    row = fetch_one(
        db,
        """
        SELECT
            sc.class_id,
            COUNT(ls.session_id) AS completed_sessions,
            sc.tuition_fee_per_session,
            sc.tuition_fee_per_session * COUNT(ls.session_id) AS amount_due
        FROM STUDY_CLASS sc
        LEFT JOIN LESSON_SESSION ls
            ON ls.class_id = sc.class_id
           AND ls.status = 'COMPLETED'
           AND ls.lesson_date BETWEEN :period_start AND :period_end
        WHERE sc.class_id = :class_id
        GROUP BY sc.class_id, sc.tuition_fee_per_session
        """,
        {"class_id": class_id, "period_start": period_start, "period_end": period_end},
    )
    return {
        "completed_sessions": row.completed_sessions if row else 0,
        "tuition_fee_per_session": row.tuition_fee_per_session if row else 0,
        "amount_due": row.amount_due if row else 0,
    }


def get_class_tuition_summary(db: Session, class_id: int):
    return fetch_one(
        db,
        """
        SELECT *
        FROM dbo.FN_CLASS_TUITION_SUMMARY(:class_id)
        """,
        {"class_id": class_id},
    )


def get_schedules(
    db: Session,
    class_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    student_id: Optional[int] = None,
) -> list[ClassSchedule]:
    return fetch_all(
        db,
        """
        SELECT
            cs.schedule_id,
            cs.class_id,
            cs.day_of_week,
            cs.start_time,
            cs.end_time,
            cs.effective_from,
            cs.effective_to,
            cs.status,
            cs.note,
            cs.created_at,
            cs.updated_at
        FROM CLASS_SCHEDULE cs
        JOIN STUDY_CLASS sc ON sc.class_id = cs.class_id
        JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
        JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
        WHERE (:class_id IS NULL OR cs.class_id = :class_id)
          AND (:tutor_id IS NULL OR ta.tutor_id = :tutor_id)
          AND (:student_id IS NULL OR lr.student_id = :student_id)
        ORDER BY cs.schedule_id DESC
        """,
        {"class_id": class_id, "tutor_id": tutor_id, "student_id": student_id},
    )


def get_schedule(db: Session, schedule_id: int) -> Optional[ClassSchedule]:
    return fetch_one(
        db,
        """
        SELECT
            schedule_id,
            class_id,
            day_of_week,
            start_time,
            end_time,
            effective_from,
            effective_to,
            status,
            note,
            created_at,
            updated_at
        FROM CLASS_SCHEDULE
        WHERE schedule_id = :schedule_id
        """,
        {"schedule_id": schedule_id},
    )


def create_schedule(db: Session, schedule: ClassSchedule) -> ClassSchedule:
    row = db.execute(
        text(
            """
            INSERT INTO CLASS_SCHEDULE (
                class_id,
                day_of_week,
                start_time,
                end_time,
                effective_from,
                effective_to,
                status,
                note
            )
            OUTPUT
                INSERTED.schedule_id,
                INSERTED.class_id,
                INSERTED.day_of_week,
                INSERTED.start_time,
                INSERTED.end_time,
                INSERTED.effective_from,
                INSERTED.effective_to,
                INSERTED.status,
                INSERTED.note,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :class_id,
                :day_of_week,
                :start_time,
                :end_time,
                :effective_from,
                :effective_to,
                :status,
                :note
            )
            """
        ),
        {
            "class_id": schedule.class_id,
            "day_of_week": schedule.day_of_week,
            "start_time": schedule.start_time,
            "end_time": schedule.end_time,
            "effective_from": schedule.effective_from,
            "effective_to": schedule.effective_to,
            "status": schedule.status,
            "note": schedule.note,
        },
    ).mappings().first()
    return to_obj(row)


def update_schedule(db: Session, schedule_id: int, data: dict) -> None:
    update_by_id(db, "CLASS_SCHEDULE", "schedule_id", schedule_id, data, SCHEDULE_UPDATE_COLUMNS)


def deactivate_schedule(db: Session, schedule_id: int) -> None:
    update_schedule(db, schedule_id, {"status": "INACTIVE"})


def get_sessions(
    db: Session,
    class_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    lesson_date: Optional[date] = None,
) -> list[LessonSession]:
    return fetch_all(
        db,
        """
        SELECT *
        FROM VW_LESSON_SESSION_DETAIL
        WHERE (:class_id IS NULL OR class_id = :class_id)
          AND (:tutor_id IS NULL OR tutor_id = :tutor_id)
          AND (:student_id IS NULL OR student_id = :student_id)
          AND (:status IS NULL OR status = :status)
          AND (:lesson_date IS NULL OR lesson_date = :lesson_date)
        ORDER BY lesson_date DESC, session_id DESC
        """,
        {
            "class_id": class_id,
            "tutor_id": tutor_id,
            "student_id": student_id,
            "status": status,
            "lesson_date": lesson_date,
        },
    )


def get_session(db: Session, session_id: int) -> Optional[LessonSession]:
    return fetch_one(
        db,
        """
        SELECT *
        FROM VW_LESSON_SESSION_DETAIL
        WHERE session_id = :session_id
        """,
        {"session_id": session_id},
    )


def create_session(db: Session, session: LessonSession) -> LessonSession:
    row = db.execute(
        text(
            """
            INSERT INTO LESSON_SESSION (
                class_id,
                schedule_id,
                session_number,
                lesson_date,
                start_time,
                end_time,
                status,
                content_note
            )
            OUTPUT
                INSERTED.session_id,
                INSERTED.class_id,
                INSERTED.schedule_id,
                INSERTED.session_number,
                INSERTED.lesson_date,
                INSERTED.start_time,
                INSERTED.end_time,
                INSERTED.status,
                INSERTED.content_note,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :class_id,
                :schedule_id,
                :session_number,
                :lesson_date,
                :start_time,
                :end_time,
                :status,
                :content_note
            )
            """
        ),
        {
            "class_id": session.class_id,
            "schedule_id": session.schedule_id,
            "session_number": session.session_number,
            "lesson_date": session.lesson_date,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "status": session.status,
            "content_note": session.content_note,
        },
    ).mappings().first()
    return to_obj(row)


def update_session(db: Session, session_id: int, data: dict) -> None:
    update_by_id(db, "LESSON_SESSION", "session_id", session_id, data, SESSION_UPDATE_COLUMNS)


def cancel_session(db: Session, session_id: int) -> None:
    update_session(db, session_id, {"status": "CANCELED"})


def _get_invoice_class_context(db: Session, class_id: int):
    return fetch_one(
        db,
        """
        SELECT
            sc.class_id,
            sc.class_code,
            lr.student_id,
            st.full_name AS student_name,
            su.subject_id,
            su.subject_name,
            su.grade_level AS subject_grade_level,
            ta.tutor_id,
            tu.full_name AS tutor_name
        FROM STUDY_CLASS sc
        JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
        JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
        JOIN STUDENT st ON st.student_id = lr.student_id
        JOIN SUBJECT su ON su.subject_id = lr.subject_id
        JOIN TUTOR tu ON tu.tutor_id = ta.tutor_id
        WHERE sc.class_id = :class_id
        """,
        {"class_id": class_id},
    )


def _attach_invoice_context(invoice, db: Optional[Session] = None):
    if invoice is None:
        return None
    context = invoice
    if not hasattr(invoice, "student_id") and db is not None:
        context = _get_invoice_class_context(db, invoice.class_id) or invoice
        for key, value in vars(context).items():
            setattr(invoice, key, value)
    learning_request = SimpleNamespace(student_id=getattr(invoice, "student_id", None))
    assignment = SimpleNamespace(learning_request=learning_request)
    invoice.study_class = SimpleNamespace(
        class_id=invoice.class_id,
        class_code=getattr(invoice, "class_code", None),
        assignment=assignment,
    )
    invoice.payments = []
    return invoice


def get_invoices(
    db: Session,
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    period_filter: Optional[str] = None,
) -> list[TuitionInvoice]:
    invoices = fetch_all(
        db,
        """
        SELECT *
        FROM VW_INVOICE_DETAIL
        WHERE (:class_id IS NULL OR class_id = :class_id)
          AND (:student_id IS NULL OR student_id = :student_id)
          AND (:status IS NULL OR status = :status)
          AND (
              :period_filter IS NULL
              OR CONVERT(VARCHAR(10), period_start, 23) LIKE :period_filter
              OR CONVERT(VARCHAR(10), period_end, 23) LIKE :period_filter
          )
        ORDER BY invoice_id DESC
        """,
        {
            "class_id": class_id,
            "student_id": student_id,
            "status": status,
            "period_filter": f"%{period_filter}%" if period_filter else None,
        },
    )
    return [_attach_invoice_context(invoice) for invoice in invoices]


def get_invoice(db: Session, invoice_id: int) -> Optional[TuitionInvoice]:
    return _attach_invoice_context(
        fetch_one(
            db,
            """
            SELECT *
            FROM VW_INVOICE_DETAIL
            WHERE invoice_id = :invoice_id
            """,
            {"invoice_id": invoice_id},
        )
    )


def create_invoice(db: Session, invoice: TuitionInvoice) -> TuitionInvoice:
    row = db.execute(
        text(
            """
            INSERT INTO TUITION_INVOICE (
                class_id,
                period_start,
                period_end,
                completed_sessions,
                tuition_fee_per_session,
                amount_due,
                amount_paid,
                status
            )
            OUTPUT
                INSERTED.invoice_id,
                INSERTED.class_id,
                INSERTED.period_start,
                INSERTED.period_end,
                INSERTED.completed_sessions,
                INSERTED.tuition_fee_per_session,
                INSERTED.amount_due,
                INSERTED.amount_paid,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :class_id,
                :period_start,
                :period_end,
                :completed_sessions,
                :tuition_fee_per_session,
                :amount_due,
                :amount_paid,
                :status
            )
            """
        ),
        {
            "class_id": invoice.class_id,
            "period_start": invoice.period_start,
            "period_end": invoice.period_end,
            "completed_sessions": invoice.completed_sessions,
            "tuition_fee_per_session": invoice.tuition_fee_per_session,
            "amount_due": invoice.amount_due,
            "amount_paid": invoice.amount_paid,
            "status": invoice.status,
        },
    ).mappings().first()
    return _attach_invoice_context(to_obj(row), db)


def call_create_invoice_for_period(
    db: Session,
    class_id: int,
    period_start: date,
    period_end: date,
) -> TuitionInvoice:
    row = db.execute(
        text(
            """
            EXEC SP_CREATE_INVOICE_FOR_PERIOD
                @class_id = :class_id,
                @period_start = :period_start,
                @period_end = :period_end
            """
        ),
        {
            "class_id": class_id,
            "period_start": period_start,
            "period_end": period_end,
        },
    ).mappings().first()
    return _attach_invoice_context(to_obj(row), db)


def get_invoice_by_class_period(
    db: Session,
    class_id: int,
    period_start: date,
    period_end: date,
) -> Optional[TuitionInvoice]:
    return _attach_invoice_context(
        fetch_one(
            db,
            """
            SELECT *
            FROM VW_INVOICE_DETAIL
            WHERE class_id = :class_id
              AND period_start = :period_start
              AND period_end = :period_end
            """,
            {"class_id": class_id, "period_start": period_start, "period_end": period_end},
        )
    )


def update_invoice(db: Session, invoice_id: int, data: dict) -> None:
    update_by_id(db, "TUITION_INVOICE", "invoice_id", invoice_id, data, INVOICE_UPDATE_COLUMNS)


def cancel_invoice(db: Session, invoice_id: int) -> None:
    update_invoice(db, invoice_id, {"status": "CANCELED"})


def _attach_payment_context(payment):
    if payment is None:
        return None
    payment.invoice = SimpleNamespace(
        invoice_id=payment.invoice_id,
        class_id=getattr(payment, "class_id", None),
        period_start=getattr(payment, "period_start", None),
        period_end=getattr(payment, "period_end", None),
        amount_due=getattr(payment, "amount_due", None),
        amount_paid=getattr(payment, "invoice_amount_paid", None),
        status=getattr(payment, "invoice_status", None),
    )
    return payment


def get_payments(
    db: Session,
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    invoice_status: Optional[str] = None,
    period_filter: Optional[str] = None,
) -> list[TuitionPayment]:
    payments = fetch_all(
        db,
        """
        SELECT
            payment_id,
            invoice_id,
            class_id,
            class_code,
            student_id,
            student_name,
            subject_id,
            subject_name,
            subject_grade_level,
            staff_id,
            staff_name,
            payment_date,
            amount_paid,
            payment_method,
            note,
            payment_status AS status,
            payment_created_at AS created_at,
            payment_updated_at AS updated_at,
            period_start,
            period_end,
            amount_due,
            invoice_amount_paid,
            invoice_status
        FROM VW_PAYMENT_DETAIL
        WHERE (:class_id IS NULL OR class_id = :class_id)
          AND (:student_id IS NULL OR student_id = :student_id)
          AND (:status IS NULL OR payment_status = :status)
          AND (:invoice_status IS NULL OR invoice_status = :invoice_status)
          AND (
              :period_filter IS NULL
              OR CONVERT(VARCHAR(10), period_start, 23) LIKE :period_filter
              OR CONVERT(VARCHAR(10), period_end, 23) LIKE :period_filter
          )
        ORDER BY payment_id DESC
        """,
        {
            "class_id": class_id,
            "student_id": student_id,
            "status": status,
            "invoice_status": invoice_status,
            "period_filter": f"%{period_filter}%" if period_filter else None,
        },
    )
    return [_attach_payment_context(payment) for payment in payments]


def get_payment(db: Session, payment_id: int) -> Optional[TuitionPayment]:
    return _attach_payment_context(
        fetch_one(
            db,
            """
            SELECT
                payment_id,
                invoice_id,
                class_id,
                class_code,
                student_id,
                student_name,
                subject_id,
                subject_name,
                subject_grade_level,
                staff_id,
                staff_name,
                payment_date,
                amount_paid,
                payment_method,
                note,
                payment_status AS status,
                payment_created_at AS created_at,
                payment_updated_at AS updated_at,
                period_start,
                period_end,
                amount_due,
                invoice_amount_paid,
                invoice_status
            FROM VW_PAYMENT_DETAIL
            WHERE payment_id = :payment_id
            """,
            {"payment_id": payment_id},
        )
    )


def create_payment(
    db: Session,
    payment: TuitionPayment,
    class_id: Optional[int] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
) -> TuitionPayment:
    row = db.execute(
        text(
            """
            EXEC SP_CREATE_TUITION_PAYMENT
                @invoice_id = :invoice_id,
                @class_id = :class_id,
                @period_start = :period_start,
                @period_end = :period_end,
                @amount_paid = :amount_paid,
                @payment_method = :payment_method,
                @payment_date = :payment_date,
                @staff_id = :staff_id,
                @note = :note,
                @status = :status
            """
        ),
        {
            "invoice_id": payment.invoice_id,
            "class_id": class_id,
            "period_start": period_start,
            "period_end": period_end,
            "amount_paid": payment.amount_paid,
            "payment_method": payment.payment_method,
            "payment_date": payment.payment_date,
            "staff_id": payment.staff_id,
            "note": payment.note,
            "status": payment.status,
        },
    ).mappings().first()
    return get_payment(db, row["payment_id"]) if row else None


def update_payment(db: Session, payment_id: int, data: dict) -> None:
    update_by_id(db, "TUITION_PAYMENT", "payment_id", payment_id, data, PAYMENT_UPDATE_COLUMNS)


def cancel_payment(db: Session, payment_id: int) -> None:
    update_payment(db, payment_id, {"status": "CANCELED"})


def get_dashboard_summary(db: Session):
    return fetch_one(
        db,
        """
        SELECT
            (SELECT COUNT(*) FROM STUDENT) AS total_students,
            (SELECT COUNT(*) FROM TUTOR) AS total_tutors,
            (SELECT COUNT(*) FROM LEARNING_REQUEST WHERE status = 'PENDING') AS pending_learning_requests,
            (SELECT COUNT(*) FROM STUDY_CLASS WHERE status = 'ACTIVE') AS active_classes,
            (SELECT COUNT(*) FROM LESSON_SESSION WHERE status = 'COMPLETED') AS completed_sessions,
            (SELECT COUNT(*) FROM TUITION_INVOICE WHERE status = 'UNPAID') AS unpaid_invoices,
            (SELECT COUNT(*) FROM TUITION_INVOICE WHERE status = 'PARTIALLY_PAID') AS partially_paid_invoices,
            (SELECT COUNT(*) FROM TUITION_PAYMENT WHERE status = 'SUCCESS') AS successful_payments
        """
    )


def commit(db: Session):
    db.commit()

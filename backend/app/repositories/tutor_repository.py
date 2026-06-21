from types import SimpleNamespace
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import Subject, Tutor, TutorAvailability, TutorCapability
from app.repositories.repository_common import (
    SUBJECT_UPDATE_COLUMNS,
    TUTOR_AVAILABILITY_UPDATE_COLUMNS,
    TUTOR_CAPABILITY_UPDATE_COLUMNS,
    TUTOR_UPDATE_COLUMNS,
    execute,
    fetch_all,
    fetch_one,
    to_obj,
    update_by_id,
)

#Lấy tất cả thuộc tính từ bảng TUTOR
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

#Lấy danh sách môn học của gia sư
def _attach_tutor_capabilities(db: Session, tutor):
    if tutor is not None:
        tutor.capabilities = get_tutor_capabilities(db, tutor.tutor_id)
    return tutor

#
def _attach_tutors_capabilities(db: Session, tutors: list):
    for tutor in tutors:
        _attach_tutor_capabilities(db, tutor)
    return tutors

#Tìm kiếm và lọc danh sách gia sư theo nhiều tiêu chí
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

#Lấy thông tin chi tiết của 1 gia sư
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

#Truy vấn gia sư theo account_id
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

#Tạo tài khoản gia sư mới
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

#Cập nhật thông tin gia sư
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

#Chuyển trạng thái khóa tài khoản gia sư
def deactivate_tutor(db: Session, tutor_id: int) -> None:
    update_tutor(db, tutor_id, {"status": "INACTIVE"})

#Lấy tất cả môn học
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

#Lấy thông tin môn học theo ID
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

#Tìm môn học dựa trên tên chính xác và cấp lớp
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

#Tọa mới môn học, sử dụng OUTPUT để lấy lại dữ liệu vừa insert
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
    created.subject = get_subject(db, created.subject_id)
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

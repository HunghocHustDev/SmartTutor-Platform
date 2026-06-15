from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import Student
from app.repositories.repository_common import STUDENT_UPDATE_COLUMNS, fetch_all, fetch_one, to_obj, update_by_id


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

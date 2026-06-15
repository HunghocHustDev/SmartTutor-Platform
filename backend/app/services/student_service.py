from sqlalchemy.orm import Session

from app.models import Student
from app.repositories import data_repository as repo
from app.schemas.entities import StudentCreate, StudentUpdate
from app.services.common import ACTIVE_INACTIVE_STATUSES, _normalize_choice, get_student_or_404, student_to_response


def list_students(db: Session, **filters) -> list[dict]:
    return [student_to_response(item) for item in repo.get_students(db, **filters)]


def create_student(db: Session, payload: StudentCreate) -> dict:
    status = _normalize_choice(payload.status, ACTIVE_INACTIVE_STATUSES, "status")
    student = repo.create_student(
        db,
        Student(
            full_name=payload.full_name,
            phone=payload.phone,
            contact_email=payload.email,
            area=payload.area,
            current_level=payload.level,
            grade_level=payload.level,
            status=status,
        ),
    )
    repo.commit(db)
    return student_to_response(student)


def update_student(db: Session, student_id: int, payload: StudentUpdate) -> dict:
    get_student_or_404(db, student_id)
    data = payload.model_dump(exclude_unset=True)
    if "status" in data:
        data["status"] = _normalize_choice(data["status"], ACTIVE_INACTIVE_STATUSES, "status")
    if "level" in data:
        level = data.pop("level")
        data["current_level"] = level
        data["grade_level"] = level
    if "email" in data:
        data["contact_email"] = data.pop("email")
    repo.update_student(db, student_id, data)
    repo.commit(db)
    return student_to_response(repo.get_student(db, student_id))


def deactivate_student(db: Session, student_id: int) -> dict:
    get_student_or_404(db, student_id)
    repo.deactivate_student(db, student_id)
    repo.commit(db)
    return {"detail": "Student deactivated"}

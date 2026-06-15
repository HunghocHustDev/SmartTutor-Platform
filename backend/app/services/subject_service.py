from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Subject
from app.repositories import data_repository as repo
from app.schemas.entities import SubjectCreate, SubjectUpdate
from app.services.common import ACTIVE_INACTIVE_STATUSES, _normalize_choice, get_subject_or_404, subject_to_response


def list_subjects(db: Session, status: str | None = None) -> list[dict]:
    return [subject_to_response(item) for item in repo.get_subjects(db, status=status)]


def create_subject(db: Session, payload: SubjectCreate) -> dict:
    status = _normalize_choice(payload.status, ACTIVE_INACTIVE_STATUSES, "status")
    if repo.get_subject_by_name_level(db, payload.name, payload.level):
        raise HTTPException(status_code=409, detail="Subject already exists for this level")
    subject = repo.create_subject(
        db,
        Subject(
            subject_name=payload.name,
            subject_group=payload.subject_group,
            grade_level=payload.level,
            description=payload.description,
            status=status,
        ),
    )
    repo.commit(db)
    return subject_to_response(subject)


def update_subject(db: Session, subject_id: int, payload: SubjectUpdate) -> dict:
    subject = get_subject_or_404(db, subject_id)
    data = payload.model_dump(exclude_unset=True)
    if "status" in data:
        data["status"] = _normalize_choice(data["status"], ACTIVE_INACTIVE_STATUSES, "status")
    next_name = data.get("name", subject.subject_name)
    next_level = data.get("level", subject.grade_level)
    duplicate = repo.get_subject_by_name_level(db, next_name, next_level)
    if duplicate and duplicate.subject_id != subject_id:
        raise HTTPException(status_code=409, detail="Subject already exists for this level")
    if "name" in data:
        data["subject_name"] = data.pop("name")
    if "level" in data:
        data["grade_level"] = data.pop("level")
    repo.update_subject(db, subject_id, data)
    repo.commit(db)
    return subject_to_response(repo.get_subject(db, subject_id))


def deactivate_subject(db: Session, subject_id: int) -> dict:
    get_subject_or_404(db, subject_id)
    repo.deactivate_subject(db, subject_id)
    repo.commit(db)
    return {"detail": "Subject deactivated"}

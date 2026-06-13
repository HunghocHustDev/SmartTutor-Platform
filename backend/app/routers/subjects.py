from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import DetailMessage, SubjectCreate, SubjectResponse, SubjectUpdate, TutorResponse
from app.services import business_service as service


router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=list[SubjectResponse])
def get_subjects(
    status: Optional[str] = None,
    _: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    return service.list_subjects(db, status=status)


@router.post("", response_model=SubjectResponse)
def create_subject(
    payload: SubjectCreate,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.create_subject(db, payload)


@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: int,
    _: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    return service.subject_to_response(service.get_subject_or_404(db, subject_id))


@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.update_subject(db, subject_id, payload)


@router.delete("/{subject_id}", response_model=DetailMessage)
def delete_subject(
    subject_id: int,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.deactivate_subject(db, subject_id)


@router.get("/{subject_id}/tutors", response_model=list[TutorResponse])
def get_subject_tutors(
    subject_id: int,
    _: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    subject = service.get_subject_or_404(db, subject_id)
    return service.list_tutors(db, subject=subject.subject_name)

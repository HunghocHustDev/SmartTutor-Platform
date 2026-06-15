from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, get_current_actor
from app.database import get_db
from app.schemas.entities import DetailMessage, TutorSubjectCreate, TutorSubjectResponse
from app.services import business_service as service

from app.routers.tutor_router_support import ensure_tutor_or_staff


router = APIRouter()


@router.get("/{tutor_id}/subjects", response_model=list[TutorSubjectResponse])
def get_tutor_subjects(
    tutor_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_tutor_or_staff(actor, tutor_id)
    return service.list_tutor_subjects(db, tutor_id)


@router.post("/{tutor_id}/subjects", response_model=TutorSubjectResponse)
def add_tutor_subject(
    tutor_id: int,
    payload: TutorSubjectCreate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_tutor_or_staff(actor, tutor_id)
    return service.add_tutor_subject(db, tutor_id, payload)


@router.delete("/{tutor_id}/subjects/{subject_id}", response_model=DetailMessage)
def remove_tutor_subject(
    tutor_id: int,
    subject_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_tutor_or_staff(actor, tutor_id)
    return service.remove_tutor_subject(db, tutor_id, subject_id)


@router.get("/{tutor_id}/capabilities", response_model=list[TutorSubjectResponse])
def get_tutor_capabilities(
    tutor_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_tutor_or_staff(actor, tutor_id)
    return service.list_tutor_subjects(db, tutor_id)


@router.post("/{tutor_id}/capabilities", response_model=TutorSubjectResponse)
def add_tutor_capability(
    tutor_id: int,
    payload: TutorSubjectCreate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_tutor_or_staff(actor, tutor_id)
    return service.add_tutor_subject(db, tutor_id, payload)


@router.delete("/{tutor_id}/capabilities/{capability_id}", response_model=DetailMessage)
def remove_tutor_capability(
    tutor_id: int,
    capability_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_tutor_or_staff(actor, tutor_id)
    return service.remove_tutor_capability(db, tutor_id, capability_id)

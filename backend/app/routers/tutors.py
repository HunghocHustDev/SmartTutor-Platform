from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import (
    ClassScheduleResponse,
    DetailMessage,
    StudyClassResponse,
    TutorAvailabilityCreate,
    TutorAvailabilityResponse,
    TutorAvailabilityUpdate,
    TutorCreate,
    TutorResponse,
    TutorSubjectCreate,
    TutorSubjectResponse,
    TutorUpdate,
)
from app.services import business_service as service


router = APIRouter(prefix="/tutors", tags=["tutors"])


def _ensure_tutor_or_staff(actor: CurrentActor, tutor_id: int) -> None:
    if actor.role == "staff":
        return
    if actor.role == "tutor" and actor.tutor_id == tutor_id:
        return
    raise HTTPException(status_code=403, detail="Only staff or the owning tutor can access this data")


@router.get("", response_model=list[TutorResponse])
def get_tutors(
    search: Optional[str] = None,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    area: Optional[str] = None,
    subject: Optional[str] = None,
    status: Optional[str] = None,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    if actor.role == "tutor":
        return [service.tutor_to_response(service.get_tutor_or_404(db, actor.tutor_id))]
    if actor.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff or the owning tutor can view tutor profiles")
    return service.list_tutors(
        db,
        search=search,
        name=name,
        phone=phone,
        email=email,
        area=area,
        subject=subject,
        status=status,
    )


@router.get("/search", response_model=list[TutorResponse])
def search_tutors(
    subject_id: Optional[int] = None,
    subject: Optional[str] = None,
    area: Optional[str] = None,
    mode: Optional[str] = None,
    actor: CurrentActor = Depends(get_current_actor),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    del mode
    if actor.role not in {"staff", "student"}:
        raise HTTPException(status_code=403, detail="Only staff or students can search tutors")
    if subject_id:
        subject_obj = service.get_subject_or_404(db, subject_id)
        subject = subject_obj.subject_name
    return service.list_tutors(db, subject=subject, area=area, status=status)


@router.post("", response_model=TutorResponse)
def create_tutor(
    payload: TutorCreate,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.create_tutor(db, payload)


@router.get("/{tutor_id}", response_model=TutorResponse)
def get_tutor(
    tutor_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    return service.tutor_to_response(service.get_tutor_or_404(db, tutor_id))


@router.put("/{tutor_id}", response_model=TutorResponse)
def update_tutor(
    tutor_id: int,
    payload: TutorUpdate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    return service.update_tutor(db, tutor_id, payload)


@router.delete("/{tutor_id}", response_model=DetailMessage)
def delete_tutor(
    tutor_id: int,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.deactivate_tutor(db, tutor_id)


@router.get("/{tutor_id}/classes", response_model=list[StudyClassResponse])
def get_tutor_classes(
    tutor_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    service.get_tutor_or_404(db, tutor_id)
    return service.list_classes(db, tutor_id=tutor_id)


@router.get("/{tutor_id}/schedule", response_model=list[ClassScheduleResponse])
def get_tutor_schedule(
    tutor_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    service.get_tutor_or_404(db, tutor_id)
    return service.list_schedules(db, tutor_id=tutor_id)


@router.get("/{tutor_id}/subjects", response_model=list[TutorSubjectResponse])
def get_tutor_subjects(
    tutor_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    return service.list_tutor_subjects(db, tutor_id)


@router.post("/{tutor_id}/subjects", response_model=TutorSubjectResponse)
def add_tutor_subject(
    tutor_id: int,
    payload: TutorSubjectCreate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    return service.add_tutor_subject(db, tutor_id, payload)


@router.delete("/{tutor_id}/subjects/{subject_id}", response_model=DetailMessage)
def remove_tutor_subject(
    tutor_id: int,
    subject_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    return service.remove_tutor_subject(db, tutor_id, subject_id)


@router.get("/{tutor_id}/capabilities", response_model=list[TutorSubjectResponse])
def get_tutor_capabilities(
    tutor_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    return service.list_tutor_subjects(db, tutor_id)


@router.post("/{tutor_id}/capabilities", response_model=TutorSubjectResponse)
def add_tutor_capability(
    tutor_id: int,
    payload: TutorSubjectCreate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    return service.add_tutor_subject(db, tutor_id, payload)


@router.delete("/{tutor_id}/capabilities/{capability_id}", response_model=DetailMessage)
def remove_tutor_capability(
    tutor_id: int,
    capability_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    return service.remove_tutor_capability(db, tutor_id, capability_id)


@router.get("/{tutor_id}/availability", response_model=list[TutorAvailabilityResponse])
def get_tutor_availability(
    tutor_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    return service.list_tutor_availabilities(db, tutor_id)


@router.post("/{tutor_id}/availability", response_model=TutorAvailabilityResponse)
def create_tutor_availability(
    tutor_id: int,
    payload: TutorAvailabilityCreate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    return service.create_tutor_availability(db, tutor_id, payload)


@router.put("/{tutor_id}/availability/{availability_id}", response_model=TutorAvailabilityResponse)
def update_tutor_availability(
    tutor_id: int,
    availability_id: int,
    payload: TutorAvailabilityUpdate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    return service.update_tutor_availability(db, tutor_id, availability_id, payload)


@router.delete("/{tutor_id}/availability/{availability_id}", response_model=DetailMessage)
def delete_tutor_availability(
    tutor_id: int,
    availability_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    _ensure_tutor_or_staff(actor, tutor_id)
    return service.delete_tutor_availability(db, tutor_id, availability_id)

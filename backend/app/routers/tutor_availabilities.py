from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, get_current_actor
from app.database import get_db
from app.schemas.entities import DetailMessage, TutorAvailabilityCreate, TutorAvailabilityResponse, TutorAvailabilityUpdate
from app.services import business_service as service

from app.routers.tutor_router_support import ensure_tutor_or_staff


router = APIRouter()


@router.get("/{tutor_id}/availability", response_model=list[TutorAvailabilityResponse])
def get_tutor_availability(
    tutor_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_tutor_or_staff(actor, tutor_id)
    return service.list_tutor_availabilities(db, tutor_id)


@router.post("/{tutor_id}/availability", response_model=TutorAvailabilityResponse)
def create_tutor_availability(
    tutor_id: int,
    payload: TutorAvailabilityCreate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_tutor_or_staff(actor, tutor_id)
    return service.create_tutor_availability(db, tutor_id, payload)


@router.put("/{tutor_id}/availability/{availability_id}", response_model=TutorAvailabilityResponse)
def update_tutor_availability(
    tutor_id: int,
    availability_id: int,
    payload: TutorAvailabilityUpdate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_tutor_or_staff(actor, tutor_id)
    return service.update_tutor_availability(db, tutor_id, availability_id, payload)


@router.delete("/{tutor_id}/availability/{availability_id}", response_model=DetailMessage)
def delete_tutor_availability(
    tutor_id: int,
    availability_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_tutor_or_staff(actor, tutor_id)
    return service.delete_tutor_availability(db, tutor_id, availability_id)

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, ensure_schedule_access, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import ClassScheduleCreate, ClassScheduleResponse, ClassScheduleUpdate, DetailMessage
from app.services import business_service as service


router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("", response_model=list[ClassScheduleResponse])
def get_schedules(
    class_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    student_id: Optional[int] = None,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    if actor.role == "student":
        student_id = actor.student_id
    elif actor.role == "tutor":
        tutor_id = actor.tutor_id
    elif actor.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff, the owning student, or the assigned tutor can view schedules")

    return service.list_schedules(db, class_id=class_id, tutor_id=tutor_id, student_id=student_id)


@router.post("", response_model=ClassScheduleResponse)
def create_schedule(
    payload: ClassScheduleCreate,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.create_schedule(db, payload)


@router.get("/{schedule_id}", response_model=ClassScheduleResponse)
def get_schedule(
    schedule_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    schedule = service.get_schedule_or_404(db, schedule_id)
    ensure_schedule_access(db, actor, schedule)
    return service.schedule_to_response(schedule)


@router.put("/{schedule_id}", response_model=ClassScheduleResponse)
def update_schedule(
    schedule_id: int,
    payload: ClassScheduleUpdate,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.update_schedule(db, schedule_id, payload)


@router.delete("/{schedule_id}", response_model=DetailMessage)
def delete_schedule(
    schedule_id: int,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.delete_schedule(db, schedule_id)

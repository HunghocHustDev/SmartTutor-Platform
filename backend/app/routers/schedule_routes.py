from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, ensure_schedule_access, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import ClassScheduleCreate, ClassScheduleResponse, ClassScheduleUpdate, DetailMessage
from app.services import business_service as service

from app.routers.class_router_support import apply_class_actor_filters, ensure_staff_student_or_tutor


router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("", response_model=list[ClassScheduleResponse])
def get_schedules(
    class_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    student_id: Optional[int] = None,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_staff_student_or_tutor(actor, "Only staff, the owning student, or the assigned tutor can view schedules")
    student_id, tutor_id = apply_class_actor_filters(actor, student_id, tutor_id)
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

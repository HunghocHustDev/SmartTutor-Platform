from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, get_current_actor
from app.database import get_db
from app.schemas.entities import LearningRequestResponse, LessonSessionResponse, StudyClassResponse
from app.services import business_service as service

from app.routers.student_router_support import ensure_student_or_staff


router = APIRouter()


@router.get("/{student_id}/learning-requests", response_model=list[LearningRequestResponse])
def get_student_learning_requests(
    student_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_student_or_staff(actor, student_id, "Only staff or the owning student can access these learning requests")
    service.get_student_or_404(db, student_id)
    return service.list_learning_requests(db, student_id=student_id)


@router.get("/{student_id}/classes", response_model=list[StudyClassResponse])
def get_student_classes(
    student_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_student_or_staff(actor, student_id, "Only staff or the owning student can access these classes")
    service.get_student_or_404(db, student_id)
    return service.list_classes(db, student_id=student_id)


@router.get("/{student_id}/schedule", response_model=list[LessonSessionResponse])
def get_student_schedule(
    student_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_student_or_staff(actor, student_id, "Only staff or the owning student can access this schedule")
    service.get_student_or_404(db, student_id)
    return service.list_sessions(db, student_id=student_id)

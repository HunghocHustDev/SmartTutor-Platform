from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, ensure_class_access, ensure_session_access, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import DetailMessage, LessonSessionCreate, LessonSessionResponse, LessonSessionStatusUpdate, LessonSessionUpdate
from app.services import business_service as service

from app.routers.class_router_support import apply_class_actor_filters, ensure_staff_student_or_tutor


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[LessonSessionResponse])
def get_sessions(
    class_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    session_date: Optional[date] = Query(default=None, alias="date"),
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_staff_student_or_tutor(actor, "Only staff, the owning student, or the assigned tutor can view sessions")
    student_id, tutor_id = apply_class_actor_filters(actor, student_id, tutor_id)
    return service.list_sessions(
        db,
        class_id=class_id,
        tutor_id=tutor_id,
        student_id=student_id,
        status=status,
        session_date=session_date,
    )


@router.post("", response_model=LessonSessionResponse)
def create_session(
    payload: LessonSessionCreate,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.create_session(db, payload)


@router.get("/{session_id}", response_model=LessonSessionResponse)
def get_session(
    session_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    session = service.get_session_or_404(db, session_id)
    ensure_session_access(db, actor, session)
    return service.session_to_response(session)


@router.put("/{session_id}", response_model=LessonSessionResponse)
def update_session(
    session_id: int,
    payload: LessonSessionUpdate,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.update_session(db, session_id, payload)


@router.delete("/{session_id}", response_model=DetailMessage)
def delete_session(
    session_id: int,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.delete_session(db, session_id)


@router.patch("/{session_id}/status", response_model=LessonSessionResponse)
def update_session_status(
    session_id: int,
    payload: LessonSessionStatusUpdate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    session = service.get_session_or_404(db, session_id)
    if actor.role == "tutor":
        study_class = service.get_class_or_404(db, session.class_id)
        ensure_class_access(actor, study_class)
    elif actor.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff or the assigned tutor can update session status")
    return service.update_session_status(db, session_id, payload)

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, ensure_class_access, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import DetailMessage, StudyClassCreate, StudyClassResponse, StudyClassUpdate
from app.services import business_service as service

from app.routers.class_router_support import apply_class_actor_filters, ensure_staff_student_or_tutor


router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("", response_model=list[StudyClassResponse])
def get_classes(
    search: Optional[str] = None,
    student_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    status: Optional[str] = None,
    open_for_tutor: Optional[bool] = None,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    del open_for_tutor
    ensure_staff_student_or_tutor(actor, "Only staff, the owning student, or the assigned tutor can view classes")
    student_id, tutor_id = apply_class_actor_filters(actor, student_id, tutor_id)
    return service.list_classes(
        db,
        search=search,
        student_id=student_id,
        tutor_id=tutor_id,
        subject_id=subject_id,
        status=status,
    )


@router.post("", response_model=StudyClassResponse)
def create_class(
    payload: StudyClassCreate,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.create_study_class(db, payload)


@router.get("/{class_id}", response_model=StudyClassResponse)
def get_class(
    class_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    study_class = service.get_class_or_404(db, class_id)
    ensure_class_access(actor, study_class)
    return service.class_to_response(study_class)


@router.put("/{class_id}", response_model=StudyClassResponse)
def update_class(
    class_id: int,
    payload: StudyClassUpdate,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.update_study_class(db, class_id, payload)


@router.delete("/{class_id}", response_model=DetailMessage)
def delete_class(
    class_id: int,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.cancel_study_class(db, class_id)

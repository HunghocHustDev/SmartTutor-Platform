from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, ensure_learning_request_access, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import DetailMessage, LearningRequestCreate, LearningRequestResponse, LearningRequestUpdate
from app.services import business_service as service

from app.routers.learning_request_router_support import ensure_learning_request_create_owner, ensure_staff_or_student_learning_request_list


router = APIRouter(prefix="/learning-requests", tags=["learning-requests"])


@router.get("", response_model=list[LearningRequestResponse])
def get_learning_requests(
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    subject: Optional[str] = None,
    status: Optional[str] = None,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_staff_or_student_learning_request_list(actor)
    if actor.role == "student":
        student_id = actor.student_id
    return service.list_learning_requests(
        db,
        student_id=student_id,
        subject_id=subject_id,
        subject=subject,
        status=status,
    )


@router.post("", response_model=LearningRequestResponse)
def create_learning_request(
    payload: LearningRequestCreate,
    actor: CurrentActor = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    ensure_learning_request_create_owner(actor, payload.student_id)
    return service.create_learning_request(db, payload)


@router.get("/{request_id}", response_model=LearningRequestResponse)
def get_learning_request(
    request_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    learning_request = service.get_learning_request_or_404(db, request_id)
    ensure_learning_request_access(actor, learning_request)
    return service.learning_request_to_response(learning_request)


@router.put("/{request_id}", response_model=LearningRequestResponse)
def update_learning_request(
    request_id: int,
    payload: LearningRequestUpdate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    learning_request = service.get_learning_request_or_404(db, request_id)
    ensure_learning_request_access(actor, learning_request)
    return service.update_learning_request(db, request_id, payload)


@router.delete("/{request_id}", response_model=DetailMessage)
def delete_learning_request(
    request_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    learning_request = service.get_learning_request_or_404(db, request_id)
    ensure_learning_request_access(actor, learning_request)
    return service.cancel_learning_request(db, request_id)

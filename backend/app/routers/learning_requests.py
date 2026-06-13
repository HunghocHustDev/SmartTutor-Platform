from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, ensure_learning_request_access, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import DetailMessage, LearningRequestCreate, LearningRequestResponse, LearningRequestUpdate
from app.services import business_service as service


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
    if actor.role == "student":
        student_id = actor.student_id
    elif actor.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff or the owning student can view learning requests")

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
    if actor.student_id is None or payload.student_id != actor.student_id:
        raise HTTPException(status_code=403, detail="Students can only create their own learning requests")
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

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, ensure_assignment_access, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import DetailMessage, TutorAssignmentCreate, TutorAssignmentResponse, TutorAssignmentUpdate
from app.services import business_service as service

from app.routers.learning_request_router_support import apply_assignment_staff


router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.get("", response_model=list[TutorAssignmentResponse])
def get_assignments(
    request_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    status: Optional[str] = None,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    if actor.role == "tutor":
        tutor_id = actor.tutor_id
    elif actor.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff or the assigned tutor can view assignments")
    return service.list_assignments(db, request_id=request_id, tutor_id=tutor_id, status=status)


@router.post("", response_model=TutorAssignmentResponse)
def create_assignment(
    payload: TutorAssignmentCreate,
    actor: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.create_assignment(db, apply_assignment_staff(payload, actor))


@router.get("/{assignment_id}", response_model=TutorAssignmentResponse)
def get_assignment(
    assignment_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    assignment = service.get_assignment_or_404(db, assignment_id)
    ensure_assignment_access(actor, assignment)
    return service.assignment_to_response(assignment)


@router.put("/{assignment_id}", response_model=TutorAssignmentResponse)
def update_assignment(
    assignment_id: int,
    payload: TutorAssignmentUpdate,
    actor: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.update_assignment(db, assignment_id, apply_assignment_staff(payload, actor))


@router.patch("/{assignment_id}/cancel", response_model=DetailMessage)
def cancel_assignment(
    assignment_id: int,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.cancel_assignment(db, assignment_id)


@router.delete("/{assignment_id}", response_model=DetailMessage)
def delete_assignment(
    assignment_id: int,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.cancel_assignment(db, assignment_id)

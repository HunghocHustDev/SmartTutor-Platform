from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, ensure_payment_access, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import DetailMessage, TuitionPaymentCreate, TuitionPaymentResponse, TuitionPaymentUpdate
from app.services import business_service as service


router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("", response_model=list[TuitionPaymentResponse])
def get_payments(
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    period: Optional[str] = None,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    if actor.role == "student":
        student_id = actor.student_id
    elif actor.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff or the owning student can view payments")
    return service.list_payments(db, class_id=class_id, student_id=student_id, status=status, period_filter=period)


@router.post("", response_model=TuitionPaymentResponse)
def create_payment(
    payload: TuitionPaymentCreate,
    actor: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    if payload.staff_id is None and actor.staff_id is not None:
        payload = payload.model_copy(update={"staff_id": actor.staff_id})
    return service.create_payment(db, payload)


@router.get("/{payment_id}", response_model=TuitionPaymentResponse)
def get_payment(
    payment_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    payment = service.get_payment_or_404(db, payment_id)
    ensure_payment_access(db, actor, payment)
    return service.payment_to_response(payment)


@router.put("/{payment_id}", response_model=TuitionPaymentResponse)
def update_payment(
    payment_id: int,
    payload: TuitionPaymentUpdate,
    actor: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    if payload.staff_id is None and actor.staff_id is not None:
        payload = payload.model_copy(update={"staff_id": actor.staff_id})
    return service.update_payment(db, payment_id, payload)


@router.delete("/{payment_id}", response_model=DetailMessage)
def delete_payment(
    payment_id: int,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.delete_payment(db, payment_id)

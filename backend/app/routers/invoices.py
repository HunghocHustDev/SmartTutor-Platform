from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, ensure_invoice_access, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import DetailMessage, TuitionInvoiceCreate, TuitionInvoiceResponse, TuitionInvoiceUpdate
from app.services import business_service as service


router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=list[TuitionInvoiceResponse])
def get_invoices(
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
        raise HTTPException(status_code=403, detail="Only staff or the owning student can view invoices")
    return service.list_invoices(db, class_id=class_id, student_id=student_id, status=status, period_filter=period)


@router.post("", response_model=TuitionInvoiceResponse)
def create_invoice(
    payload: TuitionInvoiceCreate,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.create_invoice(db, payload)


@router.get("/{invoice_id}", response_model=TuitionInvoiceResponse)
def get_invoice(
    invoice_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    invoice = service.get_invoice_or_404(db, invoice_id)
    ensure_invoice_access(db, actor, invoice)
    return service.invoice_to_response(invoice)


@router.put("/{invoice_id}", response_model=TuitionInvoiceResponse)
def update_invoice(
    invoice_id: int,
    payload: TuitionInvoiceUpdate,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.update_invoice(db, invoice_id, payload)


@router.delete("/{invoice_id}", response_model=DetailMessage)
def delete_invoice(
    invoice_id: int,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.delete_invoice(db, invoice_id)

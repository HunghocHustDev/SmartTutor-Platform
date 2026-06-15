from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import TuitionPayment
from app.repositories import data_repository as repo
from app.schemas.entities import TuitionInvoiceCreate, TuitionInvoiceUpdate, TuitionPaymentCreate, TuitionPaymentUpdate
from app.services.common import (
    _decimal_money,
    _invoice_remaining_amount,
    _invoice_remaining_amount_excluding_payment,
    _normalize_invoice_status,
    _normalize_payment_status,
    _validate_date_window,
    _validate_invoice_values,
    _validate_positive_decimal,
    get_class_or_404,
    get_invoice_or_404,
    get_payment_or_404,
    get_staff_or_404,
    invoice_to_response,
    payment_to_response,
)


def list_invoices(db: Session, **filters) -> list[dict]:
    if "status" in filters:
        filters["status"] = _normalize_invoice_status(filters["status"])
    period_filter = filters.pop("period", None)
    if period_filter is not None:
        filters["period_filter"] = period_filter
    return [invoice_to_response(item) for item in repo.get_invoices(db, **filters)]


def create_invoice(db: Session, payload: TuitionInvoiceCreate) -> dict:
    get_class_or_404(db, payload.class_id)
    _validate_invoice_values(
        payload.period_start,
        payload.period_end,
        payload.completed_sessions,
        payload.tuition_fee_per_session,
        payload.amount_due,
        payload.amount_paid,
    )
    existing_invoice = repo.get_invoice_by_class_period(db, payload.class_id, payload.period_start, payload.period_end)
    if existing_invoice:
        raise HTTPException(status_code=409, detail="Invoice already exists for this class and period")
    _normalize_invoice_status(payload.status)
    invoice = repo.call_create_invoice_for_period(
        db,
        class_id=payload.class_id,
        period_start=payload.period_start,
        period_end=payload.period_end,
    )
    repo.commit(db)
    return invoice_to_response(repo.get_invoice(db, invoice.invoice_id))


def update_invoice(db: Session, invoice_id: int, payload: TuitionInvoiceUpdate) -> dict:
    invoice = get_invoice_or_404(db, invoice_id)
    data = payload.model_dump(exclude_unset=True)
    _validate_invoice_values(
        data.get("period_start", invoice.period_start),
        data.get("period_end", invoice.period_end),
        data.get("completed_sessions", invoice.completed_sessions),
        data.get("tuition_fee_per_session", invoice.tuition_fee_per_session),
        data.get("amount_due", invoice.amount_due),
        data.get("amount_paid", invoice.amount_paid),
    )
    if "status" in data:
        data["status"] = _normalize_invoice_status(data["status"])
    repo.update_invoice(db, invoice_id, data)
    repo.commit(db)
    return invoice_to_response(repo.get_invoice(db, invoice_id))


def delete_invoice(db: Session, invoice_id: int) -> dict:
    get_invoice_or_404(db, invoice_id)
    repo.cancel_invoice(db, invoice_id)
    repo.commit(db)
    return {"detail": "Invoice canceled"}


def list_payments(db: Session, **filters) -> list[dict]:
    status = filters.pop("status", None)
    period_filter = filters.pop("period", None)
    payment_status = None
    invoice_status = None
    if status:
        normalized = status.upper()
        if normalized in {"PAID", "UNPAID", "PARTIAL", "PARTIALLY_PAID", "OVERDUE"}:
            invoice_status = _normalize_invoice_status(normalized)
        elif normalized in {"SUCCESS", "CANCELED", "REFUNDED"}:
            payment_status = normalized
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported payment filter status: {status}")
    if period_filter is not None:
        filters["period_filter"] = period_filter
    return [payment_to_response(item) for item in repo.get_payments(db, status=payment_status, invoice_status=invoice_status, **filters)]


def create_payment(db: Session, payload: TuitionPaymentCreate) -> dict:
    payment_amount = _decimal_money(payload.amount_paid)
    _validate_positive_decimal(payment_amount, "Payment amount")
    payment_status = _normalize_payment_status(payload.status) if payload.status else "SUCCESS"

    invoice = None
    period_start = None
    period_end = None
    class_student_id = None
    if payload.invoice_id:
        invoice = get_invoice_or_404(db, payload.invoice_id)
        if payload.class_id is not None and invoice.class_id != payload.class_id:
            raise HTTPException(status_code=400, detail="class_id must match invoice_id")
    elif payload.class_id:
        period_start = payload.period_start or date.today().replace(day=1)
        period_end = payload.period_end or date.today()
        _validate_date_window(period_start, period_end, "period_start", "period_end")
        invoice = repo.get_invoice_by_class_period(db, payload.class_id, period_start, period_end)
        if invoice:
            class_student_id = invoice.study_class.assignment.learning_request.student_id
        else:
            study_class = get_class_or_404(db, payload.class_id)
            class_student_id = getattr(study_class, "student_id", None)
    if not invoice and payload.class_id is None:
        raise HTTPException(status_code=400, detail="invoice_id or class_id is required")
    if payload.student_id is not None:
        if invoice is not None:
            class_student_id = invoice.study_class.assignment.learning_request.student_id
        if payload.student_id != class_student_id:
            raise HTTPException(status_code=400, detail="student_id must match the invoice class student")
    if invoice is not None and invoice.status == "CANCELED":
        raise HTTPException(status_code=400, detail="Cannot record payment for a canceled invoice")
    if payload.staff_id is not None:
        get_staff_or_404(db, payload.staff_id)

    if payment_status == "SUCCESS":
        if invoice is not None:
            remaining_amount = _invoice_remaining_amount(invoice)
        else:
            snapshot = repo.get_class_invoice_snapshot(db, payload.class_id, period_start, period_end)
            remaining_amount = _decimal_money(snapshot["amount_due"])
        if payment_amount > remaining_amount:
            raise HTTPException(status_code=400, detail="Payment amount exceeds invoice remaining amount")

    payment = repo.create_payment(
        db,
        TuitionPayment(
            invoice_id=invoice.invoice_id if invoice is not None else None,
            staff_id=payload.staff_id,
            amount_paid=payment_amount,
            payment_date=payload.payment_date or datetime.utcnow(),
            payment_method=payload.payment_method,
            note=payload.note,
            status=payment_status,
        ),
        class_id=payload.class_id if invoice is None else None,
        period_start=period_start if invoice is None else None,
        period_end=period_end if invoice is None else None,
    )
    repo.commit(db)
    return payment_to_response(payment)


def update_payment(db: Session, payment_id: int, payload: TuitionPaymentUpdate) -> dict:
    payment = get_payment_or_404(db, payment_id)
    data = payload.model_dump(exclude_unset=True)
    if "amount_paid" in data:
        data["amount_paid"] = _decimal_money(data["amount_paid"])
        _validate_positive_decimal(data["amount_paid"], "Payment amount")
    if "staff_id" in data and data["staff_id"] is not None:
        get_staff_or_404(db, data["staff_id"])
    if "status" in data:
        data["status"] = _normalize_payment_status(data["status"])
    next_status = data.get("status", payment.status)
    if next_status == "SUCCESS":
        next_amount = data.get("amount_paid", payment.amount_paid)
        remaining_amount = _invoice_remaining_amount_excluding_payment(payment.invoice, payment)
        if _decimal_money(next_amount) > remaining_amount:
            raise HTTPException(status_code=400, detail="Payment amount exceeds invoice remaining amount")
    repo.update_payment(db, payment_id, data)
    repo.commit(db)
    return payment_to_response(repo.get_payment(db, payment_id))


def delete_payment(db: Session, payment_id: int) -> dict:
    get_payment_or_404(db, payment_id)
    repo.cancel_payment(db, payment_id)
    repo.commit(db)
    return {"detail": "Payment canceled"}

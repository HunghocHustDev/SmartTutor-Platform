from datetime import date
from types import SimpleNamespace
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import TuitionInvoice, TuitionPayment
from app.repositories.repository_common import INVOICE_UPDATE_COLUMNS, PAYMENT_UPDATE_COLUMNS, fetch_all, fetch_one, to_obj, update_by_id


def _get_invoice_class_context(db: Session, class_id: int):
    return fetch_one(
        db,
        """
        SELECT
            sc.class_id,
            sc.class_code,
            lr.student_id,
            st.full_name AS student_name,
            su.subject_id,
            su.subject_name,
            su.grade_level AS subject_grade_level,
            ta.tutor_id,
            tu.full_name AS tutor_name
        FROM STUDY_CLASS sc
        JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
        JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
        JOIN STUDENT st ON st.student_id = lr.student_id
        JOIN SUBJECT su ON su.subject_id = lr.subject_id
        JOIN TUTOR tu ON tu.tutor_id = ta.tutor_id
        WHERE sc.class_id = :class_id
        """,
        {"class_id": class_id},
    )


def _attach_invoice_context(invoice, db: Optional[Session] = None):
    if invoice is None:
        return None
    context = invoice
    if not hasattr(invoice, "student_id") and db is not None:
        context = _get_invoice_class_context(db, invoice.class_id) or invoice
        for key, value in vars(context).items():
            setattr(invoice, key, value)
    learning_request = SimpleNamespace(student_id=getattr(invoice, "student_id", None))
    assignment = SimpleNamespace(learning_request=learning_request)
    invoice.study_class = SimpleNamespace(
        class_id=invoice.class_id,
        class_code=getattr(invoice, "class_code", None),
        assignment=assignment,
    )
    invoice.payments = []
    return invoice


def get_invoices(
    db: Session,
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    period_filter: Optional[str] = None,
) -> list[TuitionInvoice]:
    invoices = fetch_all(
        db,
        """
        SELECT *
        FROM VW_INVOICE_DETAIL
        WHERE (:class_id IS NULL OR class_id = :class_id)
          AND (:student_id IS NULL OR student_id = :student_id)
          AND (:status IS NULL OR status = :status)
          AND (
              :period_filter IS NULL
              OR CONVERT(VARCHAR(10), period_start, 23) LIKE :period_filter
              OR CONVERT(VARCHAR(10), period_end, 23) LIKE :period_filter
          )
        ORDER BY invoice_id DESC
        """,
        {
            "class_id": class_id,
            "student_id": student_id,
            "status": status,
            "period_filter": f"%{period_filter}%" if period_filter else None,
        },
    )
    return [_attach_invoice_context(invoice) for invoice in invoices]


def get_invoice(db: Session, invoice_id: int) -> Optional[TuitionInvoice]:
    return _attach_invoice_context(
        fetch_one(
            db,
            """
            SELECT *
            FROM VW_INVOICE_DETAIL
            WHERE invoice_id = :invoice_id
            """,
            {"invoice_id": invoice_id},
        )
    )


def create_invoice(db: Session, invoice: TuitionInvoice) -> TuitionInvoice:
    row = db.execute(
        text(
            """
            INSERT INTO TUITION_INVOICE (
                class_id,
                period_start,
                period_end,
                completed_sessions,
                tuition_fee_per_session,
                amount_due,
                amount_paid,
                status
            )
            OUTPUT
                INSERTED.invoice_id,
                INSERTED.class_id,
                INSERTED.period_start,
                INSERTED.period_end,
                INSERTED.completed_sessions,
                INSERTED.tuition_fee_per_session,
                INSERTED.amount_due,
                INSERTED.amount_paid,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :class_id,
                :period_start,
                :period_end,
                :completed_sessions,
                :tuition_fee_per_session,
                :amount_due,
                :amount_paid,
                :status
            )
            """
        ),
        {
            "class_id": invoice.class_id,
            "period_start": invoice.period_start,
            "period_end": invoice.period_end,
            "completed_sessions": invoice.completed_sessions,
            "tuition_fee_per_session": invoice.tuition_fee_per_session,
            "amount_due": invoice.amount_due,
            "amount_paid": invoice.amount_paid,
            "status": invoice.status,
        },
    ).mappings().first()
    return _attach_invoice_context(to_obj(row), db)


def call_create_invoice_for_period(
    db: Session,
    class_id: int,
    period_start: date,
    period_end: date,
) -> TuitionInvoice:
    row = db.execute(
        text(
            """
            EXEC SP_CREATE_INVOICE_FOR_PERIOD
                @class_id = :class_id,
                @period_start = :period_start,
                @period_end = :period_end
            """
        ),
        {
            "class_id": class_id,
            "period_start": period_start,
            "period_end": period_end,
        },
    ).mappings().first()
    return _attach_invoice_context(to_obj(row), db)


def get_invoice_by_class_period(
    db: Session,
    class_id: int,
    period_start: date,
    period_end: date,
) -> Optional[TuitionInvoice]:
    return _attach_invoice_context(
        fetch_one(
            db,
            """
            SELECT *
            FROM VW_INVOICE_DETAIL
            WHERE class_id = :class_id
              AND period_start = :period_start
              AND period_end = :period_end
            """,
            {"class_id": class_id, "period_start": period_start, "period_end": period_end},
        )
    )


def update_invoice(db: Session, invoice_id: int, data: dict) -> None:
    update_by_id(db, "TUITION_INVOICE", "invoice_id", invoice_id, data, INVOICE_UPDATE_COLUMNS)


def cancel_invoice(db: Session, invoice_id: int) -> None:
    update_invoice(db, invoice_id, {"status": "CANCELED"})


def _attach_payment_context(payment):
    if payment is None:
        return None
    payment.invoice = SimpleNamespace(
        invoice_id=payment.invoice_id,
        class_id=getattr(payment, "class_id", None),
        period_start=getattr(payment, "period_start", None),
        period_end=getattr(payment, "period_end", None),
        amount_due=getattr(payment, "amount_due", None),
        amount_paid=getattr(payment, "invoice_amount_paid", None),
        status=getattr(payment, "invoice_status", None),
    )
    return payment


def get_payments(
    db: Session,
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    invoice_status: Optional[str] = None,
    period_filter: Optional[str] = None,
) -> list[TuitionPayment]:
    payments = fetch_all(
        db,
        """
        SELECT
            payment_id,
            invoice_id,
            class_id,
            class_code,
            student_id,
            student_name,
            subject_id,
            subject_name,
            subject_grade_level,
            staff_id,
            staff_name,
            payment_date,
            amount_paid,
            payment_method,
            note,
            payment_status AS status,
            payment_created_at AS created_at,
            payment_updated_at AS updated_at,
            period_start,
            period_end,
            amount_due,
            invoice_amount_paid,
            invoice_status
        FROM VW_PAYMENT_DETAIL
        WHERE (:class_id IS NULL OR class_id = :class_id)
          AND (:student_id IS NULL OR student_id = :student_id)
          AND (:status IS NULL OR payment_status = :status)
          AND (:invoice_status IS NULL OR invoice_status = :invoice_status)
          AND (
              :period_filter IS NULL
              OR CONVERT(VARCHAR(10), period_start, 23) LIKE :period_filter
              OR CONVERT(VARCHAR(10), period_end, 23) LIKE :period_filter
          )
        ORDER BY payment_id DESC
        """,
        {
            "class_id": class_id,
            "student_id": student_id,
            "status": status,
            "invoice_status": invoice_status,
            "period_filter": f"%{period_filter}%" if period_filter else None,
        },
    )
    return [_attach_payment_context(payment) for payment in payments]


def get_payment(db: Session, payment_id: int) -> Optional[TuitionPayment]:
    return _attach_payment_context(
        fetch_one(
            db,
            """
            SELECT
                payment_id,
                invoice_id,
                class_id,
                class_code,
                student_id,
                student_name,
                subject_id,
                subject_name,
                subject_grade_level,
                staff_id,
                staff_name,
                payment_date,
                amount_paid,
                payment_method,
                note,
                payment_status AS status,
                payment_created_at AS created_at,
                payment_updated_at AS updated_at,
                period_start,
                period_end,
                amount_due,
                invoice_amount_paid,
                invoice_status
            FROM VW_PAYMENT_DETAIL
            WHERE payment_id = :payment_id
            """,
            {"payment_id": payment_id},
        )
    )


def create_payment(
    db: Session,
    payment: TuitionPayment,
    class_id: Optional[int] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
) -> TuitionPayment:
    row = db.execute(
        text(
            """
            EXEC SP_CREATE_TUITION_PAYMENT
                @invoice_id = :invoice_id,
                @class_id = :class_id,
                @period_start = :period_start,
                @period_end = :period_end,
                @amount_paid = :amount_paid,
                @payment_method = :payment_method,
                @payment_date = :payment_date,
                @staff_id = :staff_id,
                @note = :note,
                @status = :status
            """
        ),
        {
            "invoice_id": payment.invoice_id,
            "class_id": class_id,
            "period_start": period_start,
            "period_end": period_end,
            "amount_paid": payment.amount_paid,
            "payment_method": payment.payment_method,
            "payment_date": payment.payment_date,
            "staff_id": payment.staff_id,
            "note": payment.note,
            "status": payment.status,
        },
    ).mappings().first()
    return get_payment(db, row["payment_id"]) if row else None


def update_payment(db: Session, payment_id: int, data: dict) -> None:
    update_by_id(db, "TUITION_PAYMENT", "payment_id", payment_id, data, PAYMENT_UPDATE_COLUMNS)


def cancel_payment(db: Session, payment_id: int) -> None:
    update_payment(db, payment_id, {"status": "CANCELED"})

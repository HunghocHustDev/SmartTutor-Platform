from datetime import date
from decimal import Decimal
from hashlib import sha256
from types import SimpleNamespace
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import (
    ClassSchedule,
    LearningRequest,
    LessonSession,
    Staff,
    Student,
    StudyClass,
    Subject,
    TuitionInvoice,
    TuitionPayment,
    Tutor,
    TutorAvailability,
    TutorAssignment,
)
from app.repositories import data_repository as repo


DAY_LABELS = {
    1: "T2",
    2: "T3",
    3: "T4",
    4: "T5",
    5: "T6",
    6: "T7",
    7: "CN",
}

ACTIVE_INACTIVE_STATUSES = {"ACTIVE", "INACTIVE"}
TUTOR_STATUSES = {"ACTIVE", "INACTIVE", "PAUSED"}
TUTOR_AVAILABILITY_STATUSES = {"AVAILABLE", "UNAVAILABLE"}
LEARNING_REQUEST_STATUSES = {"PENDING", "ASSIGNED", "CANCELED"}
ASSIGNMENT_STATUSES = {"ASSIGNED", "CANCELED"}
CLASS_STATUSES = {"ACTIVE", "PAUSED", "COMPLETED", "CANCELED"}
SCHEDULE_STATUSES = {"ACTIVE", "INACTIVE"}
SESSION_STATUSES = {"SCHEDULED", "COMPLETED", "STUDENT_ABSENT", "TUTOR_ABSENT", "CANCELED"}
INVOICE_STATUSES = {"UNPAID", "PARTIALLY_PAID", "PAID", "OVERDUE", "CANCELED"}
PAYMENT_STATUSES = {"SUCCESS", "CANCELED", "REFUNDED"}


def _hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()


def _money(value) -> float:
    if value is None:
        return 0.0
    return float(value)


def _decimal_money(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _format_money(value) -> str:
    return f"{_money(value):,.0f} d"


def _subject_label(subject: Optional[Subject]) -> str:
    if not subject:
        return ""
    if subject.grade_level:
        return f"{subject.subject_name} {subject.grade_level}"
    return subject.subject_name


def _schedule_display(schedules: list[ClassSchedule]) -> Optional[str]:
    if not schedules:
        return None
    parts = []
    for schedule in schedules:
        parts.append(f"{DAY_LABELS.get(schedule.day_of_week, schedule.day_of_week)} - {schedule.start_time.strftime('%H:%M')}")
    return ", ".join(parts)


def _session_attendance(status: str) -> str:
    mapping = {
        "COMPLETED": "CÃ³ máº·t",
        "SCHEDULED": "ChÆ°a diá»…n ra",
        "STUDENT_ABSENT": "Há»c viÃªn váº¯ng",
        "TUTOR_ABSENT": "Gia sÆ° váº¯ng",
        "CANCELED": "ÄÃ£ há»§y",
    }
    return mapping.get(status, status)


def _invoice_status_label(status: str) -> str:
    mapping = {
        "PAID": "ÄÃ£ hoÃ n thÃ nh",
        "UNPAID": "ChÆ°a thanh toÃ¡n",
        "PARTIALLY_PAID": "Thanh toÃ¡n má»™t pháº§n",
        "OVERDUE": "QuÃ¡ háº¡n",
        "CANCELED": "ÄÃ£ há»§y",
    }
    return mapping.get(status, status)


def _payment_status_label(status: str) -> str:
    mapping = {
        "SUCCESS": "ThÃ nh cÃ´ng",
        "CANCELED": "ÄÃ£ há»§y",
        "REFUNDED": "ÄÃ£ hoÃ n tiá»n",
    }
    return mapping.get(status, status)


def _normalize_choice(value: Optional[str], allowed: set[str], field_name: str) -> Optional[str]:
    if value is None:
        return None
    normalized = value.upper()
    if normalized not in allowed:
        allowed_display = ", ".join(sorted(allowed))
        raise HTTPException(status_code=400, detail=f"{field_name} must be one of: {allowed_display}")
    return normalized


def _normalize_mode(mode: Optional[str], allowed: set[str], field_name: str) -> Optional[str]:
    if mode is None:
        return None
    normalized = mode.upper()
    if normalized not in allowed:
        allowed_display = ", ".join(sorted(allowed))
        raise HTTPException(status_code=400, detail=f"{field_name} must be one of: {allowed_display}")
    return normalized


def _normalize_class_status(status: Optional[str]) -> Optional[str]:
    if status is None:
        return None
    normalized = status.upper()
    if normalized == "FINISHED":
        normalized = "COMPLETED"
    return _normalize_choice(normalized, CLASS_STATUSES, "status")


def _normalize_invoice_status(status: Optional[str]) -> Optional[str]:
    if status is None:
        return None
    normalized = status.upper()
    if normalized == "PARTIAL":
        normalized = "PARTIALLY_PAID"
    return _normalize_choice(normalized, INVOICE_STATUSES, "status")


def _normalize_payment_status(status: Optional[str]) -> Optional[str]:
    if status is None:
        return None
    normalized = status.upper()
    if normalized in {"PAID", "PARTIAL", "PARTIALLY_PAID", "SUCCESS"}:
        return "SUCCESS"
    if normalized in {"CANCELED", "REFUNDED"}:
        return normalized
    if normalized == "UNPAID":
        raise HTTPException(status_code=400, detail="UNPAID is an invoice status, not a payment status")
    raise HTTPException(status_code=400, detail=f"Unsupported payment status: {status}")


def _validate_non_negative_decimal(value, field_name: str) -> None:
    if value is not None and _decimal_money(value) < 0:
        raise HTTPException(status_code=400, detail=f"{field_name} must be greater than or equal to zero")


def _validate_positive_decimal(value, field_name: str) -> None:
    if value is not None and _decimal_money(value) <= 0:
        raise HTTPException(status_code=400, detail=f"{field_name} must be greater than zero")


def _validate_non_negative_int(value: Optional[int], field_name: str) -> None:
    if value is not None and value < 0:
        raise HTTPException(status_code=400, detail=f"{field_name} must be greater than or equal to zero")


def _validate_positive_int(value: Optional[int], field_name: str) -> None:
    if value is not None and value <= 0:
        raise HTTPException(status_code=400, detail=f"{field_name} must be greater than zero")


def _validate_date_window(start_value, end_value, start_name: str, end_name: str) -> None:
    if start_value is not None and end_value is not None and end_value < start_value:
        raise HTTPException(status_code=400, detail=f"{end_name} must be on or after {start_name}")


def _validate_schedule_window(day_of_week: Optional[int], start_time, end_time) -> None:
    if day_of_week is not None and not 1 <= day_of_week <= 7:
        raise HTTPException(status_code=400, detail="day_of_week must be between 1 and 7")
    if start_time and end_time and start_time >= end_time:
        raise HTTPException(status_code=400, detail="start_time must be earlier than end_time")


def _validate_session_window(start_time, end_time) -> None:
    if (start_time is None) != (end_time is None):
        raise HTTPException(status_code=400, detail="start_time and end_time must be provided together")
    if start_time and end_time and start_time >= end_time:
        raise HTTPException(status_code=400, detail="start_time must be earlier than end_time")


def _validate_invoice_values(period_start, period_end, completed_sessions: Optional[int], tuition_fee_per_session, amount_due, amount_paid) -> None:
    _validate_date_window(period_start, period_end, "period_start", "period_end")
    _validate_non_negative_int(completed_sessions, "completed_sessions")
    _validate_non_negative_decimal(tuition_fee_per_session, "tuition_fee_per_session")
    _validate_non_negative_decimal(amount_due, "amount_due")
    _validate_non_negative_decimal(amount_paid, "amount_paid")
    if amount_due is not None and amount_paid is not None and _decimal_money(amount_paid) > _decimal_money(amount_due):
        raise HTTPException(status_code=400, detail="amount_paid must be less than or equal to amount_due")


def student_to_response(student: Student) -> dict:
    return {
        "id": student.student_id,
        "full_name": student.full_name,
        "phone": student.phone,
        "email": student.contact_email,
        "area": student.area,
        "level": student.current_level or student.grade_level,
        "status": student.status,
    }


def tutor_subjects_text(tutor: Tutor) -> str:
    labels = [_subject_label(cap.subject) for cap in tutor.capabilities if cap.subject]
    return ", ".join(label for label in labels if label)


def tutor_availability_to_response(availability: TutorAvailability) -> dict:
    return {
        "id": availability.availability_id,
        "tutor_id": availability.tutor_id,
        "day_of_week": availability.day_of_week,
        "start_time": availability.start_time,
        "end_time": availability.end_time,
        "teaching_mode": availability.teaching_mode,
        "area": availability.area,
        "status": availability.status,
    }


def tutor_to_response(tutor: Tutor) -> dict:
    return {
        "id": tutor.tutor_id,
        "full_name": tutor.full_name,
        "phone": tutor.phone,
        "email": tutor.contact_email,
        "area": tutor.area,
        "subjects": tutor_subjects_text(tutor),
        "experience": tutor.experience_years,
        "status": tutor.status,
    }


def subject_to_response(subject: Subject) -> dict:
    return {
        "id": subject.subject_id,
        "name": subject.subject_name,
        "level": subject.grade_level,
        "subject_group": subject.subject_group,
        "description": subject.description,
        "status": subject.status,
    }


def learning_request_to_response(request: LearningRequest) -> dict:
    return {
        "id": request.request_id,
        "student_id": request.student_id,
        "student": request.student.full_name if request.student else None,
        "subject_id": request.subject_id,
        "subject": _subject_label(request.subject),
        "target": request.learning_goal,
        "requested_level": request.requested_level,
        "area": request.preferred_area,
        "preferred_schedule": request.preferred_schedule,
        "expected_fee": _money(request.expected_fee) if request.expected_fee is not None else None,
        "teaching_mode": request.preferred_mode,
        "learning_goal": request.learning_goal,
        "status": request.status,
        "date": request.created_at.date() if request.created_at else None,
    }


def assignment_to_response(assignment: TutorAssignment) -> dict:
    return {
        "id": assignment.assignment_id,
        "request_id": assignment.request_id,
        "tutor_id": assignment.tutor_id,
        "staff_id": assignment.staff_id,
        "status": assignment.status,
        "assigned_at": assignment.assigned_at,
        "note": assignment.note,
    }


def class_to_response(study_class: StudyClass) -> dict:
    if hasattr(study_class, "student_name"):
        subject = study_class.subject_name
        if study_class.subject_grade_level:
            subject = f"{study_class.subject_name} {study_class.subject_grade_level}"
        return {
            "id": study_class.class_id,
            "code": study_class.class_code,
            "assignment_id": study_class.assignment_id,
            "student": study_class.student_name,
            "studentId": study_class.student_id,
            "tutor": study_class.tutor_name,
            "tutorId": study_class.tutor_id,
            "subject": subject,
            "subject_id": study_class.subject_id,
            "level": study_class.subject_grade_level,
            "schedule": getattr(study_class, "schedule_display", None),
            "fee": _money(study_class.tuition_fee_per_session),
            "tuition_fee_per_session": _money(study_class.tuition_fee_per_session),
            "teaching_mode": study_class.teaching_mode,
            "location": study_class.location,
            "status": study_class.class_status,
            "startDate": study_class.start_date,
            "endDate": study_class.end_date,
            "nextLesson": getattr(study_class, "next_lesson", None),
        }

    assignment = study_class.assignment
    request = assignment.learning_request if assignment else None
    student = request.student if request else None
    subject = request.subject if request else None
    tutor = assignment.tutor if assignment else None
    future_sessions = [
        session.lesson_date
        for session in study_class.sessions
        if session.lesson_date and session.lesson_date >= date.today() and session.status == "SCHEDULED"
    ]
    return {
        "id": study_class.class_id,
        "code": study_class.class_code,
        "assignment_id": assignment.assignment_id if assignment else None,
        "student": student.full_name if student else None,
        "studentId": student.student_id if student else None,
        "tutor": tutor.full_name if tutor else None,
        "tutorId": tutor.tutor_id if tutor else None,
        "subject": _subject_label(subject),
        "subject_id": subject.subject_id if subject else None,
        "level": subject.grade_level if subject else None,
        "schedule": _schedule_display(study_class.schedules),
        "fee": _money(study_class.tuition_fee_per_session),
        "tuition_fee_per_session": _money(study_class.tuition_fee_per_session),
        "teaching_mode": study_class.teaching_mode,
        "location": study_class.location,
        "status": study_class.status,
        "startDate": study_class.start_date,
        "endDate": study_class.end_date,
        "nextLesson": min(future_sessions) if future_sessions else None,
    }


def schedule_to_response(schedule: ClassSchedule) -> dict:
    return {
        "id": schedule.schedule_id,
        "class_id": schedule.class_id,
        "day_of_week": schedule.day_of_week,
        "start_time": schedule.start_time,
        "end_time": schedule.end_time,
        "display_text": f"{DAY_LABELS.get(schedule.day_of_week, schedule.day_of_week)} - {schedule.start_time.strftime('%H:%M')}",
        "effective_from": schedule.effective_from,
        "effective_to": schedule.effective_to,
        "status": schedule.status,
        "note": schedule.note,
    }


def session_to_response(session: LessonSession) -> dict:
    class_label = getattr(session, "class_label", None)
    if class_label is None and getattr(session, "study_class", None) and session.study_class.assignment:
        request = session.study_class.assignment.learning_request
        class_label = _subject_label(request.subject) if request else None
    return {
        "id": session.session_id,
        "class_id": session.class_id,
        "schedule_id": session.schedule_id,
        "session_number": session.session_number,
        "date": session.lesson_date,
        "class": class_label,
        "content": session.content_note,
        "attendance": _session_attendance(session.status),
        "status": session.status,
    }


def invoice_to_response(invoice: TuitionInvoice) -> dict:
    return {
        "id": invoice.invoice_id,
        "class_id": invoice.class_id,
        "period_start": invoice.period_start,
        "period_end": invoice.period_end,
        "completed_sessions": invoice.completed_sessions,
        "tuition_fee_per_session": _money(invoice.tuition_fee_per_session),
        "amount_due": _money(invoice.amount_due),
        "amount_paid": _money(invoice.amount_paid),
        "status": invoice.status,
        "created_at": invoice.created_at,
    }


def payment_to_response(payment: TuitionPayment) -> dict:
    invoice = payment.invoice
    subject_name = getattr(payment, "subject_name", None)
    subject_grade_level = getattr(payment, "subject_grade_level", None)
    class_name = None
    if subject_name is not None:
        class_name = _subject_label(SimpleNamespace(subject_name=subject_name, grade_level=subject_grade_level))
    elif invoice and getattr(invoice, "study_class", None):
        assignment = invoice.study_class.assignment
        request = assignment.learning_request if assignment else None
        subject = request.subject if request else None
        class_name = _subject_label(subject) if subject else None
    return {
        "id": payment.payment_id,
        "invoice_id": payment.invoice_id,
        "student_id": getattr(payment, "student_id", None),
        "class_id": invoice.class_id if invoice else None,
        "className": class_name,
        "amount": _format_money(payment.amount_paid),
        "amount_value": _money(payment.amount_paid),
        "period": (
            f"{invoice.period_start.isoformat()} -> {invoice.period_end.isoformat()}"
            if invoice and invoice.period_start and invoice.period_end
            else None
        ),
        "status": _payment_status_label(payment.status),
        "status_code": payment.status,
        "paid_at": payment.payment_date,
        "payment_method": payment.payment_method,
        "invoice_status": _invoice_status_label(invoice.status) if invoice else None,
        "invoice_status_code": invoice.status if invoice else None,
    }


def _invoice_remaining_amount(invoice: TuitionInvoice) -> Decimal:
    amount_due = _decimal_money(invoice.amount_due)
    amount_paid = _decimal_money(invoice.amount_paid)
    remaining = amount_due - amount_paid
    return remaining if remaining > 0 else Decimal("0")


def _invoice_remaining_amount_excluding_payment(invoice: TuitionInvoice, payment: Optional[TuitionPayment] = None) -> Decimal:
    remaining = _invoice_remaining_amount(invoice)
    if payment and payment.status == "SUCCESS":
        remaining += _decimal_money(payment.amount_paid)
    return remaining


def get_student_or_404(db: Session, student_id: int) -> Student:
    student = repo.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


def get_tutor_or_404(db: Session, tutor_id: int) -> Tutor:
    tutor = repo.get_tutor(db, tutor_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return tutor


def get_staff_or_404(db: Session, staff_id: int) -> Staff:
    staff = repo.get_staff(db, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff


def get_subject_or_404(db: Session, subject_id: int) -> Subject:
    subject = repo.get_subject(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


def _ensure_subject(db: Session, subject_id: Optional[int] = None, subject_text: Optional[str] = None) -> Subject:
    if subject_id:
        return get_subject_or_404(db, subject_id)
    if not subject_text:
        raise HTTPException(status_code=400, detail="subject_id or subject is required")
    subject = repo.get_subject_by_name_level(db, subject_text)
    if subject:
        return subject
    return repo.create_subject(db, Subject(subject_name=subject_text, status="ACTIVE"))


def get_learning_request_or_404(db: Session, request_id: int) -> LearningRequest:
    request = repo.get_learning_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Learning request not found")
    return request


def get_assignment_or_404(db: Session, assignment_id: int) -> TutorAssignment:
    assignment = repo.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


def get_class_or_404(db: Session, class_id: int) -> StudyClass:
    study_class = repo.get_class(db, class_id)
    if not study_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return study_class


def get_schedule_or_404(db: Session, schedule_id: int) -> ClassSchedule:
    schedule = repo.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


def get_session_or_404(db: Session, session_id: int) -> LessonSession:
    session = repo.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def get_invoice_or_404(db: Session, invoice_id: int) -> TuitionInvoice:
    invoice = repo.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


def get_payment_or_404(db: Session, payment_id: int) -> TuitionPayment:
    payment = repo.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

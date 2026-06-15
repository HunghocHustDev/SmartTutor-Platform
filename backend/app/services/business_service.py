from datetime import date, datetime
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
    TutorCapability,
    UserAccount,
)
from app.repositories import data_repository as repo
from app.schemas.entities import (
    ClassScheduleCreate,
    ClassScheduleUpdate,
    LearningRequestCreate,
    LearningRequestUpdate,
    LessonSessionCreate,
    LessonSessionStatusUpdate,
    LessonSessionUpdate,
    LoginRequest,
    RegisterRequest,
    StudentCreate,
    StudentUpdate,
    StudyClassCreate,
    StudyClassUpdate,
    SubjectCreate,
    SubjectUpdate,
    TuitionInvoiceCreate,
    TuitionInvoiceUpdate,
    TuitionPaymentCreate,
    TuitionPaymentUpdate,
    TutorAssignmentCreate,
    TutorAssignmentUpdate,
    TutorAvailabilityCreate,
    TutorAvailabilityUpdate,
    TutorCreate,
    TutorSubjectCreate,
    TutorUpdate,
)


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
        "COMPLETED": "Có mặt",
        "SCHEDULED": "Chưa diễn ra",
        "STUDENT_ABSENT": "Học viên vắng",
        "TUTOR_ABSENT": "Gia sư vắng",
        "CANCELED": "Đã hủy",
    }
    return mapping.get(status, status)


def _invoice_status_label(status: str) -> str:
    mapping = {
        "PAID": "Đã hoàn thành",
        "UNPAID": "Chưa thanh toán",
        "PARTIALLY_PAID": "Thanh toán một phần",
        "OVERDUE": "Quá hạn",
        "CANCELED": "Đã hủy",
    }
    return mapping.get(status, status)


def _payment_status_label(status: str) -> str:
    mapping = {
        "SUCCESS": "Thành công",
        "CANCELED": "Đã hủy",
        "REFUNDED": "Đã hoàn tiền",
    }
    return mapping.get(status, status)


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


def _invoice_remaining_amount_excluding_payment(
    invoice: TuitionInvoice,
    payment: Optional[TuitionPayment] = None,
) -> Decimal:
    remaining = _invoice_remaining_amount(invoice)
    if payment and payment.status == "SUCCESS":
        remaining += _decimal_money(payment.amount_paid)
    return remaining


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


def _validate_invoice_values(
    period_start,
    period_end,
    completed_sessions: Optional[int],
    tuition_fee_per_session,
    amount_due,
    amount_paid,
) -> None:
    _validate_date_window(period_start, period_end, "period_start", "period_end")
    _validate_non_negative_int(completed_sessions, "completed_sessions")
    _validate_non_negative_decimal(tuition_fee_per_session, "tuition_fee_per_session")
    _validate_non_negative_decimal(amount_due, "amount_due")
    _validate_non_negative_decimal(amount_paid, "amount_paid")
    if amount_due is not None and amount_paid is not None and _decimal_money(amount_paid) > _decimal_money(amount_due):
        raise HTTPException(status_code=400, detail="amount_paid must be less than or equal to amount_due")


def authenticate(db: Session, payload: LoginRequest) -> dict:
    account = repo.get_user_by_email(db, payload.email)
    if not account or account.password_hash != _hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    normalized_role = "STAFF" if account.role == "ADMIN" else account.role
    role = normalized_role.lower()
    profile_id = account.account_id
    name = account.username
    area = None
    level = None
    university = None
    major = None
    experience = None
    position = None
    if account.role == "STUDENT":
        student = repo.get_student_by_account_id(db, account.account_id)
        if student:
            profile_id = student.student_id
            name = student.full_name
            area = student.area
            level = student.current_level or student.grade_level
    elif account.role == "TUTOR":
        tutor = repo.get_tutor_by_account_id(db, account.account_id)
        if tutor:
            profile_id = tutor.tutor_id
            name = tutor.full_name
            area = tutor.area
            university = tutor.university
            major = tutor.major
            experience = tutor.experience_years
    elif normalized_role == "STAFF":
        staff = repo.get_staff_by_account_id(db, account.account_id)
        if staff:
            profile_id = staff.staff_id
            name = staff.full_name
            area = staff.position
            position = staff.position

    token = f"dev-token-{account.account_id}"
    return {
        "user": {
            "id": profile_id,
            "name": name,
            "role": role,
            "email": account.email,
            "area": area,
            "level": level,
            "university": university,
            "major": major,
            "experience": experience,
            "position": position,
        },
        "token": token,
        "access_token": token,
        "token_type": "bearer",
    }


def register(db: Session, payload: RegisterRequest) -> dict:
    if repo.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Email already exists")

    username = payload.username or payload.email.split("@")[0]
    if repo.get_user_by_username(db, username):
        raise HTTPException(status_code=409, detail="Username already exists")

    full_name = payload.full_name or payload.fullName
    if not full_name:
        raise HTTPException(status_code=400, detail="full_name is required")

    role = payload.role.upper()
    if role not in {"STUDENT", "TUTOR"}:
        raise HTTPException(status_code=400, detail="Public registration only supports STUDENT or TUTOR")

    if role == "STUDENT":
        if not payload.area:
            raise HTTPException(status_code=400, detail="area is required for student registration")
        if not payload.level:
            raise HTTPException(status_code=400, detail="level is required for student registration")
    if role == "TUTOR":
        if not payload.area:
            raise HTTPException(status_code=400, detail="area is required for tutor registration")
        if not payload.university:
            raise HTTPException(status_code=400, detail="university is required for tutor registration")
        if not payload.major:
            raise HTTPException(status_code=400, detail="major is required for tutor registration")
        if payload.experience is not None and payload.experience < 0:
            raise HTTPException(status_code=400, detail="experience must be greater than or equal to zero")

    account = repo.create_user(
        db,
        UserAccount(
            email=payload.email,
            username=username,
            password_hash=_hash_password(payload.password),
            role=role,
            status="ACTIVE",
        ),
    )

    if role == "TUTOR":
        profile = repo.create_tutor(
            db,
            Tutor(
                account_id=account.account_id,
                full_name=full_name,
                phone=payload.phone,
                contact_email=payload.email,
                university=payload.university,
                major=payload.major,
                area=payload.area,
                experience_years=payload.experience or 0,
                status="ACTIVE",
            ),
        )
        profile_id = profile.tutor_id
    else:
        profile = repo.create_student(
            db,
            Student(
                account_id=account.account_id,
                full_name=full_name,
                phone=payload.phone,
                contact_email=payload.email,
                area=payload.area,
                current_level=payload.level,
                grade_level=payload.level,
                status="ACTIVE",
            ),
        )
        profile_id = profile.student_id

    repo.commit(db)
    return {
        "id": profile_id,
        "name": full_name,
        "full_name": full_name,
        "email": payload.email,
        "phone": payload.phone,
        "role": role.lower(),
        "status": "ACTIVE",
        "area": payload.area,
        "level": payload.level,
        "university": payload.university,
        "major": payload.major,
        "experience": payload.experience if role == "TUTOR" else None,
    }


def list_students(db: Session, **filters) -> list[dict]:
    return [student_to_response(item) for item in repo.get_students(db, **filters)]


def create_student(db: Session, payload: StudentCreate) -> dict:
    status = _normalize_choice(payload.status, ACTIVE_INACTIVE_STATUSES, "status")
    student = repo.create_student(
        db,
        Student(
            full_name=payload.full_name,
            phone=payload.phone,
            contact_email=payload.email,
            area=payload.area,
            current_level=payload.level,
            grade_level=payload.level,
            status=status,
        ),
    )
    repo.commit(db)
    return student_to_response(student)


def get_student_or_404(db: Session, student_id: int) -> Student:
    student = repo.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


def update_student(db: Session, student_id: int, payload: StudentUpdate) -> dict:
    student = get_student_or_404(db, student_id)
    data = payload.model_dump(exclude_unset=True)
    if "status" in data:
        data["status"] = _normalize_choice(data["status"], ACTIVE_INACTIVE_STATUSES, "status")
    if "level" in data:
        level = data.pop("level")
        data["current_level"] = level
        data["grade_level"] = level
    if "email" in data:
        data["contact_email"] = data.pop("email")
    repo.update_student(db, student_id, data)
    repo.commit(db)
    return student_to_response(repo.get_student(db, student_id))


def deactivate_student(db: Session, student_id: int) -> dict:
    get_student_or_404(db, student_id)
    repo.deactivate_student(db, student_id)
    repo.commit(db)
    return {"detail": "Student deactivated"}


def _ensure_subject(db: Session, subject_id: Optional[int] = None, subject_text: Optional[str] = None) -> Subject:
    if subject_id:
        subject = repo.get_subject(db, subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        return subject
    if not subject_text:
        raise HTTPException(status_code=400, detail="subject_id or subject is required")
    subject = repo.get_subject_by_name_level(db, subject_text)
    if subject:
        return subject
    return repo.create_subject(db, Subject(subject_name=subject_text, status="ACTIVE"))


def list_tutors(db: Session, **filters) -> list[dict]:
    return [tutor_to_response(item) for item in repo.get_tutors(db, **filters)]


def create_tutor(db: Session, payload: TutorCreate) -> dict:
    _validate_non_negative_int(payload.experience, "experience")
    status = _normalize_choice(payload.status, TUTOR_STATUSES, "status")
    tutor = repo.create_tutor(
        db,
        Tutor(
            full_name=payload.full_name,
            phone=payload.phone,
            contact_email=payload.email,
            area=payload.area,
            experience_years=payload.experience,
            status=status,
        ),
    )
    for subject_name in [part.strip() for part in (payload.subjects or "").split(",") if part.strip()]:
        subject = _ensure_subject(db, subject_text=subject_name)
        repo.create_tutor_capability(
            db,
            TutorCapability(
                tutor_id=tutor.tutor_id,
                subject_id=subject.subject_id,
                years_experience=payload.experience,
            ),
        )
    repo.commit(db)
    return tutor_to_response(repo.get_tutor(db, tutor.tutor_id))


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


def update_tutor(db: Session, tutor_id: int, payload: TutorUpdate) -> dict:
    tutor = get_tutor_or_404(db, tutor_id)
    data = payload.model_dump(exclude_unset=True)
    subjects = data.pop("subjects", None)
    if "status" in data:
        data["status"] = _normalize_choice(data["status"], TUTOR_STATUSES, "status")
    if "experience" in data:
        _validate_non_negative_int(data["experience"], "experience")
        data["experience_years"] = data.pop("experience")
    if "email" in data:
        data["contact_email"] = data.pop("email")
    next_experience = data.get("experience_years", tutor.experience_years)
    repo.update_tutor(db, tutor_id, data)
    if subjects is not None:
        repo.delete_tutor_capabilities(db, tutor_id)
        for subject_name in [part.strip() for part in subjects.split(",") if part.strip()]:
            subject = _ensure_subject(db, subject_text=subject_name)
            repo.create_tutor_capability(
                db,
                TutorCapability(
                    tutor_id=tutor_id,
                    subject_id=subject.subject_id,
                    years_experience=next_experience,
                ),
            )
        repo.touch_tutor(db, tutor_id)
    repo.commit(db)
    return tutor_to_response(repo.get_tutor(db, tutor_id))


def deactivate_tutor(db: Session, tutor_id: int) -> dict:
    get_tutor_or_404(db, tutor_id)
    repo.deactivate_tutor(db, tutor_id)
    repo.commit(db)
    return {"detail": "Tutor deactivated"}


def list_subjects(db: Session, status: Optional[str] = None) -> list[dict]:
    return [subject_to_response(item) for item in repo.get_subjects(db, status=status)]


def create_subject(db: Session, payload: SubjectCreate) -> dict:
    status = _normalize_choice(payload.status, ACTIVE_INACTIVE_STATUSES, "status")
    if repo.get_subject_by_name_level(db, payload.name, payload.level):
        raise HTTPException(status_code=409, detail="Subject already exists for this level")
    subject = repo.create_subject(
        db,
        Subject(
            subject_name=payload.name,
            subject_group=payload.subject_group,
            grade_level=payload.level,
            description=payload.description,
            status=status,
        ),
    )
    repo.commit(db)
    return subject_to_response(subject)


def get_subject_or_404(db: Session, subject_id: int) -> Subject:
    subject = repo.get_subject(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


def update_subject(db: Session, subject_id: int, payload: SubjectUpdate) -> dict:
    subject = get_subject_or_404(db, subject_id)
    data = payload.model_dump(exclude_unset=True)
    if "status" in data:
        data["status"] = _normalize_choice(data["status"], ACTIVE_INACTIVE_STATUSES, "status")
    next_name = data.get("name", subject.subject_name)
    next_level = data.get("level", subject.grade_level)
    duplicate = repo.get_subject_by_name_level(db, next_name, next_level)
    if duplicate and duplicate.subject_id != subject_id:
        raise HTTPException(status_code=409, detail="Subject already exists for this level")
    if "name" in data:
        data["subject_name"] = data.pop("name")
    if "level" in data:
        data["grade_level"] = data.pop("level")
    repo.update_subject(db, subject_id, data)
    repo.commit(db)
    return subject_to_response(repo.get_subject(db, subject_id))


def deactivate_subject(db: Session, subject_id: int) -> dict:
    get_subject_or_404(db, subject_id)
    repo.deactivate_subject(db, subject_id)
    repo.commit(db)
    return {"detail": "Subject deactivated"}


def list_tutor_subjects(db: Session, tutor_id: int) -> list[dict]:
    tutor = get_tutor_or_404(db, tutor_id)
    return [
        {
            "capability_id": cap.capability_id,
            "subject_id": cap.subject_id,
            "name": cap.subject.subject_name,
            "level": cap.subject.grade_level,
            "teaching_level": cap.teaching_level,
            "years_experience": cap.years_experience,
        }
        for cap in tutor.capabilities
        if cap.subject
    ]


def add_tutor_subject(db: Session, tutor_id: int, payload: TutorSubjectCreate) -> dict:
    get_tutor_or_404(db, tutor_id)
    subject = get_subject_or_404(db, payload.subject_id)
    _validate_non_negative_int(payload.years_experience, "years_experience")
    existing = repo.get_tutor_capability(db, tutor_id, payload.subject_id)
    capability = existing
    if existing:
        repo.update_tutor_capability(
            db,
            existing.capability_id,
            {
                "years_experience": payload.years_experience,
                "note": payload.note,
                "teaching_level": payload.teaching_level,
            },
        )
        capability = repo.get_tutor_capability_by_id(db, tutor_id, existing.capability_id)
    else:
        capability = repo.create_tutor_capability(
            db,
            TutorCapability(
                tutor_id=tutor_id,
                subject_id=payload.subject_id,
                teaching_level=payload.teaching_level,
                years_experience=payload.years_experience,
                note=payload.note,
            ),
        )
    repo.commit(db)
    return {
        "capability_id": capability.capability_id if capability else None,
        "subject_id": subject.subject_id,
        "name": subject.subject_name,
        "level": subject.grade_level,
        "teaching_level": payload.teaching_level,
        "years_experience": payload.years_experience,
    }


def remove_tutor_subject(db: Session, tutor_id: int, subject_id: int) -> dict:
    capability = repo.get_tutor_capability(db, tutor_id, subject_id)
    if not capability:
        raise HTTPException(status_code=404, detail="Tutor subject not found")
    repo.delete_tutor_capability(db, capability)
    repo.commit(db)
    return {"detail": "Tutor subject removed"}


def remove_tutor_capability(db: Session, tutor_id: int, capability_id: int) -> dict:
    capability = repo.get_tutor_capability_by_id(db, tutor_id, capability_id)
    if not capability:
        raise HTTPException(status_code=404, detail="Tutor capability not found")
    repo.delete_tutor_capability(db, capability)
    repo.commit(db)
    return {"detail": "Tutor capability removed"}


def list_tutor_availabilities(db: Session, tutor_id: int) -> list[dict]:
    get_tutor_or_404(db, tutor_id)
    return [tutor_availability_to_response(item) for item in repo.get_tutor_availabilities(db, tutor_id)]


def get_tutor_availability_or_404(db: Session, tutor_id: int, availability_id: int) -> TutorAvailability:
    availability = repo.get_tutor_availability(db, tutor_id, availability_id)
    if not availability:
        raise HTTPException(status_code=404, detail="Tutor availability not found")
    return availability


def create_tutor_availability(db: Session, tutor_id: int, payload: TutorAvailabilityCreate) -> dict:
    get_tutor_or_404(db, tutor_id)
    _validate_schedule_window(payload.day_of_week, payload.start_time, payload.end_time)
    availability = repo.create_tutor_availability(
        db,
        TutorAvailability(
            tutor_id=tutor_id,
            day_of_week=payload.day_of_week,
            start_time=payload.start_time,
            end_time=payload.end_time,
            teaching_mode=_normalize_mode(payload.teaching_mode, {"ONLINE", "OFFLINE", "BOTH"}, "teaching_mode"),
            area=payload.area,
            status=_normalize_choice(payload.status, TUTOR_AVAILABILITY_STATUSES, "status"),
        ),
    )
    repo.commit(db)
    return tutor_availability_to_response(availability)


def update_tutor_availability(db: Session, tutor_id: int, availability_id: int, payload: TutorAvailabilityUpdate) -> dict:
    availability = get_tutor_availability_or_404(db, tutor_id, availability_id)
    data = payload.model_dump(exclude_unset=True)
    _validate_schedule_window(
        data.get("day_of_week", availability.day_of_week),
        data.get("start_time", availability.start_time),
        data.get("end_time", availability.end_time),
    )
    if "teaching_mode" in data:
        data["teaching_mode"] = _normalize_mode(data["teaching_mode"], {"ONLINE", "OFFLINE", "BOTH"}, "teaching_mode")
    if "status" in data:
        data["status"] = _normalize_choice(data["status"], TUTOR_AVAILABILITY_STATUSES, "status")
    repo.update_tutor_availability(db, availability_id, data)
    repo.commit(db)
    return tutor_availability_to_response(repo.get_tutor_availability(db, tutor_id, availability_id))


def delete_tutor_availability(db: Session, tutor_id: int, availability_id: int) -> dict:
    get_tutor_availability_or_404(db, tutor_id, availability_id)
    repo.delete_tutor_availability(db, availability_id)
    repo.commit(db)
    return {"detail": "Tutor availability deleted"}


def list_learning_requests(db: Session, **filters) -> list[dict]:
    return [learning_request_to_response(item) for item in repo.get_learning_requests(db, **filters)]


def create_learning_request(db: Session, payload: LearningRequestCreate) -> dict:
    get_student_or_404(db, payload.student_id)
    subject = _ensure_subject(db, payload.subject_id, payload.subject)
    _validate_non_negative_decimal(payload.expected_fee, "expected_fee")
    request = repo.create_learning_request(
        db,
        LearningRequest(
            student_id=payload.student_id,
            subject_id=subject.subject_id,
            requested_level=payload.requested_level,
            learning_goal=payload.learning_goal or payload.target,
            preferred_area=payload.area,
            preferred_schedule=payload.preferred_schedule,
            expected_fee=payload.expected_fee,
            preferred_mode=_normalize_mode(payload.teaching_mode, {"ONLINE", "OFFLINE", "BOTH"}, "teaching_mode"),
            status="PENDING",
        ),
    )
    repo.commit(db)
    return learning_request_to_response(repo.get_learning_request(db, request.request_id))


def get_learning_request_or_404(db: Session, request_id: int) -> LearningRequest:
    request = repo.get_learning_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Learning request not found")
    return request


def update_learning_request(db: Session, request_id: int, payload: LearningRequestUpdate) -> dict:
    request = get_learning_request_or_404(db, request_id)
    data = payload.model_dump(exclude_unset=True)
    if "expected_fee" in data:
        _validate_non_negative_decimal(data["expected_fee"], "expected_fee")
    if "status" in data:
        data["status"] = _normalize_choice(data["status"], LEARNING_REQUEST_STATUSES, "status")
    subject_text = data.pop("subject", None)
    if data.get("subject_id") or subject_text:
        subject = _ensure_subject(db, data.pop("subject_id", None), subject_text)
        data["subject_id"] = subject.subject_id
    if "target" in data and "learning_goal" not in data:
        data["learning_goal"] = data.pop("target")
    if "area" in data and "preferred_area" not in data:
        data["preferred_area"] = data.pop("area")
    if "teaching_mode" in data and "preferred_mode" not in data:
        data["preferred_mode"] = data.pop("teaching_mode")
    if "preferred_mode" in data:
        data["preferred_mode"] = _normalize_mode(data["preferred_mode"], {"ONLINE", "OFFLINE", "BOTH"}, "teaching_mode")
    repo.update_learning_request(db, request_id, data)
    repo.commit(db)
    return learning_request_to_response(repo.get_learning_request(db, request_id))


def cancel_learning_request(db: Session, request_id: int) -> dict:
    get_learning_request_or_404(db, request_id)
    repo.cancel_learning_request(db, request_id)
    repo.commit(db)
    return {"detail": "Learning request canceled"}


def create_assignment(db: Session, payload: TutorAssignmentCreate) -> dict:
    request = get_learning_request_or_404(db, payload.request_id)
    tutor = get_tutor_or_404(db, payload.tutor_id)
    if payload.staff_id is not None:
        get_staff_or_404(db, payload.staff_id)
    if request.status != "PENDING":
        raise HTTPException(status_code=409, detail="Learning request is not pending")
    if tutor.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Tutor must be ACTIVE to receive an assignment")
    active_assignments = repo.get_assignments(db, request_id=payload.request_id, status="ASSIGNED")
    if active_assignments:
        raise HTTPException(status_code=409, detail="Learning request already has an active assignment")
    capabilities = [cap.subject_id for cap in tutor.capabilities]
    if capabilities and request.subject_id not in capabilities:
        raise HTTPException(status_code=400, detail="Tutor does not have capability for requested subject")
    assignment = repo.call_assign_tutor_to_request(
        db,
        request_id=payload.request_id,
        tutor_id=payload.tutor_id,
        staff_id=payload.staff_id,
        note=payload.note,
    )
    repo.commit(db)
    return assignment_to_response(assignment)


def list_assignments(db: Session, **filters) -> list[dict]:
    return [assignment_to_response(item) for item in repo.get_assignments(db, **filters)]


def get_assignment_or_404(db: Session, assignment_id: int) -> TutorAssignment:
    assignment = repo.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


def update_assignment(db: Session, assignment_id: int, payload: TutorAssignmentUpdate) -> dict:
    assignment = get_assignment_or_404(db, assignment_id)
    data = payload.model_dump(exclude_unset=True)
    if "status" in data:
        data["status"] = _normalize_choice(data["status"], ASSIGNMENT_STATUSES, "status")
    if "staff_id" in data and data["staff_id"] is not None:
        get_staff_or_404(db, data["staff_id"])
    if "tutor_id" in data:
        tutor = get_tutor_or_404(db, data["tutor_id"])
        request = get_learning_request_or_404(db, assignment.request_id)
        if tutor.status != "ACTIVE":
            raise HTTPException(status_code=400, detail="Tutor must be ACTIVE to receive an assignment")
        capabilities = [cap.subject_id for cap in tutor.capabilities]
        if capabilities and request.subject_id not in capabilities:
            raise HTTPException(status_code=400, detail="Tutor does not have capability for requested subject")
    if data.get("status") == "CANCELED":
        get_learning_request_or_404(db, assignment.request_id)
        repo.update_learning_request(db, assignment.request_id, {"status": "PENDING"})
    repo.update_assignment(db, assignment_id, data)
    repo.commit(db)
    return assignment_to_response(repo.get_assignment(db, assignment_id))


def cancel_assignment(db: Session, assignment_id: int) -> dict:
    assignment = get_assignment_or_404(db, assignment_id)
    if assignment.study_class:
        raise HTTPException(status_code=409, detail="Cannot cancel an assignment that already has a class")
    get_learning_request_or_404(db, assignment.request_id)
    repo.cancel_assignment(db, assignment_id)
    repo.update_learning_request(db, assignment.request_id, {"status": "PENDING"})
    repo.commit(db)
    return {"detail": "Assignment canceled"}


def list_classes(db: Session, **filters) -> list[dict]:
    if "status" in filters:
        filters["status"] = _normalize_class_status(filters["status"])
    return [class_to_response(item) for item in repo.get_classes(db, **filters)]


def create_study_class(db: Session, payload: StudyClassCreate) -> dict:
    if not payload.assignment_id:
        raise HTTPException(status_code=400, detail="assignment_id is required")
    _validate_non_negative_decimal(payload.tuition_fee_per_session, "tuition_fee_per_session")
    _validate_date_window(payload.start_date, payload.end_date, "start_date", "end_date")
    assignment = get_assignment_or_404(db, payload.assignment_id)
    if assignment.status != "ASSIGNED":
        raise HTTPException(status_code=400, detail="Assignment must be ASSIGNED to create a class")
    if assignment.study_class:
        raise HTTPException(status_code=409, detail="Assignment already has a class")

    study_class = repo.create_class(
        db,
        StudyClass(
            assignment_id=assignment.assignment_id,
            class_code=payload.class_code or f"CLS-{assignment.assignment_id:04d}",
            tuition_fee_per_session=payload.tuition_fee_per_session,
            teaching_mode=_normalize_mode(payload.teaching_mode, {"ONLINE", "OFFLINE"}, "teaching_mode"),
            location=payload.location,
            start_date=payload.start_date,
            end_date=payload.end_date,
            status=_normalize_class_status(payload.status) or "ACTIVE",
        ),
    )
    repo.commit(db)
    return class_to_response(repo.get_class(db, study_class.class_id))


def get_class_or_404(db: Session, class_id: int) -> StudyClass:
    study_class = repo.get_class(db, class_id)
    if not study_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return study_class


def update_study_class(db: Session, class_id: int, payload: StudyClassUpdate) -> dict:
    study_class = get_class_or_404(db, class_id)
    data = payload.model_dump(exclude_unset=True)
    if "tuition_fee_per_session" in data:
        _validate_non_negative_decimal(data["tuition_fee_per_session"], "tuition_fee_per_session")
    _validate_date_window(
        data.get("start_date", study_class.start_date),
        data.get("end_date", study_class.end_date),
        "start_date",
        "end_date",
    )
    if "status" in data:
        data["status"] = _normalize_class_status(data["status"])
    if "teaching_mode" in data:
        data["teaching_mode"] = _normalize_mode(data["teaching_mode"], {"ONLINE", "OFFLINE"}, "teaching_mode")
    repo.update_class(db, class_id, data)
    repo.commit(db)
    return class_to_response(repo.get_class(db, class_id))


def cancel_study_class(db: Session, class_id: int) -> dict:
    get_class_or_404(db, class_id)
    repo.cancel_class(db, class_id)
    repo.commit(db)
    return {"detail": "Class canceled"}


def list_schedules(db: Session, **filters) -> list[dict]:
    return [schedule_to_response(item) for item in repo.get_schedules(db, **filters)]


def create_schedule(db: Session, payload: ClassScheduleCreate) -> dict:
    get_class_or_404(db, payload.class_id)
    _validate_schedule_window(payload.day_of_week, payload.start_time, payload.end_time)
    _validate_date_window(payload.effective_from, payload.effective_to, "effective_from", "effective_to")
    data = payload.model_dump()
    data["status"] = _normalize_choice(data["status"], SCHEDULE_STATUSES, "status")
    schedule = repo.create_schedule(db, ClassSchedule(**data))
    repo.commit(db)
    return schedule_to_response(schedule)


def get_schedule_or_404(db: Session, schedule_id: int) -> ClassSchedule:
    schedule = repo.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


def update_schedule(db: Session, schedule_id: int, payload: ClassScheduleUpdate) -> dict:
    schedule = get_schedule_or_404(db, schedule_id)
    _validate_schedule_window(
        payload.day_of_week if payload.day_of_week is not None else schedule.day_of_week,
        payload.start_time if payload.start_time is not None else schedule.start_time,
        payload.end_time if payload.end_time is not None else schedule.end_time,
    )
    _validate_date_window(
        payload.effective_from if payload.effective_from is not None else schedule.effective_from,
        payload.effective_to if payload.effective_to is not None else schedule.effective_to,
        "effective_from",
        "effective_to",
    )
    data = payload.model_dump(exclude_unset=True)
    if "status" in data:
        data["status"] = _normalize_choice(data["status"], SCHEDULE_STATUSES, "status")
    repo.update_schedule(db, schedule_id, data)
    repo.commit(db)
    return schedule_to_response(repo.get_schedule(db, schedule_id))


def delete_schedule(db: Session, schedule_id: int) -> dict:
    get_schedule_or_404(db, schedule_id)
    repo.deactivate_schedule(db, schedule_id)
    repo.commit(db)
    return {"detail": "Schedule deactivated"}


def list_sessions(db: Session, session_date: Optional[date] = None, **filters) -> list[dict]:
    return [session_to_response(item) for item in repo.get_sessions(db, lesson_date=session_date, **filters)]


def create_session(db: Session, payload: LessonSessionCreate) -> dict:
    get_class_or_404(db, payload.class_id)
    if payload.schedule_id is not None:
        schedule = get_schedule_or_404(db, payload.schedule_id)
        if schedule.class_id != payload.class_id:
            raise HTTPException(status_code=400, detail="schedule_id must belong to class_id")
    _validate_positive_int(payload.session_number, "session_number")
    _validate_session_window(payload.start_time, payload.end_time)
    data = payload.model_dump()
    data["status"] = _normalize_choice(data["status"], SESSION_STATUSES, "status")
    session = repo.create_session(db, LessonSession(**data))
    repo.commit(db)
    return session_to_response(repo.get_session(db, session.session_id))


def get_session_or_404(db: Session, session_id: int) -> LessonSession:
    session = repo.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def update_session(db: Session, session_id: int, payload: LessonSessionUpdate) -> dict:
    session = get_session_or_404(db, session_id)
    data = payload.model_dump(exclude_unset=True)
    if "schedule_id" in data and data["schedule_id"] is not None:
        schedule = get_schedule_or_404(db, data["schedule_id"])
        if schedule.class_id != session.class_id:
            raise HTTPException(status_code=400, detail="schedule_id must belong to the session class")
    if "session_number" in data:
        _validate_positive_int(data["session_number"], "session_number")
    _validate_session_window(
        data.get("start_time", session.start_time),
        data.get("end_time", session.end_time),
    )
    if "status" in data:
        data["status"] = _normalize_choice(data["status"], SESSION_STATUSES, "status")
    repo.update_session(db, session_id, data)
    repo.commit(db)
    return session_to_response(repo.get_session(db, session_id))


def update_session_status(db: Session, session_id: int, payload: LessonSessionStatusUpdate) -> dict:
    get_session_or_404(db, session_id)
    data = {"status": _normalize_choice(payload.status, SESSION_STATUSES, "status")}
    if "content_note" in payload.model_fields_set:
        data["content_note"] = payload.content_note
    repo.update_session(db, session_id, data)
    repo.commit(db)
    return session_to_response(repo.get_session(db, session_id))


def delete_session(db: Session, session_id: int) -> dict:
    get_session_or_404(db, session_id)
    repo.cancel_session(db, session_id)
    repo.commit(db)
    return {"detail": "Session canceled"}


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
    data = payload.model_dump()
    data["status"] = _normalize_invoice_status(data["status"])
    invoice = repo.create_invoice(db, TuitionInvoice(**data))
    repo.commit(db)
    return invoice_to_response(repo.get_invoice(db, invoice.invoice_id))


def get_invoice_or_404(db: Session, invoice_id: int) -> TuitionInvoice:
    invoice = repo.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


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
    return [
        payment_to_response(item)
        for item in repo.get_payments(db, status=payment_status, invoice_status=invoice_status, **filters)
    ]


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
    if not invoice:
        if payload.class_id is None:
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


def get_payment_or_404(db: Session, payment_id: int) -> TuitionPayment:
    payment = repo.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


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


def tuition_summary(db: Session, class_id: int) -> dict:
    get_class_or_404(db, class_id)
    summary = repo.get_class_tuition_summary(db, class_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Class not found")
    return {
        "class_id": class_id,
        "completed_sessions": summary.completed_sessions,
        "tuition_fee_per_session": _money(summary.tuition_fee_per_session),
        "total_fee": _money(summary.total_fee),
        "paid_amount": _money(summary.paid_amount),
        "remaining_amount": max(_money(summary.remaining_amount), 0.0),
    }


def dashboard_summary(db: Session) -> dict:
    summary = repo.get_dashboard_summary(db)
    return {
        "total_students": summary.total_students,
        "total_tutors": summary.total_tutors,
        "pending_learning_requests": summary.pending_learning_requests,
        "active_classes": summary.active_classes,
        "completed_sessions": summary.completed_sessions,
        "unpaid_invoices": summary.unpaid_invoices,
        "partially_paid_invoices": summary.partially_paid_invoices,
        "successful_payments": summary.successful_payments,
    }

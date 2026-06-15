from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LearningRequest, LessonSession, StudyClass, TuitionInvoice, TuitionPayment, TutorAssignment
from app.repositories import data_repository as repo
from app.services import business_service as service


@dataclass
class CurrentActor:
    account_id: int
    role: str
    student_id: Optional[int] = None
    tutor_id: Optional[int] = None
    staff_id: Optional[int] = None
    email: Optional[str] = None


def _forbidden(message: str = "You do not have permission to perform this action") -> None:
    raise HTTPException(status_code=403, detail=message)


def _normalize_role(role: str) -> str:
    return "staff" if role == "ADMIN" else role.lower()


def get_current_actor(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> CurrentActor:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")

    token = authorization.split(" ", 1)[1].strip()
    if not token.startswith("dev-token-"):
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    try:
        account_id = int(token.removeprefix("dev-token-"))
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token") from exc

    account = repo.get_user_by_id(db, account_id)
    if not account or account.status != "ACTIVE":
        raise HTTPException(status_code=401, detail="Account is not active")

    actor = CurrentActor(
        account_id=account.account_id,
        role=_normalize_role(account.role),
        email=account.email,
    )

    if account.role == "STUDENT":
        student = repo.get_student_by_account_id(db, account.account_id)
        actor.student_id = student.student_id if student else None
    elif account.role == "TUTOR":
        tutor = repo.get_tutor_by_account_id(db, account.account_id)
        actor.tutor_id = tutor.tutor_id if tutor else None
    else:
        staff = repo.get_staff_by_account_id(db, account.account_id)
        actor.staff_id = staff.staff_id if staff else None

    return actor


def require_roles(*roles: str):
    allowed = {role.lower() for role in roles}

    def dependency(actor: CurrentActor = Depends(get_current_actor)) -> CurrentActor:
        if actor.role not in allowed:
            _forbidden()
        return actor

    return dependency


def ensure_student_scope(actor: CurrentActor, student_id: Optional[int] = None) -> int:
    if actor.role == "staff":
        return student_id if student_id is not None else 0
    if actor.role != "student" or actor.student_id is None:
        _forbidden()
    if student_id is not None and student_id != actor.student_id:
        _forbidden("Students can only access their own data")
    return actor.student_id


def ensure_tutor_scope(actor: CurrentActor, tutor_id: Optional[int] = None) -> int:
    if actor.role == "staff":
        return tutor_id if tutor_id is not None else 0
    if actor.role != "tutor" or actor.tutor_id is None:
        _forbidden()
    if tutor_id is not None and tutor_id != actor.tutor_id:
        _forbidden("Tutors can only access their own data")
    return actor.tutor_id


def ensure_learning_request_access(actor: CurrentActor, request: LearningRequest) -> None:
    if actor.role == "staff":
        return
    if actor.role == "student" and actor.student_id == request.student_id:
        return
    _forbidden("You cannot access this learning request")


def ensure_assignment_access(actor: CurrentActor, assignment: TutorAssignment) -> None:
    if actor.role == "staff":
        return
    if actor.role == "tutor" and actor.tutor_id == assignment.tutor_id:
        return
    _forbidden("You cannot access this assignment")


def ensure_class_access(actor: CurrentActor, study_class: StudyClass) -> None:
    if actor.role == "staff":
        return
    if hasattr(study_class, "student_id") or hasattr(study_class, "tutor_id"):
        if actor.role == "student" and actor.student_id == getattr(study_class, "student_id", None):
            return
        if actor.role == "tutor" and actor.tutor_id == getattr(study_class, "tutor_id", None):
            return
    assignment = study_class.assignment
    learning_request = assignment.learning_request if assignment else None
    if actor.role == "student" and learning_request and actor.student_id == learning_request.student_id:
        return
    if actor.role == "tutor" and assignment and actor.tutor_id == assignment.tutor_id:
        return
    _forbidden("You cannot access this class")


def ensure_schedule_access(db: Session, actor: CurrentActor, schedule) -> None:
    study_class = service.get_class_or_404(db, schedule.class_id)
    ensure_class_access(actor, study_class)


def ensure_session_access(db: Session, actor: CurrentActor, session: LessonSession) -> None:
    study_class = service.get_class_or_404(db, session.class_id)
    ensure_class_access(actor, study_class)


def ensure_invoice_access(db: Session, actor: CurrentActor, invoice: TuitionInvoice) -> None:
    study_class = service.get_class_or_404(db, invoice.class_id)
    ensure_class_access(actor, study_class)


def ensure_payment_access(db: Session, actor: CurrentActor, payment: TuitionPayment) -> None:
    if not payment.invoice:
        _forbidden("Payment invoice is missing")
    ensure_invoice_access(db, actor, payment.invoice)

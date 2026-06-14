from datetime import date, datetime
from typing import Iterable, Optional

from sqlalchemy import String, cast, or_
from sqlalchemy.orm import Session, joinedload

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


def touch_model(model):
    if hasattr(model, "updated_at"):
        model.updated_at = datetime.utcnow()
    return model


def apply_updates(model, data: dict):
    changed = False
    for key, value in data.items():
        if key == "updated_at":
            continue
        if hasattr(model, key):
            setattr(model, key, value)
            changed = True
    if changed:
        touch_model(model)
    return model


def get_user_by_email(db: Session, email: str) -> Optional[UserAccount]:
    return db.query(UserAccount).filter(UserAccount.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[UserAccount]:
    return db.query(UserAccount).filter(UserAccount.username == username).first()


def create_user(db: Session, user: UserAccount) -> UserAccount:
    db.add(user)
    db.flush()
    return user


def get_staff(db: Session, staff_id: int) -> Optional[Staff]:
    return db.query(Staff).filter(Staff.staff_id == staff_id).first()


def create_staff(db: Session, staff: Staff) -> Staff:
    db.add(staff)
    db.flush()
    return staff


def get_students(
    db: Session,
    search: Optional[str] = None,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    area: Optional[str] = None,
    status: Optional[str] = None,
) -> list[Student]:
    query = db.query(Student)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Student.full_name.ilike(pattern),
                Student.phone.ilike(pattern),
                Student.contact_email.ilike(pattern),
                Student.area.ilike(pattern),
            )
        )
    if name:
        query = query.filter(Student.full_name.ilike(f"%{name}%"))
    if phone:
        query = query.filter(Student.phone.ilike(f"%{phone}%"))
    if email:
        query = query.filter(Student.contact_email.ilike(f"%{email}%"))
    if area:
        query = query.filter(Student.area.ilike(f"%{area}%"))
    if status:
        query = query.filter(Student.status == status)
    return query.order_by(Student.student_id.desc()).all()


def get_student(db: Session, student_id: int) -> Optional[Student]:
    return db.query(Student).filter(Student.student_id == student_id).first()


def create_student(db: Session, student: Student) -> Student:
    db.add(student)
    db.flush()
    return student


def get_tutors(
    db: Session,
    search: Optional[str] = None,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    area: Optional[str] = None,
    subject: Optional[str] = None,
    status: Optional[str] = None,
) -> list[Tutor]:
    query = db.query(Tutor).options(joinedload(Tutor.capabilities).joinedload(TutorCapability.subject))
    if search:
        pattern = f"%{search}%"
        query = query.outerjoin(TutorCapability).outerjoin(Subject).filter(
            or_(
                Tutor.full_name.ilike(pattern),
                Tutor.phone.ilike(pattern),
                Tutor.contact_email.ilike(pattern),
                Tutor.area.ilike(pattern),
                Subject.subject_name.ilike(pattern),
            )
        )
    if name:
        query = query.filter(Tutor.full_name.ilike(f"%{name}%"))
    if phone:
        query = query.filter(Tutor.phone.ilike(f"%{phone}%"))
    if email:
        query = query.filter(Tutor.contact_email.ilike(f"%{email}%"))
    if area:
        query = query.filter(Tutor.area.ilike(f"%{area}%"))
    if subject:
        query = query.join(TutorCapability).join(Subject).filter(Subject.subject_name.ilike(f"%{subject}%"))
    if status:
        query = query.filter(Tutor.status == status)
    return query.order_by(Tutor.tutor_id.desc()).distinct().all()


def get_tutor(db: Session, tutor_id: int) -> Optional[Tutor]:
    return (
        db.query(Tutor)
        .options(joinedload(Tutor.capabilities).joinedload(TutorCapability.subject))
        .filter(Tutor.tutor_id == tutor_id)
        .first()
    )


def create_tutor(db: Session, tutor: Tutor) -> Tutor:
    db.add(tutor)
    db.flush()
    return tutor


def get_subjects(db: Session, status: Optional[str] = None) -> list[Subject]:
    query = db.query(Subject)
    if status:
        query = query.filter(Subject.status == status)
    return query.order_by(Subject.subject_name.asc(), Subject.grade_level.asc()).all()


def get_subject(db: Session, subject_id: int) -> Optional[Subject]:
    return db.query(Subject).filter(Subject.subject_id == subject_id).first()


def get_subject_by_name_level(db: Session, name: str, level: Optional[str] = None) -> Optional[Subject]:
    query = db.query(Subject).filter(Subject.subject_name == name)
    if level is None:
        query = query.filter(Subject.grade_level.is_(None))
    else:
        query = query.filter(Subject.grade_level == level)
    return query.first()


def create_subject(db: Session, subject: Subject) -> Subject:
    db.add(subject)
    db.flush()
    return subject


def get_tutor_capability(db: Session, tutor_id: int, subject_id: int) -> Optional[TutorCapability]:
    return (
        db.query(TutorCapability)
        .filter(TutorCapability.tutor_id == tutor_id, TutorCapability.subject_id == subject_id)
        .first()
    )


def get_tutor_capability_by_id(db: Session, tutor_id: int, capability_id: int) -> Optional[TutorCapability]:
    return (
        db.query(TutorCapability)
        .filter(TutorCapability.tutor_id == tutor_id, TutorCapability.capability_id == capability_id)
        .first()
    )


def create_tutor_capability(db: Session, capability: TutorCapability) -> TutorCapability:
    db.add(capability)
    db.flush()
    return capability


def delete_tutor_capability(db: Session, capability: TutorCapability) -> None:
    db.delete(capability)


def get_tutor_availabilities(db: Session, tutor_id: int) -> list[TutorAvailability]:
    return (
        db.query(TutorAvailability)
        .filter(TutorAvailability.tutor_id == tutor_id)
        .order_by(TutorAvailability.day_of_week.asc(), TutorAvailability.start_time.asc())
        .all()
    )


def get_tutor_availability(db: Session, tutor_id: int, availability_id: int) -> Optional[TutorAvailability]:
    return (
        db.query(TutorAvailability)
        .filter(
            TutorAvailability.tutor_id == tutor_id,
            TutorAvailability.availability_id == availability_id,
        )
        .first()
    )


def create_tutor_availability(db: Session, availability: TutorAvailability) -> TutorAvailability:
    db.add(availability)
    db.flush()
    return availability


def get_learning_requests(
    db: Session,
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    subject: Optional[str] = None,
    status: Optional[str] = None,
) -> list[LearningRequest]:
    query = db.query(LearningRequest).options(
        joinedload(LearningRequest.student),
        joinedload(LearningRequest.subject),
    )
    if student_id:
        query = query.filter(LearningRequest.student_id == student_id)
    if subject_id:
        query = query.filter(LearningRequest.subject_id == subject_id)
    if subject:
        query = query.join(Subject).filter(Subject.subject_name.ilike(f"%{subject}%"))
    if status:
        query = query.filter(LearningRequest.status == status)
    return query.order_by(LearningRequest.request_id.desc()).all()


def get_learning_request(db: Session, request_id: int) -> Optional[LearningRequest]:
    return (
        db.query(LearningRequest)
        .options(joinedload(LearningRequest.student), joinedload(LearningRequest.subject))
        .filter(LearningRequest.request_id == request_id)
        .first()
    )


def create_learning_request(db: Session, request: LearningRequest) -> LearningRequest:
    db.add(request)
    db.flush()
    return request


def get_assignments(
    db: Session,
    request_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    status: Optional[str] = None,
) -> list[TutorAssignment]:
    query = db.query(TutorAssignment)
    if request_id:
        query = query.filter(TutorAssignment.request_id == request_id)
    if tutor_id:
        query = query.filter(TutorAssignment.tutor_id == tutor_id)
    if status:
        query = query.filter(TutorAssignment.status == status)
    return query.order_by(TutorAssignment.assignment_id.desc()).all()


def get_assignment(db: Session, assignment_id: int) -> Optional[TutorAssignment]:
    return db.query(TutorAssignment).filter(TutorAssignment.assignment_id == assignment_id).first()


def create_assignment(db: Session, assignment: TutorAssignment) -> TutorAssignment:
    db.add(assignment)
    db.flush()
    return assignment


def get_classes(
    db: Session,
    search: Optional[str] = None,
    student_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    status: Optional[str] = None,
) -> list[StudyClass]:
    query = db.query(StudyClass).options(
        joinedload(StudyClass.assignment)
        .joinedload(TutorAssignment.learning_request)
        .joinedload(LearningRequest.student),
        joinedload(StudyClass.assignment)
        .joinedload(TutorAssignment.learning_request)
        .joinedload(LearningRequest.subject),
        joinedload(StudyClass.assignment).joinedload(TutorAssignment.tutor),
        joinedload(StudyClass.schedules),
        joinedload(StudyClass.sessions),
    )
    query = query.join(TutorAssignment).join(LearningRequest).join(Student).join(Subject).join(Tutor)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                StudyClass.class_code.ilike(pattern),
                Student.full_name.ilike(pattern),
                Tutor.full_name.ilike(pattern),
                Subject.subject_name.ilike(pattern),
            )
        )
    if student_id:
        query = query.filter(LearningRequest.student_id == student_id)
    if tutor_id:
        query = query.filter(TutorAssignment.tutor_id == tutor_id)
    if subject_id:
        query = query.filter(LearningRequest.subject_id == subject_id)
    if status:
        query = query.filter(StudyClass.status == status)
    return query.order_by(StudyClass.class_id.desc()).all()


def get_class(db: Session, class_id: int) -> Optional[StudyClass]:
    return (
        db.query(StudyClass)
        .options(
            joinedload(StudyClass.assignment)
            .joinedload(TutorAssignment.learning_request)
            .joinedload(LearningRequest.student),
            joinedload(StudyClass.assignment)
            .joinedload(TutorAssignment.learning_request)
            .joinedload(LearningRequest.subject),
            joinedload(StudyClass.assignment).joinedload(TutorAssignment.tutor),
            joinedload(StudyClass.schedules),
            joinedload(StudyClass.sessions),
        )
        .filter(StudyClass.class_id == class_id)
        .first()
    )


def create_class(db: Session, study_class: StudyClass) -> StudyClass:
    db.add(study_class)
    db.flush()
    return study_class


def get_schedules(
    db: Session,
    class_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    student_id: Optional[int] = None,
) -> list[ClassSchedule]:
    query = db.query(ClassSchedule).join(StudyClass).join(TutorAssignment).join(LearningRequest)
    if class_id:
        query = query.filter(ClassSchedule.class_id == class_id)
    if tutor_id:
        query = query.filter(TutorAssignment.tutor_id == tutor_id)
    if student_id:
        query = query.filter(LearningRequest.student_id == student_id)
    return query.order_by(ClassSchedule.schedule_id.desc()).all()


def get_schedule(db: Session, schedule_id: int) -> Optional[ClassSchedule]:
    return db.query(ClassSchedule).filter(ClassSchedule.schedule_id == schedule_id).first()


def create_schedule(db: Session, schedule: ClassSchedule) -> ClassSchedule:
    db.add(schedule)
    db.flush()
    return schedule


def get_sessions(
    db: Session,
    class_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    lesson_date: Optional[date] = None,
) -> list[LessonSession]:
    query = db.query(LessonSession).join(StudyClass).join(TutorAssignment).join(LearningRequest)
    if class_id:
        query = query.filter(LessonSession.class_id == class_id)
    if tutor_id:
        query = query.filter(TutorAssignment.tutor_id == tutor_id)
    if student_id:
        query = query.filter(LearningRequest.student_id == student_id)
    if status:
        query = query.filter(LessonSession.status == status)
    if lesson_date:
        query = query.filter(LessonSession.lesson_date == lesson_date)
    return query.order_by(LessonSession.lesson_date.desc(), LessonSession.session_id.desc()).all()


def get_session(db: Session, session_id: int) -> Optional[LessonSession]:
    return db.query(LessonSession).filter(LessonSession.session_id == session_id).first()


def create_session(db: Session, session: LessonSession) -> LessonSession:
    db.add(session)
    db.flush()
    return session


def get_invoices(
    db: Session,
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    period_filter: Optional[str] = None,
) -> list[TuitionInvoice]:
    query = db.query(TuitionInvoice).options(joinedload(TuitionInvoice.study_class)).join(StudyClass).join(TutorAssignment).join(LearningRequest)
    if class_id:
        query = query.filter(TuitionInvoice.class_id == class_id)
    if student_id:
        query = query.filter(LearningRequest.student_id == student_id)
    if status:
        query = query.filter(TuitionInvoice.status == status)
    if period_filter:
        query = query.filter(
            or_(
                cast(TuitionInvoice.period_start, String).ilike(f"%{period_filter}%"),
                cast(TuitionInvoice.period_end, String).ilike(f"%{period_filter}%"),
            )
        )
    return query.order_by(TuitionInvoice.invoice_id.desc()).all()


def get_invoice(db: Session, invoice_id: int) -> Optional[TuitionInvoice]:
    return (
        db.query(TuitionInvoice)
        .options(joinedload(TuitionInvoice.study_class), joinedload(TuitionInvoice.payments))
        .filter(TuitionInvoice.invoice_id == invoice_id)
        .first()
    )


def create_invoice(db: Session, invoice: TuitionInvoice) -> TuitionInvoice:
    db.add(invoice)
    db.flush()
    return invoice


def get_invoice_by_class_period(
    db: Session,
    class_id: int,
    period_start: date,
    period_end: date,
) -> Optional[TuitionInvoice]:
    return (
        db.query(TuitionInvoice)
        .options(joinedload(TuitionInvoice.study_class), joinedload(TuitionInvoice.payments))
        .filter(
            TuitionInvoice.class_id == class_id,
            TuitionInvoice.period_start == period_start,
            TuitionInvoice.period_end == period_end,
        )
        .first()
    )


def get_payments(
    db: Session,
    class_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    invoice_status: Optional[str] = None,
    period_filter: Optional[str] = None,
) -> list[TuitionPayment]:
    query = (
        db.query(TuitionPayment)
        .options(
            joinedload(TuitionPayment.invoice)
            .joinedload(TuitionInvoice.study_class)
            .joinedload(StudyClass.assignment)
            .joinedload(TutorAssignment.learning_request)
            .joinedload(LearningRequest.subject),
            joinedload(TuitionPayment.invoice)
            .joinedload(TuitionInvoice.study_class)
            .joinedload(StudyClass.assignment)
            .joinedload(TutorAssignment.learning_request)
            .joinedload(LearningRequest.student),
        )
        .join(TuitionInvoice)
        .join(StudyClass)
        .join(TutorAssignment)
        .join(LearningRequest)
    )
    if class_id:
        query = query.filter(TuitionInvoice.class_id == class_id)
    if student_id:
        query = query.filter(LearningRequest.student_id == student_id)
    if status:
        query = query.filter(TuitionPayment.status == status)
    if invoice_status:
        query = query.filter(TuitionInvoice.status == invoice_status)
    if period_filter:
        query = query.filter(
            or_(
                cast(TuitionInvoice.period_start, String).ilike(f"%{period_filter}%"),
                cast(TuitionInvoice.period_end, String).ilike(f"%{period_filter}%"),
            )
        )
    return query.order_by(TuitionPayment.payment_id.desc()).all()


def get_payment(db: Session, payment_id: int) -> Optional[TuitionPayment]:
    return (
        db.query(TuitionPayment)
        .options(
            joinedload(TuitionPayment.invoice)
            .joinedload(TuitionInvoice.study_class)
            .joinedload(StudyClass.assignment)
            .joinedload(TutorAssignment.learning_request)
            .joinedload(LearningRequest.subject),
            joinedload(TuitionPayment.invoice)
            .joinedload(TuitionInvoice.study_class)
            .joinedload(StudyClass.assignment)
            .joinedload(TutorAssignment.learning_request)
            .joinedload(LearningRequest.student),
        )
        .filter(TuitionPayment.payment_id == payment_id)
        .first()
    )


def create_payment(db: Session, payment: TuitionPayment) -> TuitionPayment:
    db.add(payment)
    db.flush()
    return payment


def delete_model(db: Session, model) -> None:
    db.delete(model)


def commit(db: Session):
    db.commit()


def refresh(db: Session, model):
    db.refresh(model)
    return model

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    Unicode,
    UnicodeText,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserAccount(Base):
    __tablename__ = "USER_ACCOUNT"

    account_id = Column(Integer, primary_key=True, index=True)
    email = Column(Unicode(255), nullable=False, unique=True)
    username = Column(Unicode(50), nullable=False, unique=True)
    password_hash = Column(Unicode(255), nullable=False)
    role = Column(Unicode(20), nullable=False)
    status = Column(Unicode(20), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)


class Subject(Base):
    __tablename__ = "SUBJECT"

    subject_id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(Unicode(100), nullable=False)
    subject_group = Column(Unicode(50), nullable=True)
    grade_level = Column(Unicode(50), nullable=True)
    description = Column(UnicodeText, nullable=True)
    status = Column(Unicode(20), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    capabilities = relationship("TutorCapability", back_populates="subject")
    learning_requests = relationship("LearningRequest", back_populates="subject")


class Staff(Base):
    __tablename__ = "STAFF"

    staff_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("USER_ACCOUNT.account_id"), nullable=True)
    full_name = Column(Unicode(150), nullable=False)
    phone = Column(Unicode(20), nullable=True)
    contact_email = Column(Unicode(255), nullable=True)
    position = Column(Unicode(50), nullable=True)
    status = Column(Unicode(20), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    account = relationship("UserAccount")
    assignments = relationship("TutorAssignment", back_populates="staff")


class Student(Base):
    __tablename__ = "STUDENT"

    student_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("USER_ACCOUNT.account_id"), nullable=True)
    full_name = Column(Unicode(150), nullable=False)
    phone = Column(Unicode(20), nullable=False)
    contact_email = Column(Unicode(255), nullable=True)
    address = Column(Unicode(255), nullable=True)
    area = Column(Unicode(150), nullable=True)
    current_level = Column(Unicode(50), nullable=True)
    grade_level = Column(Unicode(50), nullable=True)
    status = Column(Unicode(20), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    account = relationship("UserAccount")
    learning_requests = relationship("LearningRequest", back_populates="student")


class Tutor(Base):
    __tablename__ = "TUTOR"

    tutor_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("USER_ACCOUNT.account_id"), nullable=True)
    full_name = Column(Unicode(150), nullable=False)
    phone = Column(Unicode(20), nullable=True)
    contact_email = Column(Unicode(255), nullable=True)
    university = Column(Unicode(150), nullable=True)
    major = Column(Unicode(150), nullable=True)
    area = Column(Unicode(255), nullable=True)
    experience_years = Column(Integer, nullable=False, default=0)
    status = Column(Unicode(20), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    account = relationship("UserAccount")
    availabilities = relationship("TutorAvailability", back_populates="tutor")
    capabilities = relationship("TutorCapability", back_populates="tutor")
    assignments = relationship("TutorAssignment", back_populates="tutor")


class TutorAvailability(Base):
    __tablename__ = "TUTOR_AVAILABILITY"

    availability_id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("TUTOR.tutor_id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    teaching_mode = Column(Unicode(20), nullable=False, default="OFFLINE")
    area = Column(Unicode(150), nullable=True)
    status = Column(Unicode(20), nullable=False, default="AVAILABLE")
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    tutor = relationship("Tutor", back_populates="availabilities")


class TutorCapability(Base):
    __tablename__ = "TUTOR_CAPABILITY"

    capability_id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("TUTOR.tutor_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("SUBJECT.subject_id"), nullable=False)
    teaching_level = Column(Unicode(50), nullable=True)
    years_experience = Column(Integer, nullable=False, default=0)
    note = Column(Unicode(500), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    tutor = relationship("Tutor", back_populates="capabilities")
    subject = relationship("Subject", back_populates="capabilities")


class LearningRequest(Base):
    __tablename__ = "LEARNING_REQUEST"

    request_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("STUDENT.student_id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("SUBJECT.subject_id"), nullable=False)
    requested_level = Column(Unicode(50), nullable=True)
    learning_goal = Column(UnicodeText, nullable=True)
    preferred_area = Column(Unicode(255), nullable=True)
    preferred_mode = Column(Unicode(20), nullable=False, default="OFFLINE")
    preferred_schedule = Column(Unicode(255), nullable=True)
    expected_fee = Column(Numeric(18, 2), nullable=True)
    status = Column(Unicode(20), nullable=False, default="PENDING")
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="learning_requests")
    subject = relationship("Subject", back_populates="learning_requests")
    assignments = relationship("TutorAssignment", back_populates="learning_request")


class TutorAssignment(Base):
    __tablename__ = "TUTOR_ASSIGNMENT"

    assignment_id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("LEARNING_REQUEST.request_id"), nullable=False)
    tutor_id = Column(Integer, ForeignKey("TUTOR.tutor_id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("STAFF.staff_id"), nullable=True)
    status = Column(Unicode(20), nullable=False, default="ASSIGNED")
    assigned_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    note = Column(Unicode(500), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    learning_request = relationship("LearningRequest", back_populates="assignments")
    tutor = relationship("Tutor", back_populates="assignments")
    staff = relationship("Staff", back_populates="assignments")
    study_class = relationship("StudyClass", back_populates="assignment", uselist=False)


class StudyClass(Base):
    __tablename__ = "STUDY_CLASS"

    class_id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("TUTOR_ASSIGNMENT.assignment_id"), nullable=False, unique=True)
    class_code = Column(Unicode(50), nullable=False, unique=True)
    tuition_fee_per_session = Column(Numeric(18, 2), nullable=False)
    teaching_mode = Column(Unicode(20), nullable=False, default="OFFLINE")
    location = Column(Unicode(255), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(Unicode(20), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    assignment = relationship("TutorAssignment", back_populates="study_class")
    schedules = relationship("ClassSchedule", back_populates="study_class")
    sessions = relationship("LessonSession", back_populates="study_class")
    invoices = relationship("TuitionInvoice", back_populates="study_class")


class ClassSchedule(Base):
    __tablename__ = "CLASS_SCHEDULE"

    schedule_id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("STUDY_CLASS.class_id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    status = Column(Unicode(20), nullable=False, default="ACTIVE")
    note = Column(Unicode(500), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    study_class = relationship("StudyClass", back_populates="schedules")


class LessonSession(Base):
    __tablename__ = "LESSON_SESSION"

    session_id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("STUDY_CLASS.class_id"), nullable=False)
    schedule_id = Column(Integer, nullable=True)
    session_number = Column(Integer, nullable=True)
    lesson_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    status = Column(Unicode(30), nullable=False, default="SCHEDULED")
    content_note = Column(UnicodeText, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    study_class = relationship("StudyClass", back_populates="sessions")


class TuitionInvoice(Base):
    __tablename__ = "TUITION_INVOICE"

    invoice_id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("STUDY_CLASS.class_id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    completed_sessions = Column(Integer, nullable=False, default=0)
    tuition_fee_per_session = Column(Numeric(18, 2), nullable=False)
    amount_due = Column(Numeric(18, 2), nullable=False)
    amount_paid = Column(Numeric(18, 2), nullable=False, default=0)
    status = Column(Unicode(20), nullable=False, default="UNPAID")
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    study_class = relationship("StudyClass", back_populates="invoices")
    payments = relationship("TuitionPayment", back_populates="invoice")


class TuitionPayment(Base):
    __tablename__ = "TUITION_PAYMENT"
    __table_args__ = {"implicit_returning": False}

    payment_id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("TUITION_INVOICE.invoice_id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("STAFF.staff_id"), nullable=True)
    payment_date = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    amount_paid = Column(Numeric(18, 2), nullable=False)
    payment_method = Column(Unicode(50), nullable=True)
    note = Column(UnicodeText, nullable=True)
    status = Column(Unicode(20), nullable=False, default="SUCCESS")
    created_at = Column(DateTime, nullable=False, server_default=func.sysutcdatetime())
    updated_at = Column(DateTime, nullable=True)

    invoice = relationship("TuitionInvoice", back_populates="payments")
    staff = relationship("Staff")

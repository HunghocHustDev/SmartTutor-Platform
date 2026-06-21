from datetime import date as date_type
from datetime import datetime as datetime_type
from datetime import time as time_type
from decimal import Decimal
from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class DetailMessage(BaseModel):
    detail: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthUser(BaseModel):
    id: int
    name: str
    role: str
    email: Optional[str] = None
    area: Optional[str] = None
    level: Optional[str] = None
    university: Optional[str] = None
    major: Optional[str] = None
    experience: Optional[int] = None
    position: Optional[str] = None


class LoginResponse(BaseModel):
    user: AuthUser
    token: str
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    fullName: Optional[str] = None
    email: str
    phone: str
    password: str
    role: str = "student"
    area: Optional[str] = None
    level: Optional[str] = None
    university: Optional[str] = None
    major: Optional[str] = None
    experience: Optional[int] = 0


class RegisterResponse(BaseModel):
    id: int
    name: str
    full_name: str
    email: str
    phone: str
    role: str
    status: str
    area: Optional[str] = None
    level: Optional[str] = None
    university: Optional[str] = None
    major: Optional[str] = None
    experience: Optional[int] = None


class StudentBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    area: Optional[str] = None
    level: Optional[str] = None
    status: str = "ACTIVE"


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    area: Optional[str] = None
    level: Optional[str] = None
    status: Optional[str] = None


class StudentResponse(StudentBase):
    id: int


class TutorBase(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    area: Optional[str] = None
    subjects: Optional[str] = None
    experience: int = 0
    status: str = "ACTIVE"


class TutorCreate(TutorBase):
    pass


class TutorUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    area: Optional[str] = None
    subjects: Optional[str] = None
    experience: Optional[int] = None
    status: Optional[str] = None


class TutorResponse(TutorBase):
    id: int


class SubjectBase(BaseModel):
    name: str
    level: Optional[str] = None
    subject_group: Optional[str] = None
    description: Optional[str] = None
    status: str = "ACTIVE"


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[str] = None
    subject_group: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class SubjectResponse(SubjectBase):
    id: int


class TutorSubjectCreate(BaseModel):
    subject_id: int
    teaching_level: Optional[str] = None
    years_experience: int = 0
    note: Optional[str] = None


class TutorSubjectResponse(BaseModel):
    capability_id: Optional[int] = None
    subject_id: int
    name: str
    level: Optional[str] = None
    teaching_level: Optional[str] = None
    years_experience: int = 0


class TutorAvailabilityCreate(BaseModel):
    day_of_week: int
    start_time: time_type
    end_time: time_type
    teaching_mode: str = "OFFLINE"
    area: Optional[str] = None
    status: str = "AVAILABLE"


class TutorAvailabilityUpdate(BaseModel):
    day_of_week: Optional[int] = None
    start_time: Optional[time_type] = None
    end_time: Optional[time_type] = None
    teaching_mode: Optional[str] = None
    area: Optional[str] = None
    status: Optional[str] = None


class TutorAvailabilityResponse(BaseModel):
    id: int
    tutor_id: int
    day_of_week: int
    start_time: time_type
    end_time: time_type
    teaching_mode: str
    area: Optional[str] = None
    status: str


class LearningRequestCreate(BaseModel):
    student_id: int
    subject_id: Optional[int] = None
    subject: Optional[str] = None
    target: Optional[str] = None
    requested_level: Optional[str] = None
    area: Optional[str] = None
    preferred_schedule: Optional[str] = None
    expected_fee: Optional[Decimal] = None
    teaching_mode: str = "OFFLINE"
    learning_goal: Optional[str] = None


class LearningRequestUpdate(BaseModel):
    subject_id: Optional[int] = None
    subject: Optional[str] = None
    target: Optional[str] = None
    requested_level: Optional[str] = None
    area: Optional[str] = None
    preferred_schedule: Optional[str] = None
    expected_fee: Optional[Decimal] = None
    teaching_mode: Optional[str] = None
    learning_goal: Optional[str] = None
    status: Optional[str] = None


class LearningRequestResponse(BaseModel):
    id: int
    student_id: int
    student: Optional[str] = None
    subject_id: int
    subject: str
    target: Optional[str] = None
    requested_level: Optional[str] = None
    area: Optional[str] = None
    preferred_schedule: Optional[str] = None
    expected_fee: Optional[float] = None
    teaching_mode: str = "OFFLINE"
    learning_goal: Optional[str] = None
    status: str
    date: Optional[date_type] = None


class TutorAssignmentCreate(BaseModel):
    request_id: int
    tutor_id: int
    staff_id: Optional[int] = None
    note: Optional[str] = None


class TutorAssignmentUpdate(BaseModel):
    tutor_id: Optional[int] = None
    staff_id: Optional[int] = None
    status: Optional[str] = None
    note: Optional[str] = None


class TutorAssignmentResponse(BaseModel):
    id: int
    request_id: int
    tutor_id: int
    staff_id: Optional[int] = None
    status: str
    assigned_at: Optional[datetime_type] = None
    note: Optional[str] = None
    class_id: Optional[int] = None


class StudyClassCreate(BaseModel):
    assignment_id: int
    class_code: Optional[str] = None
    tuition_fee_per_session: Decimal
    teaching_mode: str = "OFFLINE"
    location: Optional[str] = None
    start_date: date_type
    end_date: Optional[date_type] = None
    status: str = "ACTIVE"


class StudyClassUpdate(BaseModel):
    tuition_fee_per_session: Optional[Decimal] = None
    teaching_mode: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date_type] = None
    end_date: Optional[date_type] = None
    status: Optional[str] = None


class StudyClassResponse(BaseModel):
    id: int
    code: str
    assignment_id: Optional[int] = None
    student: Optional[str] = None
    studentId: Optional[int] = None
    tutor: Optional[str] = None
    tutorId: Optional[int] = None
    subject: Optional[str] = None
    subject_id: Optional[int] = None
    level: Optional[str] = None
    schedule: Optional[str] = None
    fee: float
    tuition_fee_per_session: float
    teaching_mode: str
    location: Optional[str] = None
    status: str
    startDate: Optional[date_type] = None
    endDate: Optional[date_type] = None
    nextLesson: Optional[date_type] = None


class ClassScheduleCreate(BaseModel):
    class_id: int
    day_of_week: int
    start_time: time_type
    end_time: time_type
    effective_from: Optional[date_type] = None
    effective_to: Optional[date_type] = None
    status: str = "ACTIVE"
    note: Optional[str] = None


class ClassScheduleUpdate(BaseModel):
    day_of_week: Optional[int] = None
    start_time: Optional[time_type] = None
    end_time: Optional[time_type] = None
    effective_from: Optional[date_type] = None
    effective_to: Optional[date_type] = None
    status: Optional[str] = None
    note: Optional[str] = None


class ClassScheduleResponse(BaseModel):
    id: int
    class_id: int
    day_of_week: int
    start_time: time_type
    end_time: time_type
    display_text: str
    effective_from: Optional[date_type] = None
    effective_to: Optional[date_type] = None
    status: str
    note: Optional[str] = None


class LessonSessionCreate(BaseModel):
    class_id: int
    schedule_id: Optional[int] = None
    session_number: Optional[int] = None
    lesson_date: date_type = Field(validation_alias=AliasChoices("lesson_date", "session_date", "date"))
    start_time: Optional[time_type] = None
    end_time: Optional[time_type] = None
    status: str = "SCHEDULED"
    content_note: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class LessonSessionUpdate(BaseModel):
    schedule_id: Optional[int] = None
    session_number: Optional[int] = None
    lesson_date: Optional[date_type] = Field(
        default=None,
        validation_alias=AliasChoices("lesson_date", "session_date", "date"),
    )
    start_time: Optional[time_type] = None
    end_time: Optional[time_type] = None
    status: Optional[str] = None
    content_note: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class LessonSessionStatusUpdate(BaseModel):
    status: str
    content_note: Optional[str] = None


class LessonSessionResponse(BaseModel):
    id: int
    class_id: int
    schedule_id: Optional[int] = None
    session_number: Optional[int] = None
    date: date_type
    class_name: Optional[str] = Field(default=None, alias="class")
    content: Optional[str] = None
    attendance: Optional[str] = None
    status: str

    class Config:
        populate_by_name = True


class TuitionInvoiceCreate(BaseModel):
    class_id: int
    period_start: date_type
    period_end: date_type
    completed_sessions: int = 0
    tuition_fee_per_session: Decimal
    amount_due: Decimal
    amount_paid: Decimal = Decimal("0")
    status: str = "UNPAID"


class TuitionInvoiceUpdate(BaseModel):
    period_start: Optional[date_type] = None
    period_end: Optional[date_type] = None
    completed_sessions: Optional[int] = None
    tuition_fee_per_session: Optional[Decimal] = None
    amount_due: Optional[Decimal] = None
    amount_paid: Optional[Decimal] = None
    status: Optional[str] = None


class TuitionInvoiceResponse(BaseModel):
    id: int
    class_id: int
    period_start: date_type
    period_end: date_type
    completed_sessions: int
    tuition_fee_per_session: float
    amount_due: float
    amount_paid: float
    status: str
    created_at: Optional[datetime_type] = None


class TuitionPaymentCreate(BaseModel):
    invoice_id: Optional[int] = None
    class_id: Optional[int] = None
    student_id: Optional[int] = None
    amount_paid: Decimal = Field(validation_alias=AliasChoices("amount_paid", "amount"))
    period: Optional[str] = None
    period_start: Optional[date_type] = None
    period_end: Optional[date_type] = None
    status: Optional[str] = None
    payment_date: Optional[datetime_type] = Field(default=None, validation_alias=AliasChoices("payment_date", "paid_at"))
    payment_method: Optional[str] = Field(default=None, validation_alias=AliasChoices("payment_method", "method"))
    staff_id: Optional[int] = None
    note: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class TuitionPaymentUpdate(BaseModel):
    amount_paid: Optional[Decimal] = Field(default=None, validation_alias=AliasChoices("amount_paid", "amount"))
    payment_date: Optional[datetime_type] = Field(default=None, validation_alias=AliasChoices("payment_date", "paid_at"))
    payment_method: Optional[str] = Field(default=None, validation_alias=AliasChoices("payment_method", "method"))
    status: Optional[str] = None
    staff_id: Optional[int] = None
    note: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class TuitionPaymentResponse(BaseModel):
    id: int
    invoice_id: Optional[int] = None
    student_id: Optional[int] = None
    class_id: Optional[int] = None
    className: Optional[str] = None
    amount: str
    amount_value: float
    period: Optional[str] = None
    status: str
    status_code: str
    paid_at: Optional[datetime_type] = None
    payment_method: Optional[str] = None
    invoice_status: Optional[str] = None
    invoice_status_code: Optional[str] = None


class TuitionSummaryResponse(BaseModel):
    class_id: int
    completed_sessions: int
    tuition_fee_per_session: float
    total_fee: float
    paid_amount: float
    remaining_amount: float


class InvoicePeriodResponse(BaseModel):
    period_start: str
    period_end: str
    completed_sessions: int


class DashboardSummaryResponse(BaseModel):
    total_students: int
    total_tutors: int
    pending_learning_requests: int
    active_classes: int
    completed_sessions: int
    unpaid_invoices: int
    partially_paid_invoices: int
    successful_payments: int


class TutorSuggestionItem(BaseModel):
    tutor_id: int
    full_name: str
    phone: Optional[str] = None
    area: Optional[str] = None
    experience_years: int = 0
    current_classes: int = 0
    max_classes: int = 10
    score: int = 0
    match_reasons: list[str] = []


class TutorSuggestionResponse(BaseModel):
    request_id: int
    subject_id: int
    suggestions: list[TutorSuggestionItem]

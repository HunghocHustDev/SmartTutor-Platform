from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import ClassSchedule, LessonSession
from app.repositories import data_repository as repo
from app.schemas.entities import (
    ClassScheduleCreate,
    ClassScheduleUpdate,
    LessonSessionCreate,
    LessonSessionStatusUpdate,
    LessonSessionUpdate,
    StudyClassCreate,
    StudyClassUpdate,
)
from app.services.common import (
    CLASS_STATUSES,
    SCHEDULE_STATUSES,
    SESSION_STATUSES,
    _money,
    _normalize_choice,
    _normalize_class_status,
    _normalize_mode,
    _validate_date_window,
    _validate_non_negative_decimal,
    _validate_positive_int,
    _validate_schedule_window,
    _validate_session_window,
    class_to_response,
    get_assignment_or_404,
    get_class_or_404,
    get_schedule_or_404,
    get_session_or_404,
    schedule_to_response,
    session_to_response,
)


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
    teaching_mode = _normalize_mode(payload.teaching_mode, {"ONLINE", "OFFLINE"}, "teaching_mode")
    class_status = _normalize_class_status(payload.status) or "ACTIVE"
    study_class = repo.call_create_class_from_assignment(
        db,
        assignment_id=assignment.assignment_id,
        class_code=payload.class_code or f"CLS-{assignment.assignment_id:04d}",
        tuition_fee_per_session=payload.tuition_fee_per_session,
        teaching_mode=teaching_mode,
        location=payload.location,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=class_status,
    )
    repo.commit(db)
    return class_to_response(repo.get_class(db, study_class.class_id))


def update_study_class(db: Session, class_id: int, payload: StudyClassUpdate) -> dict:
    study_class = get_class_or_404(db, class_id)
    data = payload.model_dump(exclude_unset=True)
    if "tuition_fee_per_session" in data:
        _validate_non_negative_decimal(data["tuition_fee_per_session"], "tuition_fee_per_session")
    _validate_date_window(data.get("start_date", study_class.start_date), data.get("end_date", study_class.end_date), "start_date", "end_date")
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


def list_sessions(db: Session, session_date: date | None = None, **filters) -> list[dict]:
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


def update_session(db: Session, session_id: int, payload: LessonSessionUpdate) -> dict:
    session = get_session_or_404(db, session_id)
    data = payload.model_dump(exclude_unset=True)
    if "schedule_id" in data and data["schedule_id"] is not None:
        schedule = get_schedule_or_404(db, data["schedule_id"])
        if schedule.class_id != session.class_id:
            raise HTTPException(status_code=400, detail="schedule_id must belong to the session class")
    if "session_number" in data:
        _validate_positive_int(data["session_number"], "session_number")
    _validate_session_window(data.get("start_time", session.start_time), data.get("end_time", session.end_time))
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

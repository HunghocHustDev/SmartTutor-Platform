from datetime import date, timedelta

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


def _resolve_session_window(
    class_start: date | None,
    class_end: date | None,
    range_start: date | None,
    range_end: date | None,
) -> tuple[date, date]:
    start = range_start or class_start or date.today()
    end = range_end or class_end or (start + timedelta(days=90))
    if end < start:
        raise HTTPException(status_code=400, detail="range_end must be on or after range_start")
    return start, end


def _iter_candidate_dates(
    range_start: date,
    range_end: date,
    weekday: int,
) -> list[date]:
    candidates: list[date] = []
    cursor = range_start
    while cursor <= range_end:
        if cursor.isoweekday() == weekday:
            candidates.append(cursor)
        cursor += timedelta(days=1)
    return candidates


def _build_session_plan(
    study_class,
    schedules: list[ClassSchedule],
    existing_sessions: list[LessonSession],
    range_start: date,
    range_end: date,
) -> list[dict]:
    active_schedules = [item for item in schedules if item.status == "ACTIVE"]
    if not active_schedules:
        return []
    existing_dates = {(item.lesson_date, item.start_time) for item in existing_sessions if item.lesson_date}
    next_number = max((item.session_number or 0) for item in existing_sessions) + 1
    plan: list[dict] = []
    for schedule in sorted(active_schedules, key=lambda item: (item.day_of_week, item.start_time)):
        eff_from = max(schedule.effective_from or range_start, range_start)
        eff_to = min(schedule.effective_to or range_end, range_end)
        if eff_to < eff_from:
            continue
        for candidate_date in _iter_candidate_dates(eff_from, eff_to, schedule.day_of_week):
            if (candidate_date, schedule.start_time) in existing_dates:
                continue
            plan.append(
                {
                    "schedule_id": schedule.schedule_id,
                    "session_number": next_number,
                    "date": candidate_date,
                    "start_time": schedule.start_time,
                    "end_time": schedule.end_time,
                }
            )
            existing_dates.add((candidate_date, schedule.start_time))
            next_number += 1
    return plan


def generate_sessions_from_schedules(
    db: Session,
    class_id: int,
    range_start: date | None = None,
    range_end: date | None = None,
) -> dict:
    study_class = get_class_or_404(db, class_id)
    start, end = _resolve_session_window(study_class.start_date, study_class.end_date, range_start, range_end)
    schedules = list(repo.get_schedules(db, class_id=class_id))
    existing_sessions = list(repo.get_sessions(db, class_id=class_id))
    plan = _build_session_plan(study_class, schedules, existing_sessions, start, end)
    if not plan:
        return {
            "class_id": class_id,
            "created_count": 0,
            "created_session_ids": [],
            "skipped_existing": True,
            "range_start": start,
            "range_end": end,
        }
    created_ids: list[int] = []
    for entry in plan:
        session = repo.create_session(
            db,
            LessonSession(
                class_id=class_id,
                schedule_id=entry["schedule_id"],
                session_number=entry["session_number"],
                lesson_date=entry["date"],
                start_time=entry["start_time"],
                end_time=entry["end_time"],
                status="SCHEDULED",
            ),
        )
        created_ids.append(session.session_id)
    repo.commit(db)
    return {
        "class_id": class_id,
        "created_count": len(created_ids),
        "created_session_ids": created_ids,
        "skipped_existing": False,
        "range_start": start,
        "range_end": end,
    }


def preview_sessions_from_schedules(
    db: Session,
    class_id: int,
    range_start: date | None = None,
    range_end: date | None = None,
) -> dict:
    study_class = get_class_or_404(db, class_id)
    start, end = _resolve_session_window(study_class.start_date, study_class.end_date, range_start, range_end)
    schedules = list(repo.get_schedules(db, class_id=class_id))
    existing_sessions = list(repo.get_sessions(db, class_id=class_id))
    plan = _build_session_plan(study_class, schedules, existing_sessions, start, end)
    return {
        "class_id": class_id,
        "range_start": start,
        "range_end": end,
        "preview_count": len(plan),
        "preview": [
            {
                "schedule_id": entry["schedule_id"],
                "session_number": entry["session_number"],
                "date": entry["date"].isoformat(),
                "start_time": entry["start_time"].strftime("%H:%M") if entry["start_time"] else None,
                "end_time": entry["end_time"].strftime("%H:%M") if entry["end_time"] else None,
            }
            for entry in plan
        ],
    }


def get_invoice_period(db: Session, class_id: int) -> dict:
    get_class_or_404(db, class_id)
    today = date.today()
    period_start = today.replace(day=1)
    if today.month == 12:
        period_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        period_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    summary = repo.get_class_tuition_summary(db, class_id)
    completed_sessions = summary.completed_sessions if summary else 0
    return {
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "completed_sessions": completed_sessions,
    }

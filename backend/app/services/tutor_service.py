from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Tutor, TutorAvailability, TutorCapability
from app.repositories import data_repository as repo
from app.schemas.entities import (
    TutorAvailabilityCreate,
    TutorAvailabilityUpdate,
    TutorCreate,
    TutorSubjectCreate,
    TutorUpdate,
)
from app.services.common import (
    ACTIVE_INACTIVE_STATUSES,
    TUTOR_AVAILABILITY_STATUSES,
    TUTOR_STATUSES,
    _ensure_subject,
    _normalize_choice,
    _normalize_mode,
    _validate_non_negative_int,
    _validate_schedule_window,
    get_subject_or_404,
    get_tutor_or_404,
    tutor_availability_to_response,
    tutor_to_response,
)


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

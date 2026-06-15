from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import LearningRequest
from app.repositories import data_repository as repo
from app.schemas.entities import LearningRequestCreate, LearningRequestUpdate, TutorAssignmentCreate, TutorAssignmentUpdate
from app.services.common import (
    ASSIGNMENT_STATUSES,
    LEARNING_REQUEST_STATUSES,
    _ensure_subject,
    _normalize_choice,
    _normalize_mode,
    _validate_non_negative_decimal,
    assignment_to_response,
    get_assignment_or_404,
    get_learning_request_or_404,
    get_staff_or_404,
    get_student_or_404,
    get_tutor_or_404,
    learning_request_to_response,
)


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


def update_learning_request(db: Session, request_id: int, payload: LearningRequestUpdate) -> dict:
    get_learning_request_or_404(db, request_id)
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

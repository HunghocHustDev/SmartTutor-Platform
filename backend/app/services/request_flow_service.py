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
from app.services.schedule_parser import (
    ParsedSchedule,
    build_schedule_display,
    check_time_overlap,
    parse_preferred_schedule,
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


def suggest_tutors_for_request(db: Session, request_id: int) -> dict:
    """
    Suggest candidate tutors for a learning request, ranked by score.

    Scoring factors:
    - experience_years (higher = better): experience * 10
    - area match (tutor.area = request.preferred_area): +20
    - schedule match (real day-of-week + time overlap): +3 to +20
    """
    from app.repositories import tutor_repository as tutor_repo

    request = get_learning_request_or_404(db, request_id)
    parsed = parse_preferred_schedule(request.preferred_schedule)

    candidates = repo.get_candidate_tutors_for_request(
        db,
        subject_id=request.subject_id,
        preferred_area=request.preferred_area,
        preferred_schedule=request.preferred_schedule,
        preferred_mode=request.preferred_mode,
    )

    suggestions = []
    for row in candidates:
        row_dict = dict(row.__dict__) if hasattr(row, "__dict__") and not hasattr(row, "_mapping") else (
            dict(row._mapping) if hasattr(row, "_mapping") else dict(row)
        )
        tutor_id = row_dict["tutor_id"]

        availabilities = tutor_repo.get_tutor_availabilities(db, tutor_id)
        availability_display = [
            {
                "day_of_week": a.day_of_week,
                "day_label": {1: "T2", 2: "T3", 3: "T4", 4: "T5", 5: "T6", 6: "T7", 7: "CN"}.get(a.day_of_week, str(a.day_of_week)),
                "start_time": str(a.start_time)[:5],
                "end_time": str(a.end_time)[:5],
                "teaching_mode": a.teaching_mode,
            }
            for a in availabilities
            if a.status == "AVAILABLE" and a.teaching_mode in ("BOTH", request.preferred_mode or "OFFLINE")
        ]

        match_reasons = []
        schedule_score = 0
        schedule_level = 0

        if row_dict.get("experience_years", 0) >= 3:
            match_reasons.append(f"Kinh nghiệm {row_dict['experience_years']} năm")
        if row_dict.get("area_match"):
            match_reasons.append("Khu vực phù hợp")
        if row_dict.get("mode_match"):
            match_reasons.append("Hình thức phù hợp")

        # Real schedule matching
        if parsed.has_time() and parsed.days:
            matching_days = 0
            total_overlap_minutes = 0
            for avail in availabilities:
                if avail.status != "AVAILABLE":
                    continue
                if avail.day_of_week not in parsed.days:
                    continue
                if avail.teaching_mode not in ("BOTH", request.preferred_mode or "OFFLINE"):
                    continue
                has_overlap, overlap_min = check_time_overlap(
                    parsed.start_time, parsed.end_time,
                    avail.start_time, avail.end_time,
                )
                if has_overlap:
                    matching_days += 1
                    total_overlap_minutes += overlap_min

            if matching_days > 0:
                # Level 3: full coverage on at least one day
                if matching_days >= 1 and total_overlap_minutes > 0:
                    req_duration = (
                        (parsed.end_time.hour * 60 + parsed.end_time.minute)
                        - (parsed.start_time.hour * 60 + parsed.start_time.minute)
                    )
                    if total_overlap_minutes >= req_duration:
                        schedule_score = 20
                        schedule_level = 3
                        match_reasons.append(f"Lịch trùng khớp {matching_days} ngày (đủ giờ)")
                    else:
                        schedule_score = 10
                        schedule_level = 2
                        match_reasons.append(f"Lịch trùng {matching_days} ngày ({total_overlap_minutes}ph overlap)")
                if matching_days >= 2:
                    schedule_score += 2 * (matching_days - 1)
                    schedule_level = 3
        elif parsed.days and not parsed.has_time():
            # Only day match, no time info
            for avail in availabilities:
                if avail.status != "AVAILABLE":
                    continue
                if avail.day_of_week in parsed.days:
                    schedule_score = 3
                    schedule_level = 1
                    match_reasons.append("Có ngày trùng")
                    break
        else:
            # No parseable schedule - zero schedule points, but still show reason
            match_reasons.append("Chưa có thông tin lịch cụ thể")

        if row_dict.get("current_classes", 0) < 3:
            match_reasons.append("Ít lớp đang dạy")

        score = (
            (row_dict.get("experience_years", 0) or 0) * 10
            + (20 if row_dict.get("area_match") else 0)
            + schedule_score
        )

        suggestions.append({
            "tutor_id": row_dict["tutor_id"],
            "full_name": row_dict["full_name"],
            "phone": row_dict.get("phone"),
            "area": row_dict.get("tutor_area"),
            "experience_years": row_dict.get("experience_years", 0),
            "current_classes": row_dict.get("current_classes", 0),
            "max_classes": row_dict.get("max_classes", 10),
            "score": score,
            "schedule_level": schedule_level,
            "match_reasons": match_reasons,
            "availability": availability_display,
        })

    suggestions.sort(key=lambda x: x["score"], reverse=True)

    return {
        "request_id": request_id,
        "subject_id": request.subject_id,
        "request_schedule": parsed.to_display() if parsed.days else request.preferred_schedule,
        "parsed_schedule": {
            "days": sorted(parsed.days),
            "start_time": str(parsed.start_time)[:5] if parsed.start_time else None,
            "end_time": str(parsed.end_time)[:5] if parsed.end_time else None,
            "has_time": parsed.has_time(),
        } if parsed.days else None,
        "suggestions": suggestions,
    }

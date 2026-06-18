from types import SimpleNamespace
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import LearningRequest, TutorAssignment
from app.repositories.repository_common import ASSIGNMENT_UPDATE_COLUMNS, LEARNING_REQUEST_UPDATE_COLUMNS, fetch_all, fetch_one, to_obj, update_by_id


def _attach_learning_request_detail(request):
    if request is not None:
        request.student = SimpleNamespace(
            student_id=request.student_id,
            full_name=getattr(request, "student_name", None),
            phone=getattr(request, "student_phone", None),
            contact_email=getattr(request, "student_email", None),
        )
        request.subject = SimpleNamespace(
            subject_id=request.subject_id,
            subject_name=getattr(request, "subject_name", None),
            grade_level=getattr(request, "subject_grade_level", None),
            subject_group=getattr(request, "subject_group", None),
        )
        if getattr(request, "assignment_id", None) is not None:
            request.assignment = SimpleNamespace(
                assignment_id=request.assignment_id,
                status=getattr(request, "assignment_status", None),
                assigned_at=getattr(request, "assignment_assigned_at", None),
                note=getattr(request, "assignment_note", None),
                staff_id=getattr(request, "assignment_staff_id", None),
                tutor_id=getattr(request, "assignment_tutor_id", None),
                class_id=getattr(request, "class_id", None),
                staff_name=getattr(request, "assignment_staff_name", None),
                tutor_name=getattr(request, "assigned_tutor_name", None),
            )
        else:
            request.assignment = None
    return request


def _attach_learning_requests_detail(requests: list):
    for request in requests:
        _attach_learning_request_detail(request)
    return requests


def get_learning_requests(
    db: Session,
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    subject: Optional[str] = None,
    status: Optional[str] = None,
) -> list[LearningRequest]:
    requests = fetch_all(
        db,
        """
        SELECT *
        FROM VW_LEARNING_REQUEST_DETAIL
        WHERE (:student_id IS NULL OR student_id = :student_id)
          AND (:subject_id IS NULL OR subject_id = :subject_id)
          AND (:status IS NULL OR status = :status)
          AND (:subject IS NULL OR subject_name LIKE :subject)
        ORDER BY request_id DESC
        """,
        {
            "student_id": student_id,
            "subject_id": subject_id,
            "status": status,
            "subject": f"%{subject}%" if subject else None,
        },
    )
    return _attach_learning_requests_detail(requests)


def get_learning_request(db: Session, request_id: int) -> Optional[LearningRequest]:
    return _attach_learning_request_detail(
        fetch_one(
            db,
            """
            SELECT *
            FROM VW_LEARNING_REQUEST_DETAIL
            WHERE request_id = :request_id
            """,
            {"request_id": request_id},
        )
    )


def create_learning_request(db: Session, request: LearningRequest) -> LearningRequest:
    row = db.execute(
        text(
            """
            INSERT INTO LEARNING_REQUEST (
                student_id,
                subject_id,
                requested_level,
                learning_goal,
                preferred_area,
                preferred_mode,
                preferred_schedule,
                expected_fee,
                status
            )
            OUTPUT
                INSERTED.request_id,
                INSERTED.student_id,
                INSERTED.subject_id,
                INSERTED.requested_level,
                INSERTED.learning_goal,
                INSERTED.preferred_area,
                INSERTED.preferred_mode,
                INSERTED.preferred_schedule,
                INSERTED.expected_fee,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :student_id,
                :subject_id,
                :requested_level,
                :learning_goal,
                :preferred_area,
                :preferred_mode,
                :preferred_schedule,
                :expected_fee,
                :status
            )
            """
        ),
        {
            "student_id": request.student_id,
            "subject_id": request.subject_id,
            "requested_level": request.requested_level,
            "learning_goal": request.learning_goal,
            "preferred_area": request.preferred_area,
            "preferred_mode": request.preferred_mode,
            "preferred_schedule": request.preferred_schedule,
            "expected_fee": request.expected_fee,
            "status": request.status,
        },
    ).mappings().first()
    return to_obj(row)


def update_learning_request(db: Session, request_id: int, data: dict) -> None:
    update_by_id(db, "LEARNING_REQUEST", "request_id", request_id, data, LEARNING_REQUEST_UPDATE_COLUMNS)


def cancel_learning_request(db: Session, request_id: int) -> None:
    update_learning_request(db, request_id, {"status": "CANCELED"})


def _attach_assignment_detail(assignment):
    if assignment is not None:
        class_id = getattr(assignment, "class_id", None)
        assignment.study_class = SimpleNamespace(class_id=class_id) if class_id is not None else None
    return assignment


def _attach_assignments_detail(assignments: list):
    for assignment in assignments:
        _attach_assignment_detail(assignment)
    return assignments


def get_assignments(
    db: Session,
    request_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    status: Optional[str] = None,
) -> list[TutorAssignment]:
    assignments = fetch_all(
        db,
        """
        SELECT
            ta.assignment_id,
            ta.request_id,
            ta.tutor_id,
            ta.staff_id,
            ta.assigned_at,
            ta.status,
            ta.note,
            ta.created_at,
            ta.updated_at,
            sc.class_id
        FROM TUTOR_ASSIGNMENT ta
        LEFT JOIN STUDY_CLASS sc ON sc.assignment_id = ta.assignment_id
        WHERE (:request_id IS NULL OR ta.request_id = :request_id)
          AND (:tutor_id IS NULL OR ta.tutor_id = :tutor_id)
          AND (:status IS NULL OR ta.status = :status)
        ORDER BY ta.assignment_id DESC
        """,
        {"request_id": request_id, "tutor_id": tutor_id, "status": status},
    )
    return _attach_assignments_detail(assignments)


def get_assignment(db: Session, assignment_id: int) -> Optional[TutorAssignment]:
    return _attach_assignment_detail(
        fetch_one(
            db,
            """
            SELECT
                ta.assignment_id,
                ta.request_id,
                ta.tutor_id,
                ta.staff_id,
                ta.assigned_at,
                ta.status,
                ta.note,
                ta.created_at,
                ta.updated_at,
                sc.class_id
            FROM TUTOR_ASSIGNMENT ta
            LEFT JOIN STUDY_CLASS sc ON sc.assignment_id = ta.assignment_id
            WHERE ta.assignment_id = :assignment_id
            """,
            {"assignment_id": assignment_id},
        )
    )


def create_assignment(db: Session, assignment: TutorAssignment) -> TutorAssignment:
    row = db.execute(
        text(
            """
            INSERT INTO TUTOR_ASSIGNMENT (
                request_id,
                tutor_id,
                staff_id,
                status,
                note
            )
            OUTPUT
                INSERTED.assignment_id,
                INSERTED.request_id,
                INSERTED.tutor_id,
                INSERTED.staff_id,
                INSERTED.assigned_at,
                INSERTED.status,
                INSERTED.note,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :request_id,
                :tutor_id,
                :staff_id,
                :status,
                :note
            )
            """
        ),
        {
            "request_id": assignment.request_id,
            "tutor_id": assignment.tutor_id,
            "staff_id": assignment.staff_id,
            "status": assignment.status,
            "note": assignment.note,
        },
    ).mappings().first()
    created = to_obj(row)
    created.study_class = None
    return created


def call_assign_tutor_to_request(
    db: Session,
    request_id: int,
    tutor_id: int,
    staff_id: Optional[int] = None,
    note: Optional[str] = None,
) -> TutorAssignment:
    row = db.execute(
        text(
            """
            EXEC SP_ASSIGN_TUTOR_TO_REQUEST
                @request_id = :request_id,
                @tutor_id = :tutor_id,
                @staff_id = :staff_id,
                @note = :note
            """
        ),
        {
            "request_id": request_id,
            "tutor_id": tutor_id,
            "staff_id": staff_id,
            "note": note,
        },
    ).mappings().first()
    created = to_obj(row)
    created.study_class = None
    return created


def update_assignment(db: Session, assignment_id: int, data: dict) -> None:
    update_by_id(db, "TUTOR_ASSIGNMENT", "assignment_id", assignment_id, data, ASSIGNMENT_UPDATE_COLUMNS)


def cancel_assignment(db: Session, assignment_id: int) -> None:
    update_assignment(db, assignment_id, {"status": "CANCELED"})


def get_candidate_tutors_for_request(
    db: Session,
    subject_id: int,
    preferred_area: Optional[str] = None,
    preferred_schedule: Optional[str] = None,
    preferred_mode: Optional[str] = None,
) -> list[dict]:
    """
    Get candidate tutors for a learning request, filtered and scored.

    Matching now uses real day-of-week + time overlap:
    - schedule_level 0 = no parseable schedule info (0 pts)
    - schedule_level 1 = same day(s) match, time overlaps (3 pts)
    - schedule_level 2 = same day(s) match, full time coverage (10 pts)
    - schedule_level 3 = same day(s) match, full time + multiple days (12+ pts)
    """
    rows = fetch_all(
        db,
        f"""
        WITH TutorWorkload AS (
            SELECT
                ta.tutor_id,
                COUNT(sc.class_id) AS current_classes
            FROM TUTOR_ASSIGNMENT ta
            LEFT JOIN STUDY_CLASS sc ON sc.assignment_id = ta.assignment_id AND sc.status = 'ACTIVE'
            WHERE ta.status = 'ASSIGNED'
            GROUP BY ta.tutor_id
        ),
        RequestSubject AS (
            SELECT
                s.subject_id,
                s.subject_name AS req_name,
                s.grade_level AS req_level
            FROM SUBJECT s
            WHERE s.subject_id = :subject_id
        ),
        EquivalentSubjects AS (
            SELECT s2.subject_id
            FROM SUBJECT s2
            CROSS JOIN RequestSubject rs
            WHERE s2.status <> 'INACTIVE'
              AND (
                  s2.subject_id = rs.subject_id
                  -- exact composite key match
                  OR LOWER(LTRIM(RTRIM(ISNULL(s2.subject_name,'')))) = LOWER(LTRIM(RTRIM(rs.req_name)))
                     AND LOWER(LTRIM(RTRIM(ISNULL(s2.grade_level,'')))) = LOWER(LTRIM(RTRIM(ISNULL(rs.req_level,''))))
                  -- legacy split form (name + grade_level) vs combined form (name contains grade_level, grade_level null)
                  OR (LOWER(LTRIM(RTRIM(ISNULL(s2.subject_name,'')))) = LOWER(LTRIM(RTRIM(rs.req_name + ' ' + ISNULL(rs.req_level,''))))
                      AND ISNULL(s2.grade_level,'') = ''
                      AND ISNULL(rs.req_level,'') <> '')
                  -- combined form (name contains grade_level, grade_level null) vs legacy split form
                  OR (LOWER(LTRIM(RTRIM(ISNULL(s2.subject_name,'')))) = LOWER(LTRIM(RTRIM(rs.req_name)))
                      AND ISNULL(s2.grade_level,'') = ''
                      AND LOWER(LTRIM(RTRIM(rs.req_name))) + ' ' + LOWER(LTRIM(RTRIM(ISNULL(rs.req_level,'')))) = LOWER(LTRIM(RTRIM(s2.subject_name + ' ' + ISNULL(s2.grade_level,'')))))
              )
        )
        SELECT
            t.tutor_id,
            t.full_name,
            t.phone,
            t.area AS tutor_area,
            t.experience_years,
            t.contact_email,
            COALESCE(twl.current_classes, 0) AS current_classes,
            10 AS max_classes,
            CASE WHEN t.area = :preferred_area THEN 1 ELSE 0 END AS area_match,
            CASE
                WHEN :preferred_mode IS NULL THEN 1
                WHEN EXISTS (
                    SELECT 1 FROM TUTOR_AVAILABILITY ta2
                    WHERE ta2.tutor_id = t.tutor_id
                      AND ta2.status = 'AVAILABLE'
                      AND ta2.teaching_mode IN ('BOTH', :preferred_mode)
                ) THEN 1
                ELSE 0
            END AS mode_match
        FROM TUTOR t
        INNER JOIN TUTOR_CAPABILITY tc ON tc.tutor_id = t.tutor_id
        INNER JOIN EquivalentSubjects es ON es.subject_id = tc.subject_id
        LEFT JOIN TutorWorkload twl ON twl.tutor_id = t.tutor_id
        WHERE t.status = 'ACTIVE'
          AND COALESCE(twl.current_classes, 0) < 10
          AND NOT EXISTS (
              SELECT 1 FROM TUTOR_ASSIGNMENT ta
              WHERE ta.tutor_id = t.tutor_id
                AND ta.status = 'ASSIGNED'
                AND EXISTS (
                    SELECT 1 FROM STUDY_CLASS sc
                    WHERE sc.assignment_id = ta.assignment_id
                      AND sc.status = 'ACTIVE'
                )
          )
        """,
        {
            "subject_id": subject_id,
            "preferred_area": preferred_area,
            "preferred_schedule": preferred_schedule,
            "preferred_mode": preferred_mode,
        },
    )
    return rows

from datetime import date
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import ClassSchedule, LessonSession, StudyClass
from app.repositories.repository_common import (
    CLASS_UPDATE_COLUMNS,
    SCHEDULE_UPDATE_COLUMNS,
    SESSION_UPDATE_COLUMNS,
    fetch_all,
    fetch_one,
    to_obj,
    update_by_id,
)


def _time_text(value) -> str:
    return value.strftime("%H:%M") if hasattr(value, "strftime") else str(value)


def _class_schedule_display(db: Session, class_id: int) -> Optional[str]:
    schedules = fetch_all(
        db,
        """
        SELECT day_of_week, start_time
        FROM CLASS_SCHEDULE
        WHERE class_id = :class_id
          AND status = 'ACTIVE'
        ORDER BY day_of_week ASC, start_time ASC
        """,
        {"class_id": class_id},
    )
    if not schedules:
        return None
    labels = {1: "T2", 2: "T3", 3: "T4", 4: "T5", 5: "T6", 6: "T7", 7: "CN"}
    return ", ".join(f"{labels.get(item.day_of_week, item.day_of_week)} - {_time_text(item.start_time)}" for item in schedules)


def _class_next_lesson(db: Session, class_id: int):
    row = fetch_one(
        db,
        """
        SELECT MIN(lesson_date) AS next_lesson
        FROM LESSON_SESSION
        WHERE class_id = :class_id
          AND status = 'SCHEDULED'
          AND lesson_date >= CAST(GETDATE() AS DATE)
        """,
        {"class_id": class_id},
    )
    return row.next_lesson if row else None


def _attach_class_display(db: Session, study_class):
    if study_class is not None:
        study_class.status = getattr(study_class, "class_status", getattr(study_class, "status", None))
        study_class.created_at = getattr(study_class, "class_created_at", getattr(study_class, "created_at", None))
        study_class.schedule_display = _class_schedule_display(db, study_class.class_id)
        study_class.next_lesson = _class_next_lesson(db, study_class.class_id)
    return study_class


def _attach_classes_display(db: Session, classes: list):
    for study_class in classes:
        _attach_class_display(db, study_class)
    return classes


def get_classes(
    db: Session,
    search: Optional[str] = None,
    student_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    status: Optional[str] = None,
) -> list[StudyClass]:
    classes = fetch_all(
        db,
        """
        SELECT
            class_id,
            class_code,
            tuition_fee_per_session,
            teaching_mode,
            location,
            start_date,
            end_date,
            class_status,
            class_created_at,
            assignment_id,
            assignment_status,
            assigned_at,
            request_id,
            requested_level,
            learning_goal,
            preferred_area,
            preferred_mode,
            preferred_schedule,
            student_id,
            student_name,
            student_phone,
            tutor_id,
            tutor_name,
            tutor_phone,
            subject_id,
            subject_name,
            subject_grade_level,
            staff_id,
            staff_name
        FROM VW_STUDY_CLASS_DETAIL
        WHERE (:student_id IS NULL OR student_id = :student_id)
          AND (:tutor_id IS NULL OR tutor_id = :tutor_id)
          AND (:subject_id IS NULL OR subject_id = :subject_id)
          AND (:status IS NULL OR class_status = :status)
          AND (
              :search IS NULL
              OR class_code LIKE :search
              OR student_name LIKE :search
              OR tutor_name LIKE :search
              OR subject_name LIKE :search
          )
        ORDER BY class_id DESC
        """,
        {
            "search": f"%{search}%" if search else None,
            "student_id": student_id,
            "tutor_id": tutor_id,
            "subject_id": subject_id,
            "status": status,
        },
    )
    return _attach_classes_display(db, classes)


def get_class(db: Session, class_id: int) -> Optional[StudyClass]:
    return _attach_class_display(
        db,
        fetch_one(
            db,
            """
            SELECT
                class_id,
                class_code,
                tuition_fee_per_session,
                teaching_mode,
                location,
                start_date,
                end_date,
                class_status,
                class_created_at,
                assignment_id,
                assignment_status,
                assigned_at,
                request_id,
                requested_level,
                learning_goal,
                preferred_area,
                preferred_mode,
                preferred_schedule,
                student_id,
                student_name,
                student_phone,
                tutor_id,
                tutor_name,
                tutor_phone,
                subject_id,
                subject_name,
                subject_grade_level,
                staff_id,
                staff_name
            FROM VW_STUDY_CLASS_DETAIL
            WHERE class_id = :class_id
            """,
            {"class_id": class_id},
        )
    )


def create_class(db: Session, study_class: StudyClass) -> StudyClass:
    row = db.execute(
        text(
            """
            INSERT INTO STUDY_CLASS (
                assignment_id,
                class_code,
                tuition_fee_per_session,
                teaching_mode,
                location,
                start_date,
                end_date,
                status
            )
            OUTPUT
                INSERTED.class_id,
                INSERTED.assignment_id,
                INSERTED.class_code,
                INSERTED.tuition_fee_per_session,
                INSERTED.teaching_mode,
                INSERTED.location,
                INSERTED.start_date,
                INSERTED.end_date,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :assignment_id,
                :class_code,
                :tuition_fee_per_session,
                :teaching_mode,
                :location,
                :start_date,
                :end_date,
                :status
            )
            """
        ),
        {
            "assignment_id": study_class.assignment_id,
            "class_code": study_class.class_code,
            "tuition_fee_per_session": study_class.tuition_fee_per_session,
            "teaching_mode": study_class.teaching_mode,
            "location": study_class.location,
            "start_date": study_class.start_date,
            "end_date": study_class.end_date,
            "status": study_class.status,
        },
    ).mappings().first()
    return to_obj(row)


def call_create_class_from_assignment(
    db: Session,
    assignment_id: int,
    class_code: str,
    tuition_fee_per_session,
    teaching_mode: str,
    location: Optional[str],
    start_date: date,
    end_date: Optional[date],
    status: str,
) -> StudyClass:
    row = db.execute(
        text(
            """
            EXEC SP_CREATE_CLASS_FROM_ASSIGNMENT
                @assignment_id = :assignment_id,
                @class_code = :class_code,
                @tuition_fee_per_session = :tuition_fee_per_session,
                @teaching_mode = :teaching_mode,
                @location = :location,
                @start_date = :start_date,
                @end_date = :end_date,
                @status = :status
            """
        ),
        {
            "assignment_id": assignment_id,
            "class_code": class_code,
            "tuition_fee_per_session": tuition_fee_per_session,
            "teaching_mode": teaching_mode,
            "location": location,
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
        },
    ).mappings().first()
    return to_obj(row)


def update_class(db: Session, class_id: int, data: dict) -> None:
    update_by_id(db, "STUDY_CLASS", "class_id", class_id, data, CLASS_UPDATE_COLUMNS)


def cancel_class(db: Session, class_id: int) -> None:
    update_class(db, class_id, {"status": "CANCELED"})


def get_class_invoice_snapshot(db: Session, class_id: int, period_start: date, period_end: date) -> dict:
    row = fetch_one(
        db,
        """
        SELECT
            sc.class_id,
            COUNT(ls.session_id) AS completed_sessions,
            sc.tuition_fee_per_session,
            sc.tuition_fee_per_session * COUNT(ls.session_id) AS amount_due
        FROM STUDY_CLASS sc
        LEFT JOIN LESSON_SESSION ls
            ON ls.class_id = sc.class_id
           AND ls.status = 'COMPLETED'
           AND ls.lesson_date BETWEEN :period_start AND :period_end
        WHERE sc.class_id = :class_id
        GROUP BY sc.class_id, sc.tuition_fee_per_session
        """,
        {"class_id": class_id, "period_start": period_start, "period_end": period_end},
    )
    return {
        "completed_sessions": row.completed_sessions if row else 0,
        "tuition_fee_per_session": row.tuition_fee_per_session if row else 0,
        "amount_due": row.amount_due if row else 0,
    }


def get_class_tuition_summary(db: Session, class_id: int):
    return fetch_one(
        db,
        """
        SELECT *
        FROM dbo.FN_CLASS_TUITION_SUMMARY(:class_id)
        """,
        {"class_id": class_id},
    )


def get_schedules(
    db: Session,
    class_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    student_id: Optional[int] = None,
) -> list[ClassSchedule]:
    return fetch_all(
        db,
        """
        SELECT
            cs.schedule_id,
            cs.class_id,
            cs.day_of_week,
            cs.start_time,
            cs.end_time,
            cs.effective_from,
            cs.effective_to,
            cs.status,
            cs.note,
            cs.created_at,
            cs.updated_at
        FROM CLASS_SCHEDULE cs
        JOIN STUDY_CLASS sc ON sc.class_id = cs.class_id
        JOIN TUTOR_ASSIGNMENT ta ON ta.assignment_id = sc.assignment_id
        JOIN LEARNING_REQUEST lr ON lr.request_id = ta.request_id
        WHERE (:class_id IS NULL OR cs.class_id = :class_id)
          AND (:tutor_id IS NULL OR ta.tutor_id = :tutor_id)
          AND (:student_id IS NULL OR lr.student_id = :student_id)
        ORDER BY cs.schedule_id DESC
        """,
        {"class_id": class_id, "tutor_id": tutor_id, "student_id": student_id},
    )


def get_schedule(db: Session, schedule_id: int) -> Optional[ClassSchedule]:
    return fetch_one(
        db,
        """
        SELECT
            schedule_id,
            class_id,
            day_of_week,
            start_time,
            end_time,
            effective_from,
            effective_to,
            status,
            note,
            created_at,
            updated_at
        FROM CLASS_SCHEDULE
        WHERE schedule_id = :schedule_id
        """,
        {"schedule_id": schedule_id},
    )


def create_schedule(db: Session, schedule: ClassSchedule) -> ClassSchedule:
    row = db.execute(
        text(
            """
            INSERT INTO CLASS_SCHEDULE (
                class_id,
                day_of_week,
                start_time,
                end_time,
                effective_from,
                effective_to,
                status,
                note
            )
            OUTPUT
                INSERTED.schedule_id,
                INSERTED.class_id,
                INSERTED.day_of_week,
                INSERTED.start_time,
                INSERTED.end_time,
                INSERTED.effective_from,
                INSERTED.effective_to,
                INSERTED.status,
                INSERTED.note,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :class_id,
                :day_of_week,
                :start_time,
                :end_time,
                :effective_from,
                :effective_to,
                :status,
                :note
            )
            """
        ),
        {
            "class_id": schedule.class_id,
            "day_of_week": schedule.day_of_week,
            "start_time": schedule.start_time,
            "end_time": schedule.end_time,
            "effective_from": schedule.effective_from,
            "effective_to": schedule.effective_to,
            "status": schedule.status,
            "note": schedule.note,
        },
    ).mappings().first()
    return to_obj(row)


def update_schedule(db: Session, schedule_id: int, data: dict) -> None:
    update_by_id(db, "CLASS_SCHEDULE", "schedule_id", schedule_id, data, SCHEDULE_UPDATE_COLUMNS)


def deactivate_schedule(db: Session, schedule_id: int) -> None:
    update_schedule(db, schedule_id, {"status": "INACTIVE"})


def get_sessions(
    db: Session,
    class_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    lesson_date: Optional[date] = None,
) -> list[LessonSession]:
    return fetch_all(
        db,
        """
        SELECT *
        FROM VW_LESSON_SESSION_DETAIL
        WHERE (:class_id IS NULL OR class_id = :class_id)
          AND (:tutor_id IS NULL OR tutor_id = :tutor_id)
          AND (:student_id IS NULL OR student_id = :student_id)
          AND (:status IS NULL OR status = :status)
          AND (:lesson_date IS NULL OR lesson_date = :lesson_date)
        ORDER BY lesson_date DESC, session_id DESC
        """,
        {
            "class_id": class_id,
            "tutor_id": tutor_id,
            "student_id": student_id,
            "status": status,
            "lesson_date": lesson_date,
        },
    )


def get_session(db: Session, session_id: int) -> Optional[LessonSession]:
    return fetch_one(
        db,
        """
        SELECT *
        FROM VW_LESSON_SESSION_DETAIL
        WHERE session_id = :session_id
        """,
        {"session_id": session_id},
    )


def create_session(db: Session, session: LessonSession) -> LessonSession:
    row = db.execute(
        text(
            """
            INSERT INTO LESSON_SESSION (
                class_id,
                schedule_id,
                session_number,
                lesson_date,
                start_time,
                end_time,
                status,
                content_note
            )
            OUTPUT
                INSERTED.session_id,
                INSERTED.class_id,
                INSERTED.schedule_id,
                INSERTED.session_number,
                INSERTED.lesson_date,
                INSERTED.start_time,
                INSERTED.end_time,
                INSERTED.status,
                INSERTED.content_note,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :class_id,
                :schedule_id,
                :session_number,
                :lesson_date,
                :start_time,
                :end_time,
                :status,
                :content_note
            )
            """
        ),
        {
            "class_id": session.class_id,
            "schedule_id": session.schedule_id,
            "session_number": session.session_number,
            "lesson_date": session.lesson_date,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "status": session.status,
            "content_note": session.content_note,
        },
    ).mappings().first()
    return to_obj(row)


def update_session(db: Session, session_id: int, data: dict) -> None:
    update_by_id(db, "LESSON_SESSION", "session_id", session_id, data, SESSION_UPDATE_COLUMNS)


def cancel_session(db: Session, session_id: int) -> None:
    update_session(db, session_id, {"status": "CANCELED"})

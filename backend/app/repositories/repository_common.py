from datetime import datetime
from types import SimpleNamespace
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


def to_obj(row):
    if row is None:
        return None
    return SimpleNamespace(**dict(row))


def to_list(rows):
    return [to_obj(row) for row in rows]


def fetch_one(db: Session, sql: str, params: Optional[dict] = None):
    row = db.execute(text(sql), params or {}).mappings().first()
    return to_obj(row)


def fetch_all(db: Session, sql: str, params: Optional[dict] = None):
    rows = db.execute(text(sql), params or {}).mappings().all()
    return to_list(rows)


def execute(db: Session, sql: str, params: Optional[dict] = None):
    return db.execute(text(sql), params or {})


def update_by_id(db: Session, table: str, id_column: str, id_value, data: dict, allowed_columns: set[str]) -> None:
    clean = {
        key: value
        for key, value in data.items()
        if key in allowed_columns and key != "updated_at"
    }
    if not clean:
        return

    assignments = ", ".join([f"{column} = :{column}" for column in clean])
    execute(
        db,
        f"""
        UPDATE {table}
        SET {assignments},
            updated_at = SYSUTCDATETIME()
        WHERE {id_column} = :id_value
        """,
        {**clean, "id_value": id_value},
    )


STUDENT_UPDATE_COLUMNS = {"full_name", "phone", "contact_email", "address", "area", "current_level", "grade_level", "status"}
TUTOR_UPDATE_COLUMNS = {"full_name", "phone", "contact_email", "university", "major", "experience_years", "area", "status"}
SUBJECT_UPDATE_COLUMNS = {"subject_name", "subject_group", "grade_level", "description", "status"}
TUTOR_CAPABILITY_UPDATE_COLUMNS = {"teaching_level", "years_experience", "note"}
TUTOR_AVAILABILITY_UPDATE_COLUMNS = {"day_of_week", "start_time", "end_time", "teaching_mode", "area", "status"}
LEARNING_REQUEST_UPDATE_COLUMNS = {
    "subject_id",
    "requested_level",
    "learning_goal",
    "preferred_area",
    "preferred_mode",
    "preferred_schedule",
    "expected_fee",
    "status",
}
ASSIGNMENT_UPDATE_COLUMNS = {"tutor_id", "staff_id", "status", "note"}
CLASS_UPDATE_COLUMNS = {
    "tuition_fee_per_session",
    "teaching_mode",
    "location",
    "start_date",
    "end_date",
    "status",
}
SCHEDULE_UPDATE_COLUMNS = {
    "day_of_week",
    "start_time",
    "end_time",
    "effective_from",
    "effective_to",
    "status",
    "note",
}
SESSION_UPDATE_COLUMNS = {
    "schedule_id",
    "session_number",
    "lesson_date",
    "start_time",
    "end_time",
    "status",
    "content_note",
}
INVOICE_UPDATE_COLUMNS = {
    "period_start",
    "period_end",
    "completed_sessions",
    "tuition_fee_per_session",
    "amount_due",
    "amount_paid",
    "status",
}
PAYMENT_UPDATE_COLUMNS = {
    "staff_id",
    "payment_date",
    "amount_paid",
    "payment_method",
    "note",
    "status",
}


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


def commit(db: Session):
    db.commit()

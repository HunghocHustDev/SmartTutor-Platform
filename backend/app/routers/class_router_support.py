from fastapi import HTTPException

from app.core.auth import CurrentActor


def ensure_staff_student_or_tutor(actor: CurrentActor, detail: str) -> None:
    if actor.role in {"staff", "student", "tutor"}:
        return
    raise HTTPException(status_code=403, detail=detail)


def apply_class_actor_filters(actor: CurrentActor, student_id: int | None, tutor_id: int | None) -> tuple[int | None, int | None]:
    if actor.role == "student":
        return actor.student_id, tutor_id
    if actor.role == "tutor":
        return student_id, actor.tutor_id
    return student_id, tutor_id

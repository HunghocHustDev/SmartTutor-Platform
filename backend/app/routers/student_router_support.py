from fastapi import HTTPException

from app.core.auth import CurrentActor


def ensure_student_or_staff(actor: CurrentActor, student_id: int, detail: str) -> None:
    if actor.role == "staff":
        return
    if actor.role == "student" and actor.student_id == student_id:
        return
    raise HTTPException(status_code=403, detail=detail)

from fastapi import HTTPException

from app.core.auth import CurrentActor
from app.schemas.entities import TutorAssignmentCreate, TutorAssignmentUpdate


def ensure_staff_or_student_learning_request_list(actor: CurrentActor) -> None:
    if actor.role in {"staff", "student"}:
        return
    raise HTTPException(status_code=403, detail="Only staff or the owning student can view learning requests")


def ensure_learning_request_create_owner(actor: CurrentActor, student_id: int) -> None:
    if actor.role != "student" or actor.student_id is None or student_id != actor.student_id:
        raise HTTPException(status_code=403, detail="Students can only create their own learning requests")


def apply_assignment_staff(payload: TutorAssignmentCreate | TutorAssignmentUpdate, actor: CurrentActor):
    if payload.staff_id is None and actor.staff_id is not None:
        return payload.model_copy(update={"staff_id": actor.staff_id})
    return payload

from fastapi import HTTPException

from app.core.auth import CurrentActor


def ensure_tutor_or_staff(actor: CurrentActor, tutor_id: int) -> None:
    if actor.role == "staff":
        return
    if actor.role == "tutor" and actor.tutor_id == tutor_id:
        return
    raise HTTPException(status_code=403, detail="Only staff or the owning tutor can access this data")

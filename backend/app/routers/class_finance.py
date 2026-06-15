from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, ensure_class_access, get_current_actor
from app.database import get_db
from app.schemas.entities import TuitionSummaryResponse
from app.services import business_service as service


router = APIRouter()


@router.get("/{class_id}/tuition-summary", response_model=TuitionSummaryResponse)
def get_class_tuition_summary(
    class_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    study_class = service.get_class_or_404(db, class_id)
    ensure_class_access(actor, study_class)
    return service.tuition_summary(db, class_id)

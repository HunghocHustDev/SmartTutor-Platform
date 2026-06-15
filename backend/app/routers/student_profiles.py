from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import DetailMessage, StudentCreate, StudentResponse, StudentUpdate
from app.services import business_service as service

from app.routers.student_router_support import ensure_student_or_staff


router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[StudentResponse])
def get_students(
    search: Optional[str] = None,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    area: Optional[str] = None,
    status: Optional[str] = None,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    if actor.role == "student":
        return [service.student_to_response(service.get_student_or_404(db, actor.student_id))]
    if actor.role != "staff":
        raise HTTPException(status_code=403, detail="Only staff or the owning student can view student profiles")
    return service.list_students(db, search=search, name=name, phone=phone, email=email, area=area, status=status)


@router.post("", response_model=StudentResponse)
def create_student(
    payload: StudentCreate,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.create_student(db, payload)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_student_or_staff(actor, student_id, "Only staff or the owning student can access this profile")
    return service.student_to_response(service.get_student_or_404(db, student_id))


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    ensure_student_or_staff(actor, student_id, "Only staff or the owning student can update this profile")
    return service.update_student(db, student_id, payload)


@router.delete("/{student_id}", response_model=DetailMessage)
def delete_student(
    student_id: int,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.deactivate_student(db, student_id)

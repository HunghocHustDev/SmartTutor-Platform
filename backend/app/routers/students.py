from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import CurrentActor, get_current_actor, require_roles
from app.database import get_db
from app.schemas.entities import DetailMessage, LearningRequestResponse, LessonSessionResponse, StudentCreate, StudentResponse, StudentUpdate, StudyClassResponse
from app.services import business_service as service


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
    if actor.role == "student" and actor.student_id != student_id:
        raise HTTPException(status_code=403, detail="Students can only access their own profile")
    if actor.role not in {"student", "staff"}:
        raise HTTPException(status_code=403, detail="Only staff or the owning student can access this profile")
    return service.student_to_response(service.get_student_or_404(db, student_id))


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    if actor.role == "student" and actor.student_id != student_id:
        raise HTTPException(status_code=403, detail="Students can only update their own profile")
    if actor.role not in {"student", "staff"}:
        raise HTTPException(status_code=403, detail="Only staff or the owning student can update this profile")
    return service.update_student(db, student_id, payload)


@router.delete("/{student_id}", response_model=DetailMessage)
def delete_student(
    student_id: int,
    _: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.deactivate_student(db, student_id)


@router.get("/{student_id}/learning-requests", response_model=list[LearningRequestResponse])
def get_student_learning_requests(
    student_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    if actor.role == "student" and actor.student_id != student_id:
        raise HTTPException(status_code=403, detail="Students can only access their own learning requests")
    if actor.role not in {"student", "staff"}:
        raise HTTPException(status_code=403, detail="Only staff or the owning student can access these learning requests")
    service.get_student_or_404(db, student_id)
    return service.list_learning_requests(db, student_id=student_id)


@router.get("/{student_id}/classes", response_model=list[StudyClassResponse])
def get_student_classes(
    student_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    if actor.role == "student" and actor.student_id != student_id:
        raise HTTPException(status_code=403, detail="Students can only access their own classes")
    if actor.role not in {"student", "staff"}:
        raise HTTPException(status_code=403, detail="Only staff or the owning student can access these classes")
    service.get_student_or_404(db, student_id)
    return service.list_classes(db, student_id=student_id)


@router.get("/{student_id}/schedule", response_model=list[LessonSessionResponse])
def get_student_schedule(
    student_id: int,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    if actor.role == "student" and actor.student_id != student_id:
        raise HTTPException(status_code=403, detail="Students can only access their own schedule")
    if actor.role not in {"student", "staff"}:
        raise HTTPException(status_code=403, detail="Only staff or the owning student can access this schedule")
    service.get_student_or_404(db, student_id)
    return service.list_sessions(db, student_id=student_id)

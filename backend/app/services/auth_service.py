from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Student, Tutor, UserAccount
from app.repositories import data_repository as repo
from app.schemas.entities import LoginRequest, RegisterRequest
from app.services.common import _hash_password


def authenticate(db: Session, payload: LoginRequest) -> dict:
    account = repo.get_user_by_email(db, payload.email)
    if not account or account.password_hash != _hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    normalized_role = "STAFF" if account.role == "ADMIN" else account.role
    role = normalized_role.lower()
    profile_id = account.account_id
    name = account.username
    area = None
    level = None
    university = None
    major = None
    experience = None
    position = None
    if account.role == "STUDENT":
        student = repo.get_student_by_account_id(db, account.account_id)
        if student:
            profile_id = student.student_id
            name = student.full_name
            area = student.area
            level = student.current_level or student.grade_level
    elif account.role == "TUTOR":
        tutor = repo.get_tutor_by_account_id(db, account.account_id)
        if tutor:
            profile_id = tutor.tutor_id
            name = tutor.full_name
            area = tutor.area
            university = tutor.university
            major = tutor.major
            experience = tutor.experience_years
    elif normalized_role == "STAFF":
        staff = repo.get_staff_by_account_id(db, account.account_id)
        if staff:
            profile_id = staff.staff_id
            name = staff.full_name
            area = staff.position
            position = staff.position

    token = f"dev-token-{account.account_id}"
    return {
        "user": {
            "id": profile_id,
            "name": name,
            "role": role,
            "email": account.email,
            "area": area,
            "level": level,
            "university": university,
            "major": major,
            "experience": experience,
            "position": position,
        },
        "token": token,
        "access_token": token,
        "token_type": "bearer",
    }


def register(db: Session, payload: RegisterRequest) -> dict:
    if repo.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Email already exists")

    username = payload.username or payload.email.split("@")[0]
    if repo.get_user_by_username(db, username):
        raise HTTPException(status_code=409, detail="Username already exists")

    full_name = payload.full_name or payload.fullName
    if not full_name:
        raise HTTPException(status_code=400, detail="full_name is required")

    role = payload.role.upper()
    if role not in {"STUDENT", "TUTOR"}:
        raise HTTPException(status_code=400, detail="Public registration only supports STUDENT or TUTOR")

    if role == "STUDENT":
        if not payload.area:
            raise HTTPException(status_code=400, detail="area is required for student registration")
        if not payload.level:
            raise HTTPException(status_code=400, detail="level is required for student registration")
    if role == "TUTOR":
        if not payload.area:
            raise HTTPException(status_code=400, detail="area is required for tutor registration")
        if not payload.university:
            raise HTTPException(status_code=400, detail="university is required for tutor registration")
        if not payload.major:
            raise HTTPException(status_code=400, detail="major is required for tutor registration")
        if payload.experience is not None and payload.experience < 0:
            raise HTTPException(status_code=400, detail="experience must be greater than or equal to zero")

    account = repo.create_user(
        db,
        UserAccount(
            email=payload.email,
            username=username,
            password_hash=_hash_password(payload.password),
            role=role,
            status="ACTIVE",
        ),
    )

    if role == "TUTOR":
        profile = repo.create_tutor(
            db,
            Tutor(
                account_id=account.account_id,
                full_name=full_name,
                phone=payload.phone,
                contact_email=payload.email,
                university=payload.university,
                major=payload.major,
                area=payload.area,
                experience_years=payload.experience or 0,
                status="ACTIVE",
            ),
        )
        profile_id = profile.tutor_id
    else:
        profile = repo.create_student(
            db,
            Student(
                account_id=account.account_id,
                full_name=full_name,
                phone=payload.phone,
                contact_email=payload.email,
                area=payload.area,
                current_level=payload.level,
                grade_level=payload.level,
                status="ACTIVE",
            ),
        )
        profile_id = profile.student_id

    repo.commit(db)
    return {
        "id": profile_id,
        "name": full_name,
        "full_name": full_name,
        "email": payload.email,
        "phone": payload.phone,
        "role": role.lower(),
        "status": "ACTIVE",
        "area": payload.area,
        "level": payload.level,
        "university": payload.university,
        "major": payload.major,
        "experience": payload.experience if role == "TUTOR" else None,
    }

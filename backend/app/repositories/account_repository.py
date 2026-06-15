from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import Staff, UserAccount
from app.repositories.repository_common import fetch_one, to_obj


def get_user_by_email(db: Session, email: str) -> Optional[UserAccount]:
    return fetch_one(
        db,
        """
        SELECT account_id, email, username, password_hash, role, status, created_at, updated_at
        FROM USER_ACCOUNT
        WHERE email = :email
        """,
        {"email": email},
    )


def get_user_by_username(db: Session, username: str) -> Optional[UserAccount]:
    return fetch_one(
        db,
        """
        SELECT account_id, email, username, password_hash, role, status, created_at, updated_at
        FROM USER_ACCOUNT
        WHERE username = :username
        """,
        {"username": username},
    )


def get_user_by_id(db: Session, account_id: int) -> Optional[UserAccount]:
    return fetch_one(
        db,
        """
        SELECT account_id, email, username, password_hash, role, status, created_at, updated_at
        FROM USER_ACCOUNT
        WHERE account_id = :account_id
        """,
        {"account_id": account_id},
    )


def create_user(db: Session, user: UserAccount) -> UserAccount:
    row = db.execute(
        text(
            """
            INSERT INTO USER_ACCOUNT (
                email,
                username,
                password_hash,
                role,
                status
            )
            OUTPUT
                INSERTED.account_id,
                INSERTED.email,
                INSERTED.username,
                INSERTED.password_hash,
                INSERTED.role,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :email,
                :username,
                :password_hash,
                :role,
                :status
            )
            """
        ),
        {
            "email": user.email,
            "username": user.username,
            "password_hash": user.password_hash,
            "role": user.role,
            "status": user.status,
        },
    ).mappings().first()
    return to_obj(row)


def get_staff(db: Session, staff_id: int) -> Optional[Staff]:
    return fetch_one(
        db,
        """
        SELECT staff_id, account_id, full_name, phone, contact_email, position, status, created_at, updated_at
        FROM STAFF
        WHERE staff_id = :staff_id
        """,
        {"staff_id": staff_id},
    )


def get_staff_by_account_id(db: Session, account_id: int) -> Optional[Staff]:
    return fetch_one(
        db,
        """
        SELECT staff_id, account_id, full_name, phone, contact_email, position, status, created_at, updated_at
        FROM STAFF
        WHERE account_id = :account_id
        """,
        {"account_id": account_id},
    )


def create_staff(db: Session, staff: Staff) -> Staff:
    row = db.execute(
        text(
            """
            INSERT INTO STAFF (
                account_id,
                full_name,
                phone,
                contact_email,
                position,
                status
            )
            OUTPUT
                INSERTED.staff_id,
                INSERTED.account_id,
                INSERTED.full_name,
                INSERTED.phone,
                INSERTED.contact_email,
                INSERTED.position,
                INSERTED.status,
                INSERTED.created_at,
                INSERTED.updated_at
            VALUES (
                :account_id,
                :full_name,
                :phone,
                :contact_email,
                :position,
                :status
            )
            """
        ),
        {
            "account_id": staff.account_id,
            "full_name": staff.full_name,
            "phone": staff.phone,
            "contact_email": staff.contact_email,
            "position": staff.position,
            "status": staff.status,
        },
    ).mappings().first()
    return to_obj(row)

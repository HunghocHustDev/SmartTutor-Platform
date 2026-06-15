from sqlalchemy.orm import Session

from app.repositories import data_repository as repo


def dashboard_summary(db: Session) -> dict:
    summary = repo.get_dashboard_summary(db)
    return {
        "total_students": summary.total_students,
        "total_tutors": summary.total_tutors,
        "pending_learning_requests": summary.pending_learning_requests,
        "active_classes": summary.active_classes,
        "completed_sessions": summary.completed_sessions,
        "unpaid_invoices": summary.unpaid_invoices,
        "partially_paid_invoices": summary.partially_paid_invoices,
        "successful_payments": summary.successful_payments,
    }

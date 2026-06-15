from sqlalchemy.orm import Session

from app.repositories.repository_common import fetch_one


def get_dashboard_summary(db: Session):
    return fetch_one(
        db,
        """
        SELECT
            (SELECT COUNT(*) FROM STUDENT) AS total_students,
            (SELECT COUNT(*) FROM TUTOR) AS total_tutors,
            (SELECT COUNT(*) FROM LEARNING_REQUEST WHERE status = 'PENDING') AS pending_learning_requests,
            (SELECT COUNT(*) FROM STUDY_CLASS WHERE status = 'ACTIVE') AS active_classes,
            (SELECT COUNT(*) FROM LESSON_SESSION WHERE status = 'COMPLETED') AS completed_sessions,
            (SELECT COUNT(*) FROM TUITION_INVOICE WHERE status = 'UNPAID') AS unpaid_invoices,
            (SELECT COUNT(*) FROM TUITION_INVOICE WHERE status = 'PARTIALLY_PAID') AS partially_paid_invoices,
            (SELECT COUNT(*) FROM TUITION_PAYMENT WHERE status = 'SUCCESS') AS successful_payments
        """
    )

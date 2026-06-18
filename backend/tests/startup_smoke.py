"""
Lightweight startup/import smoke check for the FastAPI backend.

Run from the backend directory:
    uv run python -m tests.startup_smoke

This catches FastAPI router bootstrap issues early, before running full HTTP tests.
"""
import os
import sys

# Ensure the backend root is on the Python path
_backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)


def check_imports():
    """Verify all top-level modules import cleanly."""
    print("Checking module imports...")
    try:
        import app.main  # noqa: F401
        print("  app.main: OK")
    except Exception as exc:
        print(f"  app.main: FAILED - {exc}")
        raise

    try:
        from app import routers  # noqa: F401
        print("  app.routers: OK")
    except Exception as exc:
        print(f"  app.routers: FAILED - {exc}")
        raise

    try:
        from app import services  # noqa: F401
        print("  app.services: OK")
    except Exception as exc:
        print(f"  app.services: FAILED - {exc}")
        raise

    try:
        from app import repositories  # noqa: F401
        print("  app.repositories: OK")
    except Exception as exc:
        print(f"  app.repositories: FAILED - {exc}")
        raise


def check_router_includes():
    """Verify main.py router includes resolve without circular imports."""
    print("Checking router includes in app.main...")
    from app.main import app
    included_routes = [r.path for r in app.routes if hasattr(r, "path")]
    print(f"  Total routes registered: {len(included_routes)}")
    key_paths = ["/", "/health", "/docs", "/openapi.json"]
    for path in key_paths:
        if path in included_routes:
            print(f"  {path}: present")
        else:
            print(f"  {path}: MISSING")
    return True


def check_service_facade():
    """Verify service facade still re-exports all expected functions."""
    print("Checking service facade exports...")
    from app.services import business_service as service

    expected = [
        "authenticate",
        "register_user",
        "get_students",
        "get_student",
        "create_student",
        "update_student",
        "deactivate_student",
        "get_subjects",
        "get_subject",
        "create_subject",
        "update_subject",
        "deactivate_subject",
        "get_tutors",
        "get_tutor",
        "create_tutor",
        "update_tutor",
        "deactivate_tutor",
        "get_learning_requests",
        "get_learning_request",
        "create_learning_request",
        "update_learning_request",
        "cancel_learning_request",
        "get_assignments",
        "get_assignment",
        "create_assignment",
        "update_assignment",
        "cancel_assignment",
        "get_study_classes",
        "get_study_class",
        "create_study_class",
        "update_study_class",
        "cancel_study_class",
        "get_tuition_summary",
        "get_schedules",
        "get_schedule",
        "create_schedule",
        "update_schedule",
        "deactivate_schedule",
        "get_sessions",
        "get_session",
        "create_session",
        "update_session",
        "cancel_session",
        "update_session_status",
        "get_invoices",
        "get_invoice",
        "create_invoice",
        "update_invoice",
        "cancel_invoice",
        "get_payments",
        "get_payment",
        "create_payment",
        "update_payment",
        "cancel_payment",
        "get_dashboard_summary",
    ]

    missing = []
    for name in expected:
        if not hasattr(service, name):
            missing.append(name)
    if missing:
        print(f"  MISSING exports: {missing}")
        raise AssertionError(f"Service facade missing: {missing}")
    print(f"  All {len(expected)} expected exports present")


def check_repository_facade():
    """Verify repository facade still re-exports all expected functions."""
    print("Checking repository facade exports...")
    from app.repositories import data_repository as repo

    expected = [
        "fetch_one",
        "fetch_all",
        "execute",
        "create_user",
        "get_staff",
        "create_staff",
        "get_students",
        "get_student",
        "create_student",
        "update_student",
        "deactivate_student",
        "get_subjects",
        "get_subject",
        "get_subject_by_name_level",
        "create_subject",
        "update_subject",
        "deactivate_subject",
        "get_tutors",
        "get_tutor",
        "create_tutor",
        "update_tutor",
        "deactivate_tutor",
        "get_tutor_capabilities",
        "get_tutor_capability",
        "create_tutor_capability",
        "update_tutor_capability",
        "delete_tutor_capability",
        "get_tutor_availabilities",
        "get_tutor_availability",
        "create_tutor_availability",
        "update_tutor_availability",
        "delete_tutor_availability",
        "get_learning_requests",
        "get_learning_request",
        "create_learning_request",
        "update_learning_request",
        "cancel_learning_request",
        "get_assignments",
        "get_assignment",
        "create_assignment",
        "update_assignment",
        "cancel_assignment",
        "get_study_classes",
        "get_study_class",
        "create_study_class",
        "update_study_class",
        "cancel_study_class",
        "get_tuition_summary",
        "get_schedules",
        "get_schedule",
        "create_schedule",
        "update_schedule",
        "deactivate_schedule",
        "get_sessions",
        "get_session",
        "create_session",
        "update_session",
        "cancel_session",
        "get_invoices",
        "get_invoice",
        "get_invoice_by_class_period",
        "create_invoice",
        "update_invoice",
        "cancel_invoice",
        "get_payments",
        "get_payment",
        "create_payment",
        "update_payment",
        "cancel_payment",
        "get_dashboard_summary",
    ]

    missing = []
    for name in expected:
        if not hasattr(repo, name):
            missing.append(name)
    if missing:
        print(f"  MISSING exports: {missing}")
        raise AssertionError(f"Repository facade missing: {missing}")
    print(f"  All {len(expected)} expected exports present")


def main():
    print("=" * 60)
    print("Backend Startup/Import Smoke Check")
    print("=" * 60)

    check_imports()
    check_router_includes()
    check_service_facade()
    check_repository_facade()

    print("=" * 60)
    print("All startup smoke checks PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()

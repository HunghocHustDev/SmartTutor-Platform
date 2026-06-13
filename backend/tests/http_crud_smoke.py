import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta


def request(method: str, base_url: str, path: str, payload=None, expected_status: int = 200):
    url = f"{base_url.rstrip('/')}{path}"
    headers = {"Content-Type": "application/json"}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            parsed = json.loads(body) if body else None
            if response.status != expected_status:
                raise AssertionError(f"{method} {path} expected {expected_status}, got {response.status}: {parsed}")
            return parsed
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        parsed = json.loads(body) if body else None
        if exc.code != expected_status:
            raise AssertionError(f"{method} {path} expected {expected_status}, got {exc.code}: {parsed}") from exc
        return parsed


def assert_equal(actual, expected, label: str):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_true(condition: bool, label: str):
    if not condition:
        raise AssertionError(label)


def contains_id(items: list[dict], expected_id: int) -> bool:
    return any(item.get("id") == expected_id for item in items)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args()

    suffix = date.today().strftime("%Y%m%d")
    token = f"{suffix}-{abs(hash(args.base_url)) % 1000000}"
    today = date.today()
    next_week = today + timedelta(days=7)
    period_end = today + timedelta(days=30)

    results: list[tuple[str, str]] = []

    register_payload = {
        "username": f"http-smoke-{token}",
        "full_name": f"HTTP Smoke Student {token}",
        "email": f"http-smoke-{token}@example.com",
        "phone": f"09{str(abs(hash(token)) % 100000000):0>8}",
        "password": "SmokePass123!",
        "role": "student",
    }
    registered = request("POST", args.base_url, "/auth/register", register_payload)
    assert_equal(registered["role"], "student", "register role")
    logged_in = request(
        "POST",
        args.base_url,
        "/auth/login",
        {"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert_equal(logged_in["user"]["email"], register_payload["email"], "login email")
    assert_true(bool(logged_in["access_token"]), "login access_token should be present")
    results.append(("auth", "PASS"))

    subject = request(
        "POST",
        args.base_url,
        "/subjects",
        {
            "name": f"HTTP Subject {token}",
            "level": "Lop 12",
            "subject_group": "STEM",
            "description": "HTTP CRUD smoke subject",
            "status": "ACTIVE",
        },
    )
    subject_id = subject["id"]
    assert_true(contains_id(request("GET", args.base_url, "/subjects"), subject_id), "subject list should include created row")
    subject_detail = request("GET", args.base_url, f"/subjects/{subject_id}")
    assert_equal(subject_detail["id"], subject_id, "subject detail id")
    subject_updated = request(
        "PUT",
        args.base_url,
        f"/subjects/{subject_id}",
        {"description": "HTTP CRUD smoke subject updated", "status": "ACTIVE"},
    )
    assert_equal(subject_updated["description"], "HTTP CRUD smoke subject updated", "subject update description")
    results.append(("subjects", "PASS"))

    student = request(
        "POST",
        args.base_url,
        "/students",
        {
            "full_name": f"HTTP Student {token}",
            "phone": f"08{str(abs(hash(token + '-student')) % 100000000):0>8}",
            "email": f"http-student-{token}@example.com",
            "area": "Thu Duc",
            "level": "12",
            "status": "ACTIVE",
        },
    )
    student_id = student["id"]
    assert_true(contains_id(request("GET", args.base_url, "/students"), student_id), "student list should include created row")
    student_detail = request("GET", args.base_url, f"/students/{student_id}")
    assert_equal(student_detail["id"], student_id, "student detail id")
    student_updated = request(
        "PUT",
        args.base_url,
        f"/students/{student_id}",
        {"area": "Go Vap", "status": "ACTIVE"},
    )
    assert_equal(student_updated["area"], "Go Vap", "student update area")
    results.append(("students", "PASS"))

    tutor = request(
        "POST",
        args.base_url,
        "/tutors",
        {
            "full_name": f"HTTP Tutor {token}",
            "phone": f"07{str(abs(hash(token + '-tutor')) % 100000000):0>8}",
            "email": f"http-tutor-{token}@example.com",
            "area": "Binh Thanh",
            "subjects": "",
            "experience": 3,
            "status": "ACTIVE",
        },
    )
    tutor_id = tutor["id"]
    assert_true(contains_id(request("GET", args.base_url, "/tutors"), tutor_id), "tutor list should include created row")
    tutor_detail = request("GET", args.base_url, f"/tutors/{tutor_id}")
    assert_equal(tutor_detail["id"], tutor_id, "tutor detail id")
    tutor_updated = request(
        "PUT",
        args.base_url,
        f"/tutors/{tutor_id}",
        {"area": "Phu Nhuan", "experience": 4, "status": "ACTIVE"},
    )
    assert_equal(tutor_updated["area"], "Phu Nhuan", "tutor update area")
    results.append(("tutors", "PASS"))

    capability = request(
        "POST",
        args.base_url,
        f"/tutors/{tutor_id}/capabilities",
        {
            "subject_id": subject_id,
            "teaching_level": "ADVANCED",
            "years_experience": 4,
            "note": "HTTP smoke capability",
        },
    )
    capability_id = capability["capability_id"]
    capabilities = request("GET", args.base_url, f"/tutors/{tutor_id}/capabilities")
    assert_true(any(item.get("capability_id") == capability_id for item in capabilities), "capability list should include created row")
    results.append(("tutor_capabilities", "PASS"))

    availability = request(
        "POST",
        args.base_url,
        f"/tutors/{tutor_id}/availability",
        {
            "day_of_week": 2,
            "start_time": "18:00:00",
            "end_time": "20:00:00",
            "teaching_mode": "OFFLINE",
            "area": "Phu Nhuan",
            "status": "AVAILABLE",
        },
    )
    availability_id = availability["id"]
    availabilities = request("GET", args.base_url, f"/tutors/{tutor_id}/availability")
    assert_true(any(item.get("id") == availability_id for item in availabilities), "availability list should include created row")
    availability_updated = request(
        "PUT",
        args.base_url,
        f"/tutors/{tutor_id}/availability/{availability_id}",
        {"end_time": "20:30:00", "area": "Tan Binh", "status": "AVAILABLE"},
    )
    assert_equal(availability_updated["area"], "Tan Binh", "availability update area")
    results.append(("tutor_availability", "PASS"))

    chain_request = request(
        "POST",
        args.base_url,
        "/learning-requests",
        {
            "student_id": student_id,
            "subject_id": subject_id,
            "target": "Dat 8+",
            "requested_level": "Lop 12",
            "area": "Go Vap",
            "preferred_schedule": "T3-T5 18:00",
            "expected_fee": 150000,
            "teaching_mode": "OFFLINE",
            "learning_goal": "On thi tot nghiep",
        },
    )
    request_id = chain_request["id"]
    assert_true(contains_id(request("GET", args.base_url, "/learning-requests"), request_id), "request list should include created row")
    request_detail = request("GET", args.base_url, f"/learning-requests/{request_id}")
    assert_equal(request_detail["id"], request_id, "request detail id")
    request_updated = request(
        "PUT",
        args.base_url,
        f"/learning-requests/{request_id}",
        {"area": "Thu Duc", "teaching_mode": "BOTH", "target": "Dat 9+"},
    )
    assert_equal(request_updated["area"], "Thu Duc", "request update area")
    results.append(("learning_requests", "PASS"))

    cancel_request = request(
        "POST",
        args.base_url,
        "/learning-requests",
        {
            "student_id": student_id,
            "subject_id": subject_id,
            "target": "Test cancel request",
            "requested_level": "Lop 12",
            "area": "Binh Thanh",
            "preferred_schedule": "CN 09:00",
            "expected_fee": 120000,
            "teaching_mode": "ONLINE",
        },
    )
    cancel_request_id = cancel_request["id"]
    request("DELETE", args.base_url, f"/learning-requests/{cancel_request_id}")
    canceled_request_detail = request("GET", args.base_url, f"/learning-requests/{cancel_request_id}")
    assert_equal(canceled_request_detail["status"], "CANCELED", "request delete should soft cancel")

    assignment = request(
        "POST",
        args.base_url,
        "/assignments",
        {"request_id": request_id, "tutor_id": tutor_id, "note": "HTTP smoke assignment"},
    )
    assignment_id = assignment["id"]
    assert_true(contains_id(request("GET", args.base_url, "/assignments"), assignment_id), "assignment list should include created row")
    assignment_detail = request("GET", args.base_url, f"/assignments/{assignment_id}")
    assert_equal(assignment_detail["id"], assignment_id, "assignment detail id")
    assignment_updated = request(
        "PUT",
        args.base_url,
        f"/assignments/{assignment_id}",
        {"note": "HTTP smoke assignment updated"},
    )
    assert_equal(assignment_updated["note"], "HTTP smoke assignment updated", "assignment update note")
    results.append(("assignments", "PASS"))

    cancel_assignment_request = request(
        "POST",
        args.base_url,
        "/learning-requests",
        {
            "student_id": student_id,
            "subject_id": subject_id,
            "target": "Test cancel assignment",
            "requested_level": "Lop 12",
            "area": "Phu Nhuan",
            "preferred_schedule": "T7 08:00",
            "expected_fee": 120000,
            "teaching_mode": "OFFLINE",
        },
    )
    cancel_assignment = request(
        "POST",
        args.base_url,
        "/assignments",
        {"request_id": cancel_assignment_request["id"], "tutor_id": tutor_id, "note": "Cancel me"},
    )
    cancel_assignment_id = cancel_assignment["id"]
    request("PATCH", args.base_url, f"/assignments/{cancel_assignment_id}/cancel", {})
    canceled_assignment_detail = request("GET", args.base_url, f"/assignments/{cancel_assignment_id}")
    assert_equal(canceled_assignment_detail["status"], "CANCELED", "assignment cancel route should set CANCELED")

    study_class = request(
        "POST",
        args.base_url,
        "/classes",
        {
            "assignment_id": assignment_id,
            "tuition_fee_per_session": 150000,
            "teaching_mode": "OFFLINE",
            "location": "Go Vap",
            "start_date": str(today),
            "end_date": str(period_end),
            "status": "ACTIVE",
        },
    )
    class_id = study_class["id"]
    class_list = request("GET", args.base_url, "/classes")
    created_class = next(item for item in class_list if item.get("id") == class_id)
    assert_true(bool(created_class.get("student")), "class list should resolve student")
    assert_true(bool(created_class.get("tutor")), "class list should resolve tutor")
    assert_true(bool(created_class.get("subject")), "class list should resolve subject")
    class_detail = request("GET", args.base_url, f"/classes/{class_id}")
    assert_equal(class_detail["id"], class_id, "class detail id")
    class_updated = request(
        "PUT",
        args.base_url,
        f"/classes/{class_id}",
        {"location": "Thu Duc", "status": "ACTIVE"},
    )
    assert_equal(class_updated["location"], "Thu Duc", "class update location")
    results.append(("classes", "PASS"))

    schedule = request(
        "POST",
        args.base_url,
        "/schedules",
        {
            "class_id": class_id,
            "day_of_week": 2,
            "start_time": "18:00:00",
            "end_time": "20:00:00",
            "effective_from": str(today),
            "effective_to": str(period_end),
            "status": "ACTIVE",
            "note": "HTTP smoke schedule",
        },
    )
    schedule_id = schedule["id"]
    assert_true(contains_id(request("GET", args.base_url, "/schedules"), schedule_id), "schedule list should include created row")
    schedule_detail = request("GET", args.base_url, f"/schedules/{schedule_id}")
    assert_equal(schedule_detail["id"], schedule_id, "schedule detail id")
    schedule_updated = request(
        "PUT",
        args.base_url,
        f"/schedules/{schedule_id}",
        {"end_time": "20:30:00", "note": "HTTP smoke schedule updated", "status": "ACTIVE"},
    )
    assert_equal(schedule_updated["note"], "HTTP smoke schedule updated", "schedule update note")
    results.append(("schedules", "PASS"))

    session = request(
        "POST",
        args.base_url,
        "/sessions",
        {
            "class_id": class_id,
            "schedule_id": schedule_id,
            "session_number": 1,
            "date": str(next_week),
            "start_time": "18:00:00",
            "end_time": "20:00:00",
            "status": "SCHEDULED",
            "content_note": "HTTP smoke session",
        },
    )
    session_id = session["id"]
    assert_true(contains_id(request("GET", args.base_url, "/sessions"), session_id), "session list should include created row")
    session_detail = request("GET", args.base_url, f"/sessions/{session_id}")
    assert_equal(session_detail["id"], session_id, "session detail id")
    session_updated = request(
        "PUT",
        args.base_url,
        f"/sessions/{session_id}",
        {"content_note": "HTTP smoke session updated"},
    )
    assert_equal(session_updated["content"], "HTTP smoke session updated", "session update content")
    session_completed = request(
        "PATCH",
        args.base_url,
        f"/sessions/{session_id}/status",
        {"status": "COMPLETED", "content_note": "HTTP smoke session completed"},
    )
    assert_equal(session_completed["status"], "COMPLETED", "session status patch")
    results.append(("sessions", "PASS"))

    invoice = request(
        "POST",
        args.base_url,
        "/invoices",
        {
            "class_id": class_id,
            "period_start": str(today),
            "period_end": str(period_end),
            "completed_sessions": 1,
            "tuition_fee_per_session": 150000,
            "amount_due": 150000,
            "amount_paid": 0,
            "status": "UNPAID",
        },
    )
    invoice_id = invoice["id"]
    assert_true(contains_id(request("GET", args.base_url, "/invoices"), invoice_id), "invoice list should include created row")
    invoice_detail = request("GET", args.base_url, f"/invoices/{invoice_id}")
    assert_equal(invoice_detail["id"], invoice_id, "invoice detail id")
    invoice_updated = request(
        "PUT",
        args.base_url,
        f"/invoices/{invoice_id}",
        {"completed_sessions": 2, "amount_due": 300000, "status": "UNPAID"},
    )
    assert_equal(invoice_updated["completed_sessions"], 2, "invoice update completed_sessions")
    results.append(("invoices", "PASS"))

    payment = request(
        "POST",
        args.base_url,
        "/payments",
        {
            "invoice_id": invoice_id,
            "amount_paid": 50000,
            "payment_method": "CASH",
            "status": "SUCCESS",
            "note": "HTTP smoke payment",
        },
    )
    payment_id = payment["id"]
    assert_true(contains_id(request("GET", args.base_url, "/payments"), payment_id), "payment list should include created row")
    payment_detail = request("GET", args.base_url, f"/payments/{payment_id}")
    assert_equal(payment_detail["id"], payment_id, "payment detail id")
    payment_updated = request(
        "PUT",
        args.base_url,
        f"/payments/{payment_id}",
        {"amount_paid": 70000, "payment_method": "TRANSFER", "status": "SUCCESS"},
    )
    assert_equal(payment_updated["amount_value"], 70000.0, "payment update amount")
    results.append(("payments", "PASS"))

    request("DELETE", args.base_url, f"/payments/{payment_id}")
    deleted_payment_detail = request("GET", args.base_url, f"/payments/{payment_id}")
    assert_equal(deleted_payment_detail["status_code"], "CANCELED", "payment delete should soft cancel")

    request("DELETE", args.base_url, f"/invoices/{invoice_id}")
    deleted_invoice_detail = request("GET", args.base_url, f"/invoices/{invoice_id}")
    assert_equal(deleted_invoice_detail["status"], "CANCELED", "invoice delete should soft cancel")

    request("DELETE", args.base_url, f"/sessions/{session_id}")
    deleted_session_detail = request("GET", args.base_url, f"/sessions/{session_id}")
    assert_equal(deleted_session_detail["status"], "CANCELED", "session delete should soft cancel")

    request("DELETE", args.base_url, f"/schedules/{schedule_id}")
    deleted_schedule_detail = request("GET", args.base_url, f"/schedules/{schedule_id}")
    assert_equal(deleted_schedule_detail["status"], "INACTIVE", "schedule delete should soft deactivate")

    request("DELETE", args.base_url, f"/classes/{class_id}")
    deleted_class_detail = request("GET", args.base_url, f"/classes/{class_id}")
    assert_equal(deleted_class_detail["status"], "CANCELED", "class delete should soft cancel")

    request("DELETE", args.base_url, f"/tutors/{tutor_id}/availability/{availability_id}")
    remaining_availability = request("GET", args.base_url, f"/tutors/{tutor_id}/availability")
    assert_true(all(item.get("id") != availability_id for item in remaining_availability), "availability delete should remove row")

    request("DELETE", args.base_url, f"/tutors/{tutor_id}/capabilities/{capability_id}")
    remaining_capabilities = request("GET", args.base_url, f"/tutors/{tutor_id}/capabilities")
    assert_true(all(item.get("capability_id") != capability_id for item in remaining_capabilities), "capability delete should remove row")

    request("DELETE", args.base_url, f"/learning-requests/{request_id}")
    request_after_delete = request("GET", args.base_url, f"/learning-requests/{request_id}")
    assert_equal(request_after_delete["status"], "CANCELED", "request delete should soft cancel even after class chain")

    request("DELETE", args.base_url, f"/tutors/{tutor_id}")
    deleted_tutor_detail = request("GET", args.base_url, f"/tutors/{tutor_id}")
    assert_equal(deleted_tutor_detail["status"], "INACTIVE", "tutor delete should soft deactivate")

    request("DELETE", args.base_url, f"/students/{student_id}")
    deleted_student_detail = request("GET", args.base_url, f"/students/{student_id}")
    assert_equal(deleted_student_detail["status"], "INACTIVE", "student delete should soft deactivate")

    request("DELETE", args.base_url, f"/subjects/{subject_id}")
    deleted_subject_detail = request("GET", args.base_url, f"/subjects/{subject_id}")
    assert_equal(deleted_subject_detail["status"], "INACTIVE", "subject delete should soft deactivate")

    results.append(("delete_lifecycle", "PASS"))

    print("HTTP CRUD smoke test passed")
    for name, status in results:
        print(f"- {name}: {status}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - script-style failure path
        print(f"HTTP CRUD smoke test failed: {exc}", file=sys.stderr)
        raise

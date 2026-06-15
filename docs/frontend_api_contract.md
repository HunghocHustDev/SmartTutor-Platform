# Frontend API Contract Snapshot

This file is a frontend-oriented snapshot of the current API understanding.

Canonical contract details live in `docs/api_contract.md`.

## Current Compatibility Notes

- Class responses should keep compatibility fields like `student`, `studentId`, `tutor`, `tutorId`, `subject`, `schedule`, `fee`, `startDate`, `endDate`, `nextLesson`.
- Learning request responses should keep `target`, `area`, `teaching_mode`, `learning_goal`, and `date` compatibility fields.
- Payment responses should keep both display and code fields when possible.
- Soft delete actions should continue to use `DELETE` semantics in the frontend, even when the backend only toggles status.
- The frontend should treat mock data as fallback only, and keep it until the matching backend screen is verified.

## Known Endpoint Groups

- Health: `GET /health`
- Auth: `POST /auth/login`, `POST /auth/register`
- Dashboard: `GET /dashboard/summary`
- Students: `GET /students`, `POST /students`, `PUT /students/{id}`, `DELETE /students/{id}`, `GET /students/{id}/classes`, `GET /students/{id}/schedule`
- Tutors: `GET /tutors`, `POST /tutors`, `PUT /tutors/{id}`, `DELETE /tutors/{id}`, `GET /tutors/{id}/classes`, `GET /tutors/{id}/schedule`
- Tutor capabilities: `GET /tutors/{id}/capabilities`, `POST /tutors/{id}/capabilities`, `DELETE /tutors/{id}/capabilities/{capability_id}`
- Tutor availability: `GET /tutors/{id}/availability`, `POST /tutors/{id}/availability`, `PUT /tutors/{id}/availability/{availability_id}`, `DELETE /tutors/{id}/availability/{availability_id}`
- Subjects: `GET /subjects`, `POST /subjects`, `PUT /subjects/{id}`, `DELETE /subjects/{id}`
- Learning requests: `GET /learning-requests`, `POST /learning-requests`, `PUT /learning-requests/{id}`
- Assignments: `GET /assignments`, `POST /assignments`, `PATCH /assignments/{id}/cancel`
- Classes: `GET /classes`, `POST /classes`, `PUT /classes/{id}`, `GET /classes/{id}`, `GET /classes/{id}/tuition-summary`
- Schedules: `GET /schedules`, `POST /schedules`
- Sessions: `GET /sessions`, `POST /sessions`, `PATCH /sessions/{id}/status`
- Invoices: `GET /invoices`, `POST /invoices`
- Payments: `GET /payments`, `POST /payments`


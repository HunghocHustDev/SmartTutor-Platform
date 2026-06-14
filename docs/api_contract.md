# SmartTutor Platform - API Contract

This is a practical contract snapshot based on the current backend and frontend context.

If a field shape is not fully verified, it is marked `TODO`.

## Health

### `GET /health`

- Purpose: check backend liveness.
- Important response fields: `status`.
- TODO: exact response model beyond `{"status":"ok"}`.

## Auth

### `POST /auth/login`

- Purpose: authenticate a user.
- Important request fields: `email`, `password`.
- Important response fields: `user`, `token`, `access_token`, `token_type`.
- TODO: whether token is demo token or JWT may still be changed later.

### `POST /auth/register`

- Purpose: create a new account and profile.
- Important request fields: `email`, `phone`, `password`, `role`, `full_name` or `fullName`.
- Important response fields: `id`, `name`, `full_name`, `email`, `phone`, `role`, `status`.

## Dashboard

### `GET /dashboard/summary`

- Purpose: return high-level operational counts.
- Important response fields: `total_students`, `total_tutors`, `pending_learning_requests`.
- TODO: role-specific summary may be added later.

## Students

### `GET /students`

- Purpose: list students with search/filter.
- Important query fields: `search`, `name`, `phone`, `email`, `area`, `status`.
- Important response fields: `id`, `full_name`, `phone`, `email`, `area`, `level`, `status`.

### `POST /students`

- Purpose: create a student.
- Important request fields: `full_name`, `phone`, `email`, `area`, `level`.
- Important response fields: student object with `id`.

### `PUT /students/{id}`

- Purpose: update a student.
- Important request fields: same as create, all optional.
- Important response fields: updated student object.

### `DELETE /students/{id}`

- Purpose: soft delete a student.
- Important behavior: set status to `INACTIVE`.
- Important response fields: `detail`.

### `GET /students/{id}/classes`

- Purpose: list classes for a student.
- Important response fields: class list using class response shape.

### `GET /students/{id}/schedule`

- Purpose: list lesson sessions for a student.
- Important response fields: session list using lesson session response shape.

## Tutors

### `GET /tutors`

- Purpose: list tutors with search/filter.
- Important query fields: `search`, `name`, `phone`, `email`, `area`, `subject`, `status`.
- Important response fields: `id`, `full_name`, `phone`, `email`, `area`, `subjects`, `experience`, `status`.

### `POST /tutors`

- Purpose: create a tutor profile.
- Important request fields: `full_name`, `phone`, `email`, `area`, `subjects`, `experience`.
- Important response fields: tutor object with `id`.

### `PUT /tutors/{id}`

- Purpose: update a tutor profile.
- Important request fields: same as create, all optional.
- Important response fields: updated tutor object.

### `DELETE /tutors/{id}`

- Purpose: soft delete a tutor.
- Important behavior: set status to `INACTIVE`.

### `GET /tutors/{id}/classes`

- Purpose: list classes assigned to a tutor.
- Important response fields: class list.

### `GET /tutors/{id}/schedule`

- Purpose: list schedules for a tutor.
- Important response fields: schedule list.

## Tutor Capabilities

### `GET /tutors/{id}/capabilities`

- Purpose: list tutor subject capabilities.
- Important response fields: `capability_id`, `subject_id`, `name`, `level`, `teaching_level`, `years_experience`.

### `POST /tutors/{id}/capabilities`

- Purpose: add a capability to a tutor.
- Important request fields: `subject_id`, `teaching_level`, `years_experience`, `note`.
- Important response fields: capability object.

### `DELETE /tutors/{id}/capabilities/{capability_id}`

- Purpose: remove a capability from a tutor.
- Important response fields: `detail`.

## Tutor Availability

### `GET /tutors/{id}/availability`

- Purpose: list tutor availability slots.
- Important response fields: `id`, `tutor_id`, `day_of_week`, `start_time`, `end_time`, `teaching_mode`, `area`, `status`.

### `POST /tutors/{id}/availability`

- Purpose: add an availability slot.
- Important request fields: `day_of_week`, `start_time`, `end_time`, `teaching_mode`, `area`, `status`.
- Important response fields: availability object.

### `PUT /tutors/{id}/availability/{availability_id}`

- Purpose: update an availability slot.
- Important request fields: same as create, all optional.
- Important response fields: updated availability object.

### `DELETE /tutors/{id}/availability/{availability_id}`

- Purpose: delete an availability slot.
- Important response fields: `detail`.

## Subjects

### `GET /subjects`

- Purpose: list subjects.
- Important query fields: `status`.
- Important response fields: `id`, `name`, `level`, `subject_group`, `description`, `status`.

### `POST /subjects`

- Purpose: create a subject.
- Important request fields: `name`, `level`, `subject_group`, `description`, `status`.
- Important response fields: subject object.

### `PUT /subjects/{id}`

- Purpose: update a subject.
- Important response fields: updated subject object.

### `DELETE /subjects/{id}`

- Purpose: soft delete a subject.
- Important behavior: set status to `INACTIVE`.

## Learning Requests

### `GET /learning-requests`

- Purpose: list learning requests.
- Important query fields: `student_id`, `subject_id`, `subject`, `status`.
- Important response fields: `id`, `student_id`, `student`, `subject_id`, `subject`, `target`, `requested_level`, `area`, `preferred_schedule`, `expected_fee`, `teaching_mode`, `learning_goal`, `status`, `date`.

### `POST /learning-requests`

- Purpose: create a learning request.
- Important request fields: `student_id`, `subject_id` or `subject`, `target` or `learning_goal`, `requested_level`, `area`, `preferred_schedule`, `expected_fee`, `teaching_mode`.
- Important response fields: learning request object.

### `PUT /learning-requests/{id}`

- Purpose: update a request.
- Important response fields: updated learning request object.

## Assignments

### `GET /assignments`

- Purpose: list tutor assignments.
- Important query fields: `request_id`, `tutor_id`, `status`.
- Important response fields: `id`, `request_id`, `tutor_id`, `staff_id`, `status`, `assigned_at`, `note`.

### `POST /assignments`

- Purpose: assign a tutor to a learning request.
- Important request fields: `request_id`, `tutor_id`, `staff_id`, `note`.
- Important behavior: request must be pending, tutor must be active, tutor should have matching capability.
- Important response fields: assignment object.

### `PATCH /assignments/{id}/cancel`

- Purpose: cancel an assignment.
- Important behavior: set assignment status to `CANCELED`; `DELETE /assignments/{id}` is also exposed as cancel compatibility.

## Classes

### `GET /classes`

- Purpose: list classes.
- Important query fields: `search`, `student_id`, `tutor_id`, `subject_id`, `status`, `open_for_tutor`.
- Important response fields: `id`, `code`, `student`, `studentId`, `tutor`, `tutorId`, `subject`, `subject_id`, `level`, `schedule`, `fee`, `tuition_fee_per_session`, `teaching_mode`, `location`, `status`, `startDate`, `endDate`, `nextLesson`.

### `POST /classes`

- Purpose: create a study class.
- Important request fields: `assignment_id`, `class_code`, `tuition_fee_per_session`, `teaching_mode`, `location`, `start_date`, `end_date`, `status`.
- Important behavior: class should be created from `assignment_id`, not direct `student_id` / `tutor_id` / `subject_id`.
- Important response fields: class object.

### `PUT /classes/{id}`

- Purpose: update a class.
- Important response fields: updated class object.

### `GET /classes/{id}`

- Purpose: get class detail.
- Important response fields: class object, preferably backed by `VW_STUDY_CLASS_DETAIL`.

### `GET /classes/{id}/tuition-summary`

- Purpose: realtime tuition summary.
- Important response fields: `class_id`, `completed_sessions`, `tuition_fee_per_session`, `total_fee`, `paid_amount`, `remaining_amount`.
- Important behavior: compute from current sessions and successful payments, not from a stale manual snapshot.

## Schedules

### `GET /schedules`

- Purpose: list schedules.
- Important query fields: `class_id`, `tutor_id`, `student_id`.
- Important response fields: schedule object list.

### `POST /schedules`

- Purpose: create a class schedule.
- Important request fields: `class_id`, `day_of_week`, `start_time`, `end_time`, `effective_from`, `effective_to`, `status`, `note`.
- Important behavior: `day_of_week` must be `1..7` and `start_time` must be earlier than `end_time`.
- Important response fields: schedule object.

## Sessions

### `GET /sessions`

- Purpose: list lesson sessions.
- Important query fields: `class_id`, `tutor_id`, `student_id`, `status`, `date`.
- Important response fields: `id`, `class_id`, `schedule_id`, `session_number`, `date`, `class`, `content`, `attendance`, `status`.

### `POST /sessions`

- Purpose: create a lesson session.
- Important request fields: `class_id`, `schedule_id`, `session_number`, `lesson_date` or `session_date` or `date`, `start_time`, `end_time`, `status`, `content_note`.
- Important response fields: session object.

### `PATCH /sessions/{id}/status`

- Purpose: update session status and notes.
- Important request fields: `status`, `content_note`.
- Important response fields: updated session object.

### `DELETE /sessions/{id}`

- Purpose: cancel a lesson session.
- Important behavior: soft cancel by setting `status = CANCELED`.

## Invoices

### `GET /invoices`

- Purpose: list tuition invoices.
- Important query fields: `class_id`, `status`, `period` (compatibility filter over period dates).
- Important response fields: `id`, `class_id`, `period_start`, `period_end`, `completed_sessions`, `tuition_fee_per_session`, `amount_due`, `amount_paid`, `status`, `created_at`.

### `POST /invoices`

- Purpose: create a tuition invoice snapshot.
- Important request fields: `class_id`, `period_start`, `period_end`, `completed_sessions`, `tuition_fee_per_session`, `amount_due`, `amount_paid`, `status`.
- Important behavior: invoice should be treated as a snapshot for the current class period.
- Important behavior: duplicate `class_id` + `period_start` + `period_end` should return `409`.
- Important response fields: invoice object.

### `DELETE /invoices/{id}`

- Purpose: cancel a tuition invoice.
- Important behavior: soft cancel by setting `status = CANCELED`.

## Payments

### `GET /payments`

- Purpose: list tuition payments.
- Important query fields: `class_id`, `student_id`, `status`, `period` (compatibility filter over invoice period dates).
- Important response fields: `id`, `invoice_id`, `student_id`, `class_id`, `className`, `amount`, `amount_value`, `period`, `status`, `status_code`, `paid_at`, `payment_method`, `invoice_status`, `invoice_status_code`.

### `POST /payments`

- Purpose: record a payment.
- Important request fields: `invoice_id` or `class_id`, `amount_paid` or `amount`, `payment_date` or `paid_at`, `payment_method` or `method`, `staff_id`, `note`, `status`.
- Important behavior: service should validate invoice remaining amount before insert and reject overpayment with `Payment amount exceeds invoice remaining amount`.
- Important behavior: when `class_id` is provided without `invoice_id`, the service auto-creates a `TUITION_INVOICE` snapshot for `period_start`/`period_end` if one does not already exist.
- Important behavior: auto-created invoices use invoice status `UNPAID`; `status` in the payment payload is always interpreted as a `TUITION_PAYMENT` status such as `SUCCESS`, `CANCELED`, or `REFUNDED`.
- Important behavior: auto-created invoice totals are calculated from `COMPLETED` lesson sessions inside the requested period, while `/classes/{id}/tuition-summary` remains realtime for the whole class.
- Important response fields: payment object.

### `DELETE /payments/{id}`

- Purpose: cancel a payment.
- Important behavior: soft cancel by setting `status = CANCELED`.

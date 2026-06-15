# SmartTutor Platform - Project Context

## What This System Is

SmartTutor Platform is a tutor center management system for coordinating learning requests, tutor assignment, study classes, schedules, lesson sessions, invoices, and payments.

It is built around a centralized staff-driven process.

## Actors

- `Admin / Staff`
- `Student`
- `Tutor`

## Main Business Flow

```text
Student creates a learning request
-> Staff reviews the request
-> Staff assigns a tutor
-> Staff creates a study class
-> Staff creates class schedules
-> Tutor/staff updates lesson sessions
-> Staff manages tuition invoices and payments
```

## What The System Is Not

- Not a tutor marketplace
- Tutors do not apply to classes
- Students do not directly select tutors
- The center does not operate as a direct peer-to-peer marketplace

## Main Modules

- Auth
- Dashboard
- Students
- Tutors
- Subjects
- Tutor capabilities
- Tutor availability
- Learning requests
- Assignments
- Study classes
- Class schedules
- Lesson sessions
- Tuition invoices
- Tuition payments

## Data Model Reminder

The backend must follow `sql/schema.sql` as the source of truth.

The normalized class flow is:

```text
LEARNING_REQUEST -> TUTOR_ASSIGNMENT -> STUDY_CLASS
```

`STUDY_CLASS` does not store `student_id`, `tutor_id`, or `subject_id` directly.


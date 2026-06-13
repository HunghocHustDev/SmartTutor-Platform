# SmartTutor Platform - Project Completion Plan

## 1. Muc tieu tong the

Muc tieu la hoan thien project `SmartTutor-Platform` theo dung schema SQL Server `FINAL CLEAN` trong `sql/schema.sql`, chay duoc end-to-end voi:

- Frontend React/Vite trong `frontend/`
- Backend FastAPI/SQLAlchemy/pyodbc trong `backend/`
- SQL Server database `TutorCenterDB`
- Du lieu seed du de demo cac flow chinh

Nguyen tac lon nhat:

- Khong quay lai schema cu.
- Luon giu flow chuan hoa: `LEARNING_REQUEST -> TUTOR_ASSIGNMENT -> STUDY_CLASS`.
- `STUDY_CLASS` khong chua truc tiep `student_id`, `tutor_id`, `subject_id`.
- Frontend co the dung field compatibility, nhung backend model va repository phai bam schema moi.

## 2. Database Rules Bat Buoc

Can tao hoac cap nhat them `docs/database_rules.md` de ghi nho cac rule nay cho cac batch sau.

Rule can co:

- `STUDY_CLASS` chi lien ket qua `assignment_id`.
- Thong tin student/tutor/subject cua class lay bang join:
  `STUDY_CLASS -> TUTOR_ASSIGNMENT -> LEARNING_REQUEST -> STUDENT/SUBJECT`
  va `TUTOR_ASSIGNMENT -> TUTOR`.
- Co the dung view `VW_STUDY_CLASS_DETAIL` cho display/query tong hop.
- `day_of_week` dung so `1..7`, trong do `1 = Monday`, `7 = Sunday`.
- `TUTOR_ASSIGNMENT.status` chi dung `ASSIGNED` hoac `CANCELED`.
- `STUDY_CLASS.status` dung `ACTIVE`, `PAUSED`, `COMPLETED`, `CANCELED`; neu frontend gui `FINISHED` thi backend map sang `COMPLETED`.
- `LESSON_SESSION.attendance` khong phai cot DB rieng; day la field derived tu `LESSON_SESSION.status`.
- `TUITION_INVOICE` la snapshot theo ky, khong phai realtime summary.
- `/classes/{id}/tuition-summary` la realtime summary tu session/payment hien tai.
- `TUITION_PAYMENT.status = SUCCESS` moi duoc tinh vao tien da thanh toan.
- Trigger `TRG_TUITION_PAYMENT_RECALC_INVOICE` la noi cap nhat lai `TUITION_INVOICE.amount_paid` va invoice status sau payment.

## 3. Phase 1 - Backend Audit Va Smoke Test DB

Muc tieu: backend khop schema that, import duoc, chay duoc, query DB duoc.

Viec can lam:

- Doi chieu `backend/app/models/entities.py` voi `sql/schema.sql`.
- Ra soat `schemas`, `repositories`, `services`, `routers` de tim field cu con sot.
- Dam bao cac mapping compatibility dang dung dung:
  `contact_email -> email`, `learning_goal -> target`, `preferred_area -> area`, `preferred_mode -> teaching_mode`, `lesson_date -> date`.
- Kiem tra query class khong lay `student_id`, `tutor_id`, `subject_id` truc tiep tu `STUDY_CLASS`.
- Chuan hoa status input/output:
  `FINISHED -> COMPLETED`, `PARTIAL -> PARTIALLY_PAID`.
- Chay compile backend.
- Chay `sql/schema.sql` tren SQL Server.
- Khoi dong backend bang uvicorn.
- Goi `GET /health`.
- Mo Swagger `/docs`.
- Goi thu mot query DB don gian, uu tien `GET /subjects`.

Tieu chi duyet:

```powershell
python -m compileall backend\app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Va cac endpoint sau tra response thanh cong:

- `GET /`
- `GET /health`
- `GET /subjects`

## 4. Phase 1.5 - Minimal Seed Cho Smoke Test

Muc tieu: co du lieu toi thieu de test backend ngay tu dau, khong phai nhap tay qua nhieu.

Du lieu toi thieu:

- `USER_ACCOUNT`: admin, staff, student, tutor
- `STAFF`
- `STUDENT`
- `TUTOR`
- `SUBJECT`
- `TUTOR_CAPABILITY`
- `LEARNING_REQUEST`
- `TUTOR_ASSIGNMENT`
- `STUDY_CLASS`

Yeu cau:

- Password trong seed phai khop cach backend hash password.
- Giai doan demo hien tai co the dung SHA-256 nhu backend dang co.
- Neu doi sang bcrypt sau nay, seed phai doi sang bcrypt hash san.

Tieu chi duyet:

- Chay seed toi thieu khong loi FK/check constraint.
- Login duoc account demo.
- `GET /classes` tra class co student/tutor/subject dung.

## 5. Phase 2 - Chot API Contract Backend

Muc tieu: backend co du cac endpoint can thiet va response shape tuong thich frontend.

### 5.1 Health va Auth

Endpoint can co:

- `GET /`
- `GET /health`
- `POST /auth/login`
- `POST /auth/register`

Auth rule:

- Giai doan demo chi can login/register co ban.
- Token co the la demo token hoac JWT don gian.
- Khong bat buoc lam phan quyen bao mat sau trong giai doan nop mon.
- Response login nen tra ca `token` va `access_token` de frontend de dung.

### 5.2 Students, Tutors, Subjects

Endpoint can co:

- `GET /students`
- `POST /students`
- `GET /students/{id}`
- `PUT /students/{id}`
- `DELETE /students/{id}`
- `GET /tutors`
- `POST /tutors`
- `GET /tutors/{id}`
- `PUT /tutors/{id}`
- `DELETE /tutors/{id}`
- `GET /subjects`
- `POST /subjects`
- `GET /subjects/{id}`
- `PUT /subjects/{id}`
- `DELETE /subjects/{id}`

Delete rule:

- `DELETE /students/{id}` la soft delete, set `status = INACTIVE`.
- `DELETE /tutors/{id}` la soft delete, set `status = INACTIVE`.
- `DELETE /subjects/{id}` la soft delete, set `status = INACTIVE`.
- Khong hard delete entity da co lich su nghiep vu/FK.

### 5.3 Tutor Capability Va Availability

Can bo sung vi day la nen tang cho viec match tutor theo subject/area/time.

Endpoint capability:

- `GET /tutors/{id}/capabilities`
- `POST /tutors/{id}/capabilities`
- `DELETE /tutors/{id}/capabilities/{capability_id}`

Body tao capability:

```json
{
  "subject_id": 1,
  "teaching_level": "Lop 12",
  "years_experience": 5,
  "note": "Chuyen luyen thi"
}
```

Endpoint availability:

- `GET /tutors/{id}/availability`
- `POST /tutors/{id}/availability`
- `PUT /tutors/{id}/availability/{availability_id}`
- `DELETE /tutors/{id}/availability/{availability_id}`

Body tao availability:

```json
{
  "day_of_week": 1,
  "start_time": "19:00",
  "end_time": "20:30",
  "teaching_mode": "OFFLINE",
  "area": "Cau Giay",
  "status": "AVAILABLE"
}
```

Ghi chu:

- Neu backend hien co `/tutors/{id}/subjects`, co the giu compatibility.
- Nen xem `capabilities` la API canonical moi vi ten khop bang `TUTOR_CAPABILITY`.

### 5.4 Learning Requests

Endpoint can co:

- `GET /learning-requests`
- `POST /learning-requests`
- `GET /learning-requests/{id}`
- `PUT /learning-requests/{id}`
- `DELETE /learning-requests/{id}`

Logic:

- Request moi tao co status `PENDING`.
- Khi assign tutor thanh cong thi request chuyen `ASSIGNED`.
- Cancel request set status `CANCELED`.

### 5.5 Assignments

Day la endpoint bat buoc vi nam giua request va class.

Endpoint can co:

- `GET /assignments`
- `POST /assignments`
- `GET /assignments/{id}`
- `PUT /assignments/{id}`
- `DELETE /assignments/{id}` hoac `PATCH /assignments/{id}/cancel`

Body tao assignment:

```json
{
  "request_id": 1,
  "tutor_id": 1,
  "staff_id": 1,
  "note": "Phu hop lich va khu vuc"
}
```

Logic `POST /assignments`:

- Kiem tra learning request ton tai.
- Kiem tra request dang `PENDING`, tru khi nghiep vu cho phep reassign.
- Kiem tra tutor ton tai va status `ACTIVE`.
- Kiem tra tutor co capability voi subject cua request.
- Tao `TUTOR_ASSIGNMENT` status `ASSIGNED`.
- Update `LEARNING_REQUEST.status = ASSIGNED`.
- Neu request da co active assignment thi tra 409.

Cancel assignment:

- Set `TUTOR_ASSIGNMENT.status = CANCELED`.
- Neu request khong con assignment active thi co the dua request ve `PENDING` hoac giu `ASSIGNED` tuy nghiep vu; can chot khi implement.

### 5.6 Classes

Endpoint can co:

- `GET /classes`
- `POST /classes`
- `GET /classes/{id}`
- `PUT /classes/{id}`
- `DELETE /classes/{id}`
- `GET /classes/{id}/tuition-summary`

Canonical `POST /classes` body:

```json
{
  "assignment_id": 1,
  "class_code": "CLS-0001",
  "tuition_fee_per_session": 250000,
  "teaching_mode": "OFFLINE",
  "location": "Nha hoc vien - Cau Giay",
  "start_date": "2026-06-01",
  "end_date": null,
  "status": "ACTIVE"
}
```

Rule:

- `POST /classes` nen nhan `assignment_id` la chinh.
- Khong coi `request_id + tutor_id` la input canonical cua class.
- Neu frontend muon mot buoc tao lop tu request + tutor, tao endpoint rieng:
  `POST /classes/create-from-request`.

Optional endpoint gop:

```json
{
  "request_id": 1,
  "tutor_id": 1,
  "staff_id": 1,
  "class_code": "CLS-0001",
  "tuition_fee_per_session": 250000,
  "teaching_mode": "OFFLINE",
  "location": "Nha hoc vien - Cau Giay",
  "start_date": "2026-06-01"
}
```

Neu lam endpoint gop, phai ghi ro no tao ca:

- `TUTOR_ASSIGNMENT`
- `STUDY_CLASS`

Response class van can tra field frontend:

- `student`
- `studentId`
- `tutor`
- `tutorId`
- `subject`
- `subject_id`
- `schedule`
- `fee`
- `startDate`
- `endDate`
- `nextLesson`

### 5.7 Schedules Va Sessions

Endpoint schedule:

- `GET /schedules`
- `POST /schedules`
- `GET /schedules/{id}`
- `PUT /schedules/{id}`
- `DELETE /schedules/{id}`

Endpoint session:

- `GET /sessions`
- `POST /sessions`
- `GET /sessions/{id}`
- `PUT /sessions/{id}`
- `DELETE /sessions/{id}`
- `PATCH /sessions/{id}/status`

Session mapping:

- DB `lesson_date` -> API `date`.
- DB `content_note` -> API `content`.
- API `attendance` la derived field tu `status`.

Attendance/status mapping:

- `SCHEDULED -> Chua dien ra`
- `COMPLETED -> Co mat`
- `STUDENT_ABSENT -> Hoc vien vang`
- `TUTOR_ABSENT -> Gia su vang`
- `CANCELED -> Da huy`

### 5.8 Invoices Va Payments

Endpoint invoice:

- `GET /invoices`
- `POST /invoices`
- `GET /invoices/{id}`
- `PUT /invoices/{id}`
- `DELETE /invoices/{id}`

Endpoint payment:

- `GET /payments`
- `POST /payments`
- `GET /payments/{id}`
- `PUT /payments/{id}`
- `DELETE /payments/{id}`

Invoice rule:

- Invoice la snapshot theo ky.
- `completed_sessions`, `tuition_fee_per_session`, `amount_due` la gia tri tai luc tao invoice.
- Khong tu dong sua snapshot invoice moi khi session thay doi, tru khi co chuc nang regenerate/recalculate ro rang.

Payment rule:

- Backend phai check `remaining_amount` truoc khi insert payment.
- Neu payment vuot so tien con lai, tra:

```json
{
  "detail": "Payment amount exceeds invoice remaining amount"
}
```

- Khong de DB trigger/check constraint day loi 500 len frontend.
- Sau insert/update/delete payment, trigger DB cap nhat lai invoice.

## 6. Phase 3 - Full Demo Seed Data

Muc tieu: du lieu mau day du cho demo chinh thuc.

Seed can co:

- Admin account
- Staff account
- Nhieu student
- Nhieu tutor
- Nhieu subject
- Tutor capabilities
- Tutor availability
- Learning requests `PENDING`, `ASSIGNED`, `CANCELED`
- Assignments
- Study classes `ACTIVE`, `PAUSED`, `COMPLETED`
- Class schedules
- Lesson sessions `SCHEDULED`, `COMPLETED`, `STUDENT_ABSENT`
- Tuition invoices `UNPAID`, `PARTIALLY_PAID`, `PAID`
- Tuition payments `SUCCESS`, optionally `CANCELED` or `REFUNDED`

Tieu chi duyet:

- Chay `sql/schema.sql` thanh cong.
- Chay `sql/sample_data.sql` thanh cong.
- `SELECT * FROM VW_STUDY_CLASS_DETAIL` co du lieu dung.
- Login duoc account demo.
- `GET /dashboard/summary`, `GET /classes`, `GET /payments` co du lieu.

## 7. Phase 4 - Ket Noi Frontend Voi API That

Muc tieu: tung man hinh chinh chuyen sang API that, mock chi giu lam fallback trong luc dev.

Nguyen tac:

- Thay mock bang API theo tung man hinh.
- Chi xoa mock sau khi man hinh do test pass.
- Co loading state va error state toi thieu.
- Tao API client chung, vi du `frontend/src/services/api.js`.
- Base URL dung env: `VITE_API_BASE_URL=http://localhost:8000`.

Thu tu noi frontend:

1. Auth:
   - `LoginForm` -> `POST /auth/login`
   - `RegisterForm` -> `POST /auth/register`
   - `AuthContext` luu user/token tu API

2. Dashboard:
   - `DashboardPage` -> `GET /dashboard/summary`

3. Admin students:
   - List/create/update/delete -> `/students`

4. Admin tutors:
   - List/create/update/delete -> `/tutors`
   - Capabilities -> `/tutors/{id}/capabilities`
   - Availability -> `/tutors/{id}/availability`

5. Learning requests:
   - List/create/update/cancel -> `/learning-requests`

6. Assignments:
   - Assign tutor cho request -> `POST /assignments`
   - List assignment -> `GET /assignments`

7. Classes:
   - Tao class tu `assignment_id`
   - List/update/cancel class -> `/classes`

8. Schedules:
   - CRUD lich hoc -> `/schedules`

9. Sessions:
   - List/create/update status -> `/sessions`

10. Invoices/payments:
   - Invoice CRUD -> `/invoices`
   - Payment CRUD -> `/payments`
   - Summary -> `/classes/{id}/tuition-summary`

Tieu chi duyet:

- Admin dang nhap va quan ly student/tutor/request/assignment/class duoc.
- Student xem request/class/schedule/tuition duoc.
- Tutor xem class/schedule va cap nhat session status duoc neu UI co.

## 8. Phase 5 - End-To-End Test

Muc tieu: test dung luong nghiep vu trung tam gia su.

Checklist E2E:

- Login admin, student, tutor.
- Register student moi.
- Admin tao subject.
- Admin tao tutor.
- Admin gan tutor capability.
- Admin gan tutor availability.
- Student tao learning request.
- Admin xem request `PENDING`.
- Admin tao assignment qua `POST /assignments`.
- Request chuyen `ASSIGNED`.
- Admin tao class tu `assignment_id`.
- Admin tao schedule cho class.
- Admin/tutor tao session.
- Tutor/staff update session sang `COMPLETED`.
- Admin tao invoice snapshot theo ky.
- Admin ghi nhan payment.
- Invoice status doi thanh `PARTIALLY_PAID` hoac `PAID`.
- Student xem tuition/payment.
- Dashboard summary cap nhat dung.

Bug can bat:

- Loi FK khi tao class sai flow.
- Payment vuot invoice con lai.
- Class response thieu student/tutor/subject do join sai.
- Status frontend/backend map khong thong nhat.
- Mock fallback che mat loi API that.

## 9. Phase 6 - UI Polish Va Demo Readiness

Muc tieu: san sang nop/demo.

Viec can lam:

- Tao status mapping dung chung, khong de moi component map rieng.
- Status labels de xuat:
  `ACTIVE -> Dang hoat dong`
  `INACTIVE -> Ngung hoat dong`
  `PENDING -> Cho xu ly`
  `ASSIGNED -> Da phan cong`
  `COMPLETED -> Hoan thanh`
  `CANCELED -> Da huy`
  `UNPAID -> Chua thanh toan`
  `PARTIALLY_PAID -> Thanh toan mot phan`
  `PAID -> Da thanh toan`
- Them empty state cho bang rong.
- Them error state khi API loi.
- Form co validate toi thieu.
- Doi cac text/status cu nhu `FINISHED` sang `COMPLETED`.
- Xoa mock chi sau khi man hinh da test pass voi API.
- Kiem tra console frontend va network tab trong demo flow.

Tieu chi duyet:

- Frontend dev server chay duoc.
- Backend uvicorn chay duoc.
- SQL Server co schema va seed.
- Demo flow chay tron tru.
- Khong co loi blocking tren console/API.

## 10. Phase 7 - Docs Va Handoff

Muc tieu: nguoi khac clone project ve co the chay.

Docs can cap nhat:

- `README.md` root:
  - Cach cai dependency frontend/backend
  - Cach tao DB
  - Cach chay `schema.sql`
  - Cach chay `sample_data.sql`
  - Cach chay backend
  - Cach chay frontend
  - Account demo

- `backend/README.md`:
  - Env vars
  - SQL Server/ODBC driver
  - Health check
  - Swagger
  - Seed data

- `docs/frontend_api_contract.md`:
  - Cap nhat neu endpoint/response thay doi

- `docs/database_rules.md`:
  - Rule DB bat buoc cho cac lan code tiep theo

## 11. Thu Tu Lam De Xuat

Nen lam theo batch sau:

1. Backend audit + DB smoke test.
2. Minimal seed.
3. Hoan thien `/assignments`.
4. Chinh `POST /classes` ve canonical `assignment_id`.
5. Bo sung tutor capabilities API.
6. Bo sung tutor availability API.
7. Hoan thien invoice/payment validation.
8. Full demo seed.
9. Frontend API client + auth.
10. Frontend students/tutors/subjects.
11. Frontend learning requests/assignments/classes.
12. Frontend schedules/sessions.
13. Frontend invoices/payments.
14. E2E test va fix bug.
15. Polish UI va docs.

## 12. Definition Of Done

Project duoc xem la hoan thanh khi:

- Backend dung dung schema `FINAL CLEAN`.
- Khong co flow nao tao class ma bo qua `TUTOR_ASSIGNMENT`.
- `/assignments` la buoc ro rang trong flow dieu phoi.
- Tutor capability va availability co API de tao du lieu match that.
- Delete voi entity nghiep vu la soft delete.
- Invoice va payment tach ro snapshot/realtime summary.
- Payment vuot invoice remaining amount tra loi 400 de hieu.
- Frontend dung API that o cac man hinh chinh.
- Mock chi con la fallback/sample, khong chi phoi demo chinh.
- Seed data du de demo.
- `python -m compileall backend\app` pass.
- `GET /health` pass.
- Swagger `/docs` mo duoc.
- E2E flow chay duoc:
  student request -> assignment -> class -> schedule -> session -> invoice -> payment.

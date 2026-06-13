# Prompt mo chat moi cho backend

Ban la AI coding agent dang tiep tuc xay backend cho project `SmartTutor-Platform` tai workspace:

`d:\uni\2025.2\Database\SmartTutor-Platform`

Hay doc ky va coi day la context chinh xac nhat truoc khi code:

## 1. Muc tieu hien tai

- Tiep tuc xay backend FastAPI cho project web mon Database.
- Backend phai remap theo schema SQL Server `FINAL CLEAN` trong file:
  - `sql/schema.sql`
- Frontend da duoc tach rieng trong:
  - `frontend/`
- Backend da duoc khoi tao trong:
  - `backend/`
- Tai lieu phan tich frontend va API contract hien co trong:
  - `docs/frontend_analysis.md`
  - `docs/frontend_api_contract.md`

## 2. Kien truc project hien tai

- `frontend/`: React + Vite UI
- `backend/`: FastAPI + SQLAlchemy + pyodbc
- `sql/schema.sql`: schema SQL Server authoritative
- `docs/frontend_analysis.md`: phan tich frontend
- `docs/frontend_api_contract.md`: contract API uu tien tuong thich frontend
- `docs/backend_handoff_prompt.md`: file prompt nay

## 3. Nguon su that ve database

Schema chuan hien tai la `sql/schema.sql` ban `FINAL CLEAN`, khong dung schema cu nua.

Nhung diem quan trong cua schema moi:

- Flow chuan hoa:
  - `LEARNING_REQUEST -> TUTOR_ASSIGNMENT -> STUDY_CLASS`
- `STUDY_CLASS` khong luu truc tiep `student_id`, `tutor_id`, `subject_id`; phai join qua assignment/request.
- `USER_ACCOUNT` co `username`.
- `SUBJECT` co `subject_group`.
- `STUDENT`, `TUTOR`, `STAFF` dung `contact_email`.
- `TUTOR` co them `university`, `major`, status co `PAUSED`.
- `TUTOR_AVAILABILITY.day_of_week` la so `1..7`, co them `area`, `status`, `updated_at`.
- `TUTOR_CAPABILITY` co `teaching_level`.
- `LEARNING_REQUEST` dung `requested_level`, `learning_goal`, `preferred_area`, `preferred_mode`.
- `STUDY_CLASS` co `location`, status dung `COMPLETED` thay vi `FINISHED`.
- `CLASS_SCHEDULE` co `effective_from`, `effective_to`, `status`.
- `LESSON_SESSION` dung `schedule_id`, `session_number`, `lesson_date`.
- `TUITION_INVOICE` dung `period_start`, `period_end`, `amount_due`, `amount_paid`, status co `PARTIALLY_PAID`.
- `TUITION_PAYMENT` dung `staff_id`, `payment_date`, `amount_paid`, `payment_method`, `status`.
- Co trigger:
  - `TRG_TUITION_PAYMENT_RECALC_INVOICE`
- Co view:
  - `VW_STUDY_CLASS_DETAIL`

## 4. Tinh trang backend da lam

Backend da duoc remap phan lon theo schema moi:

- Models:
  - `backend/app/models/entities.py`
- Schemas:
  - `backend/app/schemas/entities.py`
- Repository:
  - `backend/app/repositories/data_repository.py`
- Service:
  - `backend/app/services/business_service.py`
- Routers:
  - `backend/app/routers/*.py`

Backend da compile pass bang:

```powershell
python -m compileall backend\app
```

Luu y: co the import runtime se can cai them `pyodbc` va ODBC Driver SQL Server.

## 5. Nguyen tac mapping API hien tai

Muc tieu la vua dung schema moi, vua giam sua frontend:

- DB `contact_email` -> API `email`
- DB `learning_goal` -> API `target` va dong thoi co the tra `learning_goal`
- DB `preferred_area` -> API `area`
- DB `preferred_mode` -> API `teaching_mode`
- DB `lesson_date` -> API `date`
- Class response van tra:
  - `student`, `studentId`, `tutor`, `tutorId`, `subject`, `schedule`, `fee`, `startDate`, `endDate`, `nextLesson`
- Payment response hien tra:
  - `amount` da format
  - `amount_value`
  - `status`/`status_code` cho payment
  - `invoice_status`/`invoice_status_code` cho invoice neu co

## 6. File nen doc truoc khi code

Hay doc toi thieu cac file nay truoc:

- `sql/schema.sql`
- `backend/README.md`
- `backend/app/models/entities.py`
- `backend/app/schemas/entities.py`
- `backend/app/repositories/data_repository.py`
- `backend/app/services/business_service.py`
- `backend/app/main.py`
- `docs/frontend_api_contract.md`

## 7. Viec uu tien tiep theo

Lam theo thu tu uu tien nay:

1. Rasoat backend voi schema `FINAL CLEAN` de tim field cu con sot.
2. Chot request/response model cho frontend su dung that.
3. Them seed/sample data hoac migration script neu can.
4. Ket noi frontend voi API that.
5. Test end-to-end cac luong:
   - auth
   - students
   - tutors
   - learning requests
   - classes
   - schedules
   - sessions
   - invoices/payments

## 8. Yeu cau cach lam viec

- Khong duoc quay lai schema cu.
- Uu tien giu compatibility voi frontend contract hien tai.
- Neu thay field frontend cu, co the mapping o service/schema thay vi sua frontend ngay.
- Truoc khi sua code, hay doc context trong repo, khong duoc doan.
- Sau moi batch sua, compile/check lai backend.

Hay bat dau bang viec doc schema va backend service/repository hien tai, sau do de xuat danh sach viec tiep theo ngan gon roi moi code.

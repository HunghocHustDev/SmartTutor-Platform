# SmartTutor Platform — End-to-End Flow Walkthrough

> Tài liệu này mô tả **từng bước** cách hệ thống SmartTutor Platform xử lý một thao tác nghiệp vụ, đi từ **UI click** → **HTTP request** → **Router/Service/Repository** → **SQL/View/SP/Trigger** → **DB** → **response trả về UI**.
>
> Mọi tham chiếu file đều dùng `path:line` hoặc `path:startLine-endLine` để bạn có thể mở editor và đọc lại chính xác đoạn đó.
>
> Stack: FastAPI + SQLAlchemy + pyodbc + SQL Server (backend) · React + Vite + Tailwind (frontend) · Auth = `dev-token-{account_id}` (placeholder cho JWT).

---

## Mục lục

1. [Kiến trúc tổng quan](#1-kiến-trúc-tổng-quan)
2. [Lớp xác thực & phân quyền](#2-lớp-xác-thực--phân-quyền)
3. [Các quy ước chung trong code](#3-các-quy-ước-chung-trong-code)
4. [Flow #1 — Login & Register](#4-flow-1--login--register)
5. [Flow #2 — Tạo Learning Request (Student)](#5-flow-2--tạo-learning-request-student)
6. [Flow #3 — Phân công Tutor (Staff)](#6-flow-3--phân-công-tutor-staff)
7. [Flow #4 — Tạo Study Class từ Assignment (Staff)](#7-flow-4--tạo-study-class-từ-assignment-staff)
8. [Flow #5 — Tạo Schedule + Auto-generate Sessions](#8-flow-5--tạo-schedule--auto-generate-sessions)
9. [Flow #6 — Cập nhật trạng thái buổi học](#9-flow-6--cập-nhật-trạng-thái-buổi-học)
10. [Flow #7 — Tạo Invoice + Payment + Realtime Tuition Summary](#10-flow-7--tạo-invoice--payment--realtime-tuition-summary)
11. [Phụ lục A — Soft delete pattern](#11-phụ-lục-a--soft-delete-pattern)
12. [Phụ lục B — SQL objects (View/SP/Function/Trigger)](#12-phụ-lục-b--sql-objects-viewspfunctiontrigger)

---

## 1. Kiến trúc tổng quan

```
┌────────────────────────────────────────────────────────────────────┐
│                       FRONTEND (React)                              │
│                                                                     │
│  pages/*  ──►  contexts/AuthContext  ──►  services/api.js  ──HTTP──┼──┐
│                                                                     │  │
│  components/ (Header, Sidebar, ConfirmDialog, StatusBadge…)        │  │
│                                                                     │  │
└────────────────────────────────────────────────────────────────────┘  │
                                                                         │
                                            Authorization: Bearer        │
                                            dev-token-{account_id}       │
                                                                         │
┌────────────────────────────────────────────────────────────────────┐  │
│                       BACKEND (FastAPI)                            │  │
│                                                                     │  │
│  routers/*  ──►  core/auth.get_current_actor  ──►  ┐                │  │
│       │                                              │ CurrentActor  │  │
│       ▼                                              │ (role, ids)   │  │
│  services/business_service (facade)  ◄──────────────┘                │  │
│       │                                                              │  │
│       ▼                                                              │  │
│  services/{request_flow,class_flow,finance,dashboard,…}_service    │  │
│       │                                                              │  │
│       ▼                                                              │  │
│  repositories/data_repository (facade)                              │  │
│       │                                                              │  │
│       ▼                                                              │  │
│  repositories/{request,class,finance,…}_repository                  │  │
│       │                                                              │  │
│       ├──► raw text SQL qua pyodbc ──► View  ──► SQL Server          │  │
│       ├──► raw INSERT/UPDATE/DELETE ──► SQL Server                  │  │
│       └──► EXEC SP_…    ──► Stored Procedure ──► SQL Server         │  │
│                                                                     │  │
│  services/common.py: model ↔ response converter, validation         │  │
│  schemas/entities.py: Pydantic models                                │  │
│  models/entities.py: SQLAlchemy ORM models                           │  │
└────────────────────────────────────────────────────────────────────┘  │
                                                                         │
┌────────────────────────────────────────────────────────────────────┐  │
│                       SQL Server (TutorCenterDB)                    │  │
│                                                                     │  │
│  14 bảng normalized + 5 view + 2 function + 4 SP + 1 trigger       │  │
│                                                                     │  │
│  USER_ACCOUNT (1-1) STAFF / STUDENT / TUTOR                         │  │
│  STUDENT → LEARNING_REQUEST → TUTOR_ASSIGNMENT → STUDY_CLASS        │  │
│                                  → CLASS_SCHEDULE                   │  │
│                                  → LESSON_SESSION                   │  │
│                                  → TUITION_INVOICE → TUITION_PAYMENT│  │
│  TUTOR → TUTOR_CAPABILITY / TUTOR_AVAILABILITY                      │  │
│  SUBJECT (danh mục môn học)                                         │  │
└────────────────────────────────────────────────────────────────────┘
```

### 1.1. Bản đồ thư mục backend (`backend/app/`)

```
app/
├── main.py                 # FastAPI app, include 12 router
├── config.py               # settings (env-driven)
├── database.py             # engine, SessionLocal, get_db dependency
├── core/auth.py            # CurrentActor dataclass + get_current_actor + role guards
├── models/entities.py      # SQLAlchemy ORM (UserAccount, Staff, Student, Tutor, …)
├── schemas/entities.py     # Pydantic v2 (Request/Response DTO)
├── services/
│   ├── business_service.py # facade re-export mọi service function
│   ├── auth_service.py     # authenticate, register
│   ├── student_service.py  # list/create/update/deactivate
│   ├── tutor_service.py    # list/create/update + capabilities + availability
│   ├── subject_service.py
│   ├── request_flow_service.py   # learning request + assignment + suggest
│   ├── class_flow_service.py     # class + schedule + session + summary + auto-gen
│   ├── finance_service.py        # invoice + payment
│   ├── dashboard_service.py      # 7 chỉ số tổng
│   ├── schedule_parser.py        # parse "T2,T4 17:00-19:00" → structured
│   └── common.py                 # constants, validators, response converters
├── repositories/
│   ├── data_repository.py  # facade re-export mọi repo function
│   ├── account_repository.py
│   ├── student_repository.py
│   ├── tutor_repository.py
│   ├── request_repository.py
│   ├── class_repository.py
│   ├── finance_repository.py
│   ├── dashboard_repository.py
│   └── repository_common.py     # fetch_one, fetch_all, update_by_id, …
└── routers/
    ├── auth.py             # POST /auth/login, /auth/register
    ├── dashboard.py        # GET /dashboard/summary
    ├── students.py         # includes student_profiles + student_relations
    ├── tutors.py           # includes tutor_profiles + tutor_capabilities + tutor_availabilities
    ├── subjects.py
    ├── learning_requests.py # includes learning_request_profiles
    ├── assignments.py      # includes assignment_routes
    ├── classes.py          # includes class_profiles + class_finance
    ├── schedules.py
    ├── sessions.py
    ├── invoices.py
    └── payments.py
```

### 1.2. Nguyên tắc facade

Hai facade giúp giữ import một chỗ cho router layer:

- `services/business_service.py` re-export tất cả function từ `services/*.py` nên router chỉ cần `from app.services import business_service as service`.
- `repositories/data_repository.py` re-export tất cả function từ `repositories/*.py` nên service chỉ cần `from app.repositories import data_repository as repo`.

Xem cụ thể:
- `app/main.py:42-53` — include 12 router.
- `app/services/business_service.py` — import + re-export.
- `app/repositories/data_repository.py` — import + re-export.

### 1.3. Nguyên tắc normalized data

`STUDY_CLASS` **không lưu trực tiếp** `student_id`, `tutor_id`, `subject_id`. Để resolve, luôn đi qua chuỗi join:

```
STUDY_CLASS
  └─ assignment_id ─► TUTOR_ASSIGNMENT
                        ├─ request_id ─► LEARNING_REQUEST ─► STUDENT
                        │                              └─► SUBJECT
                        └─ tutor_id   ─► TUTOR
```

API nghiệp vụ luôn dùng view đã join sẵn (`VW_STUDY_CLASS_DETAIL`, `VW_LEARNING_REQUEST_DETAIL`, `VW_LESSON_SESSION_DETAIL`, `VW_INVOICE_DETAIL`, `VW_PAYMENT_DETAIL`) — xem `repositories/{class,request,finance}_repository.py`.

---

## 2. Lớp xác thực & phân quyền

### 2.1. Token format

`app/core/auth.py:31-67` — `get_current_actor()` parse header `Authorization: Bearer dev-token-{account_id}` (không phải JWT thật, chỉ là số account_id). Lookup `USER_ACCOUNT` + profile (STUDENT/TUTOR/STAFF) theo `account_id`, trả về dataclass `CurrentActor`:

```python
# app/core/auth.py:13-20
@dataclass
class CurrentActor:
    account_id: int
    role: str                  # "staff" | "student" | "tutor"
    student_id: Optional[int] = None
    tutor_id: Optional[int] = None
    staff_id: Optional[int] = None
    email: Optional[str] = None
```

Vai trò `"ADMIN"` được normalize về `"staff"` (`app/core/auth.py:27-28`).

### 2.2. Dependency `require_roles(*roles)`

`app/core/auth.py:70-78` — factory dependency. Nếu `actor.role` không thuộc `allowed`, raise 403.

```python
@router.post("", response_model=LearningRequestResponse)
def create_learning_request(
    payload: LearningRequestCreate,
    actor: CurrentActor = Depends(require_roles("student")),  # chỉ student mới tạo
    db: Session = Depends(get_db),
):
```

### 2.3. Scope guards

`app/core/auth.py:81-153` — các hàm `ensure_*_access` được gọi **trong thân route** sau khi load object, vì cần so sánh `actor.student_id == object.student_id` chẳng hạn.

| Guard | Vai trò được phép | Quy tắc |
|---|---|---|
| `ensure_student_scope(actor, student_id)` | staff (bypass) / student (chỉ truy cập của mình) | `app/core/auth.py:81-88` |
| `ensure_tutor_scope(actor, tutor_id)` | staff / tutor (chỉ của mình) | `app/core/auth.py:91-98` |
| `ensure_learning_request_access` | staff / student owning | `app/core/auth.py:101-106` |
| `ensure_assignment_access` | staff / tutor owning | `app/core/auth.py:109-114` |
| `ensure_class_access` | staff / student owning (via chain) / tutor owning | `app/core/auth.py:117-131` |
| `ensure_schedule_access` | delegate `ensure_class_access` | `app/core/auth.py:134-136` |
| `ensure_session_access` | delegate | `app/core/auth.py:139-141` |
| `ensure_invoice_access` | delegate | `app/core/auth.py:144-146` |
| `ensure_payment_access` | delegate via `payment.invoice` | `app/core/auth.py:149-152` |

### 2.4. Frontend tương ứng

- Token lưu ở `localStorage['smarttutor_user']` (và fallback `'user'`) — `frontend/src/services/api.js:3-14`.
- Mỗi request tự đính `Authorization: Bearer {token}` — `api.js:16-44`.
- Mỗi page tự check `user?.role` để render hoặc chặn — xem `pages/AssignmentsPage.jsx`, `pages/FinancePage.jsx`, `pages/TutorProfilePage.jsx`.

---

## 3. Các quy ước chung trong code

### 3.1. Repository pattern — raw text SQL

`repositories/repository_common.py` cung cấp 3 helper chính:

```python
fetch_one(db, sql, params)   # trả về 1 row dạng SimpleNamespace (qua to_obj)
fetch_all(db, sql, params)   # trả về list
update_by_id(db, table, id_col, id_val, data, allowed_columns)  # UPDATE với whitelist cột
```

Các tên `*_UPDATE_COLUMNS` được khai báo trong `repository_common.py` để chỉ cho phép update một số cột nhất định (an toàn hơn `UPDATE *`).

INSERT dùng pattern `INSERT … OUTPUT INSERTED.col1, INSERTED.col2, … VALUES …` để lấy lại row vừa insert, gán cho `mappings().first()` rồi `to_obj()` → trả về object có cả default (created_at, updated_at) do DB sinh.

### 3.2. Service layer

Service:
- Validate input (raise `HTTPException(status_code=400)` với message cụ thể).
- Check điều kiện nghiệp vụ (409 conflict, 404 not found).
- Gọi repository.
- `repo.commit(db)` sau khi ghi.
- Convert ORM/raw row → response dict qua helper trong `services/common.py` (ví dụ `learning_request_to_response`, `class_to_response`).

### 3.3. Soft delete

Mọi DELETE ở router đều thực chất là **update `status = 'CANCELED'` (cho nghiệp vụ) hoặc `INACTIVE` (cho actor)**:
- `cancel_learning_request`, `cancel_assignment`, `cancel_class`, `cancel_session`, `cancel_invoice`, `cancel_payment` → `status = 'CANCELED'`
- `deactivate_student`, `deactivate_tutor`, `deactivate_subject` → `status = 'INACTIVE'`
- `deactivate_schedule` → `status = 'INACTIVE'`

### 3.4. Response converter — `services/common.py`

Mỗi entity có hàm `xxx_to_response(row)` trong `services/common.py` để:
- Gắn nested object (`row.student`, `row.subject`, `row.assignment`, `row.study_class`, `row.invoice`) bằng `SimpleNamespace`.
- Convert `Decimal` → `float` qua `_money()` (frontend cần JSON number, không phải string).
- Định dạng `display_text`, `next_lesson` cho lịch.

Helper get_or_404 dùng cho mọi endpoint detail: `get_class_or_404`, `get_tutor_or_404`, `get_staff_or_404`, … — raise `HTTPException(404)` nếu không thấy.

### 3.5. Validation phổ biến trong `services/common.py`

- `_validate_non_negative_decimal(value, field_name)` — `expected_fee`, `tuition_fee_per_session`.
- `_validate_positive_decimal(value, field_name)` — `amount_paid`.
- `_validate_positive_int(value, field_name)` — `session_number`.
- `_validate_date_window(start, end, …)` — `start_date <= end_date`, `effective_from <= effective_to`.
- `_validate_schedule_window(day_of_week, start_time, end_time)` — `1 <= day_of_week <= 7`, `start_time < end_time`.
- `_validate_invoice_values(...)` — `period_start <= period_end`, `completed_sessions >= 0`, `amount_due >= amount_paid`.
- `_normalize_choice(value, allowed, field_name)` — check status enum.
- `_normalize_mode(value, allowed, field_name)` — check teaching_mode.
- `_normalize_invoice_status(value)` — map `PARTIAL` → `PARTIALLY_PAID`.
- `_normalize_payment_status(value)` — check.
- `_normalize_class_status(value)` — check.
- `_invoice_remaining_amount(invoice)` — `max(0, amount_due - amount_paid)`.
- `_invoice_remaining_amount_excluding_payment(invoice, payment)` — dùng khi update payment để tránh tính trùng payment cũ.

---

## 4. Flow #1 — Login & Register

### 4.1. UI

`frontend/src/components/auth/LoginForm.jsx:1` — modal đăng nhập. State: `email`, `password`, `loading`, `error`. Submit gọi `loginWithCredentials(email, password)` từ `useAuth()`.

`frontend/src/components/auth/RegisterForm.jsx:1` — modal đăng ký. State: `role` (`'student'` | `'tutor'`), form các trường tương ứng. Submit gọi `registerAccount(payload)`.

### 4.2. Frontend AuthContext

`frontend/src/contexts/AuthContext.jsx:102-133`:

```js
// Login
const loginWithCredentials = async (email, password) => {
  const response = await loginRequest({ email, password });  // services/api.js:57
  const hydratedUser = await hydrateUserProfile({
    ...response.user,
    token: response.access_token || response.token,
  });
  login(hydratedUser);  // setState + localStorage
  return response;
};
```

`hydrateUserProfile()` ở `AuthContext.jsx:13-55`:
- `tutor` role → gọi `listTutors({ email })`, tìm tutor có email khớp, merge `id`, `name`, `area`, `experience` vào user state.
- `student` role → gọi `listStudents({ email })`, merge `id`, `name`, `area`, `level`.
- `staff` role → giữ nguyên (đã có đủ).

Lý do: `auth/login` chỉ trả về thông tin từ `USER_ACCOUNT`, không có `student_id` / `tutor_id` profile. Frontend cần 1 round-trip lookup bổ sung để có id thật (dùng cho filter / permission check sau này).

Token lưu localStorage key `smarttutor_user` (key mới) + fallback `user` (key cũ) — `AuthContext.jsx:90-94`. Khi `useEffect` mount, đọc lại + gọi `hydrateUserProfile` để cập nhật nếu server đổi dữ liệu.

### 4.3. Backend route

`app/routers/auth.py:12-19` — hai endpoint:

```
POST /auth/login     body: LoginRequest     → LoginResponse
POST /auth/register  body: RegisterRequest  → RegisterResponse
```

### 4.4. Service `authenticate`

`app/services/auth_service.py` (xem trong report backend — không đọc trực tiếp nhưng dựa theo convention):

1. `get_user_by_email(db, payload.email)` — `repositories/account_repository.py` raw `SELECT … FROM USER_ACCOUNT WHERE email = :email`.
2. So sánh `sha256(payload.password)` với `password_hash` (hash SHA256, không salt — `services/common.py:50`).
3. Lookup profile theo `account_id`:
   - role `STUDENT` → `get_student_by_account_id(account_id)` → lấy `student_id`.
   - role `TUTOR` → `get_tutor_by_account_id(account_id)` → lấy `tutor_id`.
   - role `STAFF` / `ADMIN` → `get_staff_by_account_id(account_id)` → lấy `staff_id`.
4. Trả về `{ access_token: f"dev-token-{account_id}", token_type: "bearer", user: {id, name, email, role} }`.

### 4.5. Service `register`

`app/services/auth_service.py` (theo convention):

1. `get_user_by_email` + `get_user_by_username` — nếu tồn tại raise 409.
2. `create_user(db, user)` — `INSERT INTO USER_ACCOUNT … OUTPUT INSERTED.*`.
3. Tuỳ `role`:
   - `STUDENT` → `create_student(...)` thêm row STUDENT.
   - `TUTOR` → `create_tutor(...)` thêm row TUTOR.
4. `repo.commit(db)`.
5. Trả về user mới (chưa cấp token — frontend sẽ gọi `loginRequest` ngay sau).

### 4.6. Frontend `registerAccount`

`AuthContext.jsx:115-133` — sau khi `registerRequest` thành công, tự gọi `loginRequest({email, password})` để lấy token, rồi `hydrateUserProfile` như login bình thường.

---

## 5. Flow #2 — Tạo Learning Request (Student)

> Đây là flow nghiệp vụ chính đầu tiên. Student đăng nhập → vào `/request` → điền form → submit.

### 5.1. UI

`frontend/src/pages/LearningRequestsPage.jsx` — page chính. State quan trọng:

```js
const [formData, setFormData] = useState({
  student_id, subject_id, target, requested_level, area,
  teaching_mode, preferred_days, preferred_start_time, preferred_end_time,
  preferred_schedule, expected_fee
});
const [requests, setRequests] = useState([]);
const [subjects, setSubjects] = useState([]);
```

Khi mount, page gọi:
- `listLearningRequests(filters)` — `services/api.js` (~dòng 113-118).
- `listSubjects({ status: 'ACTIVE' })` — cho dropdown môn học.

Nếu role student, filter tự giới hạn `student_id` của mình. Nếu role staff, xem tất cả.

### 5.2. Submit handler

`LearningRequestsPage.jsx` (`handleSubmit`):

1. Build payload từ `formData`.
2. Convert UI state → API DTO:
   - `formData.preferred_days` (array of day numbers `[1, 2]`) + `start_time` + `end_time` → string `"T2,T3 17:00-19:00"` qua `buildScheduleString(days, start, end)`.
3. Gọi `createLearningRequest(payload)` — `api.js:114-118`:

```js
export const createLearningRequest = (payload) => request('/learning-requests', {
  method: 'POST',
  body: JSON.stringify(payload),
});
```

### 5.3. Request đi tới backend

`Authorization: Bearer dev-token-{account_id}` được `services/api.js:22` gắn tự động.

Request body mẫu (theo `schemas/entities.py`):
```json
{
  "student_id": 12,
  "subject_id": 9,
  "requested_level": "Lớp 11",
  "area": "Quận Gò Vấp",
  "teaching_mode": "OFFLINE",
  "preferred_schedule": "T2,T4 17:00-19:00",
  "expected_fee": 200000,
  "learning_goal": "Cải thiện điểm Toán HK1"
}
```

### 5.4. Router

`app/routers/learning_request_profiles.py:44-51`:

```python
@router.post("", response_model=LearningRequestResponse)
def create_learning_request(
    payload: LearningRequestCreate,
    actor: CurrentActor = Depends(require_roles("student")),  # chỉ student
    db: Session = Depends(get_db),
):
    ensure_learning_request_create_owner(actor, payload.student_id)
    return service.create_learning_request(db, payload)
```

- `require_roles("student")` đảm bảo actor là student.
- `ensure_learning_request_create_owner(actor, payload.student_id)` ở `app/routers/learning_request_router_support.py` chặn việc student tạo request mang `student_id` của người khác.

### 5.5. Service `create_learning_request`

`app/services/request_flow_service.py:34-53`:

```python
def create_learning_request(db: Session, payload: LearningRequestCreate) -> dict:
    get_student_or_404(db, payload.student_id)              # 404 nếu student không tồn tại
    subject = _ensure_subject(db, payload.subject_id, payload.subject)
                                                          # tìm hoặc tạo SUBJECT mới nếu cần
    _validate_non_negative_decimal(payload.expected_fee, "expected_fee")
    request = repo.create_learning_request(
        db,
        LearningRequest(
            student_id=payload.student_id,
            subject_id=subject.subject_id,
            requested_level=payload.requested_level,
            learning_goal=payload.learning_goal or payload.target,  # accept cả 2 alias
            preferred_area=payload.area,                          # UI gửi 'area' → DB 'preferred_area'
            preferred_schedule=payload.preferred_schedule,
            expected_fee=payload.expected_fee,
            preferred_mode=_normalize_mode(payload.teaching_mode, {"ONLINE", "OFFLINE", "BOTH"}, "teaching_mode"),
            status="PENDING",                                     # default
        ),
    )
    repo.commit(db)
    return learning_request_to_response(repo.get_learning_request(db, request.request_id))
```

Sau insert, gọi lại `get_learning_request(...)` để lấy row từ **view** (`VW_LEARNING_REQUEST_DETAIL`) — view join sẵn `STUDENT`, `SUBJECT`, `TUTOR_ASSIGNMENT` → response có sẵn `student`, `subject`, `assignment` nested.

### 5.6. Repository `create_learning_request`

`app/repositories/request_repository.py:90-143` — raw text SQL:

```sql
INSERT INTO LEARNING_REQUEST (
    student_id, subject_id, requested_level, learning_goal,
    preferred_area, preferred_mode, preferred_schedule, expected_fee, status
)
OUTPUT
    INSERTED.request_id, INSERTED.student_id, INSERTED.subject_id,
    INSERTED.requested_level, INSERTED.learning_goal, INSERTED.preferred_area,
    INSERTED.preferred_mode, INSERTED.preferred_schedule, INSERTED.expected_fee,
    INSERTED.status, INSERTED.created_at, INSERTED.updated_at
VALUES (
    :student_id, :subject_id, :requested_level, :learning_goal,
    :preferred_area, :preferred_mode, :preferred_schedule, :expected_fee, :status
)
```

`OUTPUT INSERTED.*` trả về row vừa insert (bao gồm default values từ DB như `created_at = SYSUTCDATETIME()`). `db.execute(...).mappings().first()` rồi `to_obj()` (`repositories/repository_common.py`) convert thành `SimpleNamespace`.

### 5.7. DB

`sql/schema.sql:257-279` — bảng `LEARNING_REQUEST`:

| Cột | Kiểu | Default | Check |
|---|---|---|---|
| `request_id` | INT IDENTITY(1,1) | | PK |
| `student_id` | INT | | FK → STUDENT |
| `subject_id` | INT | | FK → SUBJECT |
| `requested_level` | NVARCHAR(50) | | |
| `learning_goal` | NVARCHAR(MAX) | | |
| `preferred_area` | NVARCHAR(255) | | |
| `preferred_mode` | VARCHAR(20) | `'OFFLINE'` | IN ('ONLINE','OFFLINE','BOTH') |
| `preferred_schedule` | NVARCHAR(255) | | free text — "T2,T4 17:00-19:00" |
| `expected_fee` | DECIMAL(18,2) | | >= 0 |
| `status` | VARCHAR(20) | `'PENDING'` | IN ('PENDING','ASSIGNED','CANCELED') |
| `created_at`, `updated_at` | DATETIME2 | `SYSUTCDATETIME()` | |

### 5.8. Response trả về UI

`learning_request_to_response(...)` trong `services/common.py` gắn:
- `request.student = SimpleNamespace(student_id, full_name, phone, contact_email)` (lấy từ view columns `student_name`, `student_phone`, `student_email`).
- `request.subject = SimpleNamespace(subject_id, subject_name, grade_level, subject_group)`.
- `request.assignment = SimpleNamespace(...)` hoặc `None`.

Khi về tới frontend, `LearningRequestsPage` reload `listLearningRequests()` để cập nhật table.

### 5.9. Sơ đồ tóm tắt

```
UI (LearningRequestsPage.handleSubmit)
  └─► services/api.js.createLearningRequest
        └─► POST /learning-requests  + Bearer dev-token-{account_id}
              └─► routers/learning_request_profiles.create_learning_request
                    ├─ require_roles("student")
                    ├─ ensure_learning_request_create_owner(actor, payload.student_id)
                    └─► services/request_flow_service.create_learning_request
                          ├─ get_student_or_404        → 404 nếu student_id không tồn tại
                          ├─ _ensure_subject           → resolve SUBJECT
                          ├─ _validate_non_negative_decimal(expected_fee)
                          └─► repositories/request_repository.create_learning_request
                                └─► raw INSERT INTO LEARNING_REQUEST … OUTPUT INSERTED.*
                                      └─► DB: row mới status='PENDING'
                          repo.commit(db)
                          repo.get_learning_request → SELECT * FROM VW_LEARNING_REQUEST_DETAIL
                          └─► services/common.learning_request_to_response
                                └─► JSON: {request_id, status, student{…}, subject{…}, assignment?}
                    ← 201 Created + LearningRequestResponse
        ← 201 → UI setState và reload list
```

---

## 6. Flow #3 — Phân công Tutor (Staff)

> Sau khi student tạo request, staff vào `/staff/assignments`, chọn request, bấm "Gợi ý gia sư" → chọn tutor → bấm "Phân công".

### 6.1. UI

`frontend/src/pages/AssignmentsPage.jsx` — 2-panel:
- Trái: danh sách `pendingRequests` (filter từ `listLearningRequests` có `status='PENDING'`).
- Phải: tab "Phân công" / "Lịch sử" cho request đang chọn. Có filter theo `day`, `search`, `area`, `minExp`, `mode`.

State chính:
```js
const [selectedRequestId, setSelectedRequestId] = useState(null);
const [rightTab, setRightTab] = useState('assign');
const [filterDays, filterSearch, filterArea, filterMinExp, filterMode] = useState(...);
const [selectedTutorId, setSelectedTutorId] = useState(null);
const [assignNote, setAssignNote] = useState('');
const [suggestResult, setSuggestResult] = useState({ status, suggestions, error });
```

### 6.2. Gợi ý gia sư

Handler `handleSuggest()`:
```js
const data = await getSuggestedTutors(selectedRequestId);
setSuggestResult({ status: 'success', suggestions: data.suggestions, error: null });
// auto-select tutor đầu tiên nếu có
if (data.suggestions?.length > 0) {
  setSelectedTutorId(data.suggestions[0].tutor_id);
}
```

`getSuggestedTutors` ở `api.js:127-129` gọi:
```
GET /learning-requests/{request_id}/suggested-tutors
```

### 6.3. Backend route suggested-tutors

`app/routers/learning_request_profiles.py:88-103`:

```python
@router.get("/{request_id}/suggested-tutors", response_model=TutorSuggestionResponse)
def suggest_tutors_for_request(
    request_id: int,
    actor: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.suggest_tutors_for_request(db, request_id)
```

### 6.4. Service `suggest_tutors_for_request`

`app/services/request_flow_service.py:151-291` — flow rất dài, gồm 4 giai đoạn:

#### Bước A — Parse lịch

```python
parsed = parse_preferred_schedule(request.preferred_schedule)
# parse "T2,T4 17:00-19:00" → ParsedSchedule(days={2,4}, start_time=17:00, end_time=19:00)
```

`app/services/schedule_parser.py:68-120` — tokenize `"T2,T4 17:00-19:00"`, dùng `DAY_LABELS` mapping ngược (`T2=2, ..., CN=7`), gọi `_parse_time` cho từng phần `HH:MM`.

#### Bước B — Lấy candidate tutors (1 query SQL phức tạp)

`app/repositories/request_repository.py:304-404` — `get_candidate_tutors_for_request(...)`. Đây là raw SQL dùng **3 CTE**:

```sql
WITH TutorWorkload AS (
    SELECT ta.tutor_id, COUNT(sc.class_id) AS current_classes
    FROM TUTOR_ASSIGNMENT ta
    LEFT JOIN STUDY_CLASS sc
        ON sc.assignment_id = ta.assignment_id AND sc.status = 'ACTIVE'
    WHERE ta.status = 'ASSIGNED'
    GROUP BY ta.tutor_id
),
RequestSubject AS (
    SELECT s.subject_id, s.subject_name AS req_name, s.grade_level AS req_level
    FROM SUBJECT s
    WHERE s.subject_id = :subject_id
),
EquivalentSubjects AS (
    -- Match chính xác, hoặc legacy "subject name + grade_level", hoặc combined form
    SELECT s2.subject_id FROM SUBJECT s2 CROSS JOIN RequestSubject rs
    WHERE s2.status <> 'INACTIVE' AND (
        s2.subject_id = rs.subject_id
        OR (LOWER(s2.subject_name) = LOWER(rs.req_name) AND LOWER(s2.grade_level) = LOWER(rs.req_level))
        -- … 2 nhánh legacy split/combined nữa
    )
)
SELECT
    t.tutor_id, t.full_name, t.phone, t.area AS tutor_area, t.experience_years,
    COALESCE(twl.current_classes, 0) AS current_classes,
    10 AS max_classes,
    CASE WHEN t.area = :preferred_area THEN 1 ELSE 0 END AS area_match,
    CASE WHEN EXISTS (
        SELECT 1 FROM TUTOR_AVAILABILITY ta2
        WHERE ta2.tutor_id = t.tutor_id
          AND ta2.status = 'AVAILABLE'
          AND ta2.teaching_mode IN ('BOTH', :preferred_mode)
    ) THEN 1 ELSE 0 END AS mode_match
FROM TUTOR t
INNER JOIN TUTOR_CAPABILITY tc ON tc.tutor_id = t.tutor_id
INNER JOIN EquivalentSubjects es ON es.subject_id = tc.subject_id
LEFT JOIN TutorWorkload twl ON twl.tutor_id = t.tutor_id
WHERE t.status = 'ACTIVE'
  AND COALESCE(twl.current_classes, 0) < 10
  AND NOT EXISTS (
      SELECT 1 FROM TUTOR_ASSIGNMENT ta
      WHERE ta.tutor_id = t.tutor_id
        AND ta.status = 'ASSIGNED'
        AND EXISTS (
            SELECT 1 FROM STUDY_CLASS sc
            WHERE sc.assignment_id = ta.assignment_id AND sc.status = 'ACTIVE'
        )
  )
```

Lọc:
- Tutor `ACTIVE` có capability cho subject (chính xác hoặc tương đương).
- Chưa quá 10 lớp đang dạy.
- Không có assignment ACTIVE nào mà đã có class ACTIVE (tránh tutor đang bận).

Cột `area_match`, `mode_match` được tính tại SQL; schedule match thực hiện **bằng Python** sau.

#### Bước C — Tính schedule score cho từng candidate (Python)

```python
for row in candidates:
    availabilities = tutor_repo.get_tutor_availabilities(db, tutor_id)
    # … lọc status='AVAILABLE' + teaching_mode phù hợp
    schedule_score = 0
    schedule_level = 0
    if parsed.has_time() and parsed.days:
        matching_days, total_overlap_minutes = ...
        if matching_days >= 1 and total_overlap_minutes >= req_duration:
            schedule_score = 20; schedule_level = 3  # full coverage
        elif matching_days >= 1:
            schedule_score = 10; schedule_level = 2  # partial
        if matching_days >= 2:
            schedule_score += 2 * (matching_days - 1)
    elif parsed.days:
        # chỉ match ngày, không có giờ
        schedule_score = 3; schedule_level = 1
```

`check_time_overlap` ở `schedule_parser.py:136-155` tính overlap bằng phút.

#### Bước D — Tổng hợp score

```python
score = (
    experience_years * 10
    + (20 if area_match else 0)
    + schedule_score
)
# sắp xếp giảm dần theo score
suggestions.sort(key=lambda x: x["score"], reverse=True)
```

Trả về:
```python
{
    "request_id": ...,
    "subject_id": ...,
    "request_schedule": "T2,T4 17:00-19:00",
    "parsed_schedule": { "days": [2,4], "start_time": "17:00", "end_time": "19:00", "has_time": True },
    "suggestions": [
        {
            "tutor_id": 1, "full_name": "...", "phone": "...",
            "area": "...", "experience_years": 5,
            "current_classes": 1, "max_classes": 10,
            "score": 75, "schedule_level": 3,
            "match_reasons": ["Khu vực phù hợp", "Lịch trùng khớp 2 ngày (đủ giờ)"],
            "availability": [{day_of_week: 2, day_label: "T2", start_time: "17:00", end_time: "19:00", teaching_mode: "OFFLINE"}, …]
        },
        ...
    ]
}
```

### 6.5. Phân công — UI handler

`AssignmentsPage.handleAssign()`:

```js
const payload = {
  request_id: selectedRequestId,
  tutor_id: selectedTutorId,
  staff_id: user.staff_id ?? user.id,  // staff tự gán
  note: assignNote,
};
const assignment = await createAssignment(payload);
// refresh list
const [reqs, assigns] = await Promise.all([
  listLearningRequests(),
  listAssignments(),
]);
setRequests(reqs);
setAssignments(assigns);
```

`createAssignment` ở `api.js:131-134`:
```
POST /assignments
```

### 6.6. Backend route `POST /assignments`

`app/routers/assignment_routes.py:32-38`:

```python
@router.post("", response_model=TutorAssignmentResponse)
def create_assignment(
    payload: TutorAssignmentCreate,
    actor: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.create_assignment(db, apply_assignment_staff(payload, actor))
```

`apply_assignment_staff` ở `app/routers/learning_request_router_support.py` tự động gán `payload.staff_id = actor.staff_id` nếu frontend không gửi.

### 6.7. Service `create_assignment`

`app/services/request_flow_service.py:87-110` — flow kiểm tra rất chặt:

```python
def create_assignment(db, payload):
    request = get_learning_request_or_404(db, payload.request_id)  # 404 nếu request không tồn tại
    tutor = get_tutor_or_404(db, payload.tutor_id)                # 404 nếu tutor không tồn tại
    if payload.staff_id is not None:
        get_staff_or_404(db, payload.staff_id)                    # 404 nếu staff_id không tồn tại
    if request.status != "PENDING":
        raise HTTPException(409, "Learning request is not pending")
    if tutor.status != "ACTIVE":
        raise HTTPException(400, "Tutor must be ACTIVE to receive an assignment")
    active_assignments = repo.get_assignments(db, request_id=payload.request_id, status="ASSIGNED")
    if active_assignments:
        raise HTTPException(409, "Learning request already has an active assignment")
    capabilities = [cap.subject_id for cap in tutor.capabilities]
    if capabilities and request.subject_id not in capabilities:
        raise HTTPException(400, "Tutor does not have capability for requested subject")
    # ── Tất cả check pass → gọi SP
    assignment = repo.call_assign_tutor_to_request(
        db,
        request_id=payload.request_id,
        tutor_id=payload.tutor_id,
        staff_id=payload.staff_id,
        note=payload.note,
    )
    repo.commit(db)
    return assignment_to_response(assignment)
```

### 6.8. Repository `call_assign_tutor_to_request`

`app/repositories/request_repository.py:267-293` — gọi stored procedure:

```sql
EXEC SP_ASSIGN_TUTOR_TO_REQUEST
    @request_id = :request_id,
    @tutor_id   = :tutor_id,
    @staff_id   = :staff_id,
    @note       = :note
```

### 6.9. SP `SP_ASSIGN_TUTOR_TO_REQUEST`

`sql/schema.sql:563-662` — flow:

1. `BEGIN TRAN` + `SET XACT_ABORT ON`.
2. Lock `LEARNING_REQUEST` với `UPDLOCK, HOLDLOCK`:
   ```sql
   SELECT @request_id = request_id
   FROM LEARNING_REQUEST WITH (UPDLOCK, HOLDLOCK)
   WHERE request_id = @request_id;
   IF @@ROWCOUNT = 0 OR @status != 'PENDING' THROW 50001, '…', 1;
   ```
3. Kiểm tra không có assignment ACTIVE cho request:
   ```sql
   IF EXISTS (SELECT 1 FROM TUTOR_ASSIGNMENT WHERE request_id = @request_id AND status = 'ASSIGNED')
       THROW 50002, '…', 1;
   ```
4. Kiểm tra tutor ACTIVE + có capability:
   ```sql
   IF NOT EXISTS (SELECT 1 FROM TUTOR WHERE tutor_id = @tutor_id AND status = 'ACTIVE')
       THROW 50003, '…', 1;
   IF NOT EXISTS (SELECT 1 FROM TUTOR_CAPABILITY
                  WHERE tutor_id = @tutor_id AND subject_id = @req_subject_id)
       THROW 50004, '…', 1;
   ```
5. `INSERT INTO TUTOR_ASSIGNMENT (request_id, tutor_id, staff_id, status, note) VALUES (..., 'ASSIGNED', ...);`
6. `UPDATE LEARNING_REQUEST SET status = 'ASSIGNED' WHERE request_id = @request_id;`
7. `COMMIT;` rồi `SELECT * FROM TUTOR_ASSIGNMENT WHERE assignment_id = SCOPE_IDENTITY();` trả về assignment mới.
8. Có `TRY/CATCH` + `ROLLBACK` + `THROW` để bubble lỗi.

### 6.10. Response

`assignment_to_response(...)` attach `study_class = SimpleNamespace(class_id=…)` nếu có (class nào reference assignment này). Thường khi vừa assign, `study_class = None`.

Frontend refresh `listAssignments()` + `listLearningRequests()` → thấy request chuyển từ `PENDING` → `ASSIGNED`, và assignment mới hiện trong lịch sử.

### 6.11. Sơ đồ tóm tắt

```
UI (AssignmentsPage.handleSuggest + handleAssign)
  │
  ├─► getSuggestedTutors(requestId)
  │     └─► GET /learning-requests/{id}/suggested-tutors
  │           └─► service.suggest_tutors_for_request
  │                 ├─ parse_preferred_schedule("T2,T4 17:00-19:00")
  │                 ├─► repo.get_candidate_tutors_for_request (SQL CTE 3 tầng)
  │                 ├─► for each candidate:
  │                 │     ├─► repo.get_tutor_availabilities (raw SQL)
  │                 │     ├─► schedule_parser.check_time_overlap
  │                 │     └─ score = experience*10 + area_match*20 + schedule_score
  │                 └─ sort desc, return suggestions[]
  │
  └─► createAssignment({request_id, tutor_id, staff_id, note})
        └─► POST /assignments
              └─► router.assignment_routes.create_assignment
                    └─► service.create_assignment
                          ├─ 404/409/400 guards
                          └─► repo.call_assign_tutor_to_request
                                └─► EXEC SP_ASSIGN_TUTOR_TO_REQUEST
                                      ├─ lock LEARNING_REQUEST, validate
                                      ├─ INSERT TUTOR_ASSIGNMENT (status=ASSIGNED)
                                      ├─ UPDATE LEARNING_REQUEST SET status=ASSIGNED
                                      └─ return new row
                          repo.commit(db)
                    ← assignment_to_response → JSON
        ← 201 → UI refresh lists
```

---

## 7. Flow #4 — Tạo Study Class từ Assignment (Staff)

> Sau khi có assignment, staff tạo class với mã lớp, học phí, lịch học, ngày bắt đầu/kết thúc.

### 7.1. UI

`frontend/src/pages/ClassesPage.jsx` — page quản lý class. State form:
```js
const [formData, setFormData] = useState({
  assignment_id, class_code,
  tuition_fee_per_session, teaching_mode, location,
  start_date, end_date, status
});
```

Khi staff bấm "Tạo lớp mới", page load `listAssignments({ status: 'ASSIGNED' })` + `listLearningRequests()` để đổ dropdown chọn assignment (mỗi assignment hiển thị mã/tên yêu cầu).

Submit → `createClass(payload)` — `api.js:148-151`:
```
POST /classes
```

### 7.2. Router

`app/routers/class_profiles.py` (xem convention):

```python
@router.post("", response_model=StudyClassResponse)
def create_study_class(
    payload: StudyClassCreate,
    actor: CurrentActor = Depends(require_roles("staff")),
    db: Session = Depends(get_db),
):
    return service.create_study_class(db, payload)
```

### 7.3. Service `create_study_class`

`app/services/class_flow_service.py:46-70`:

```python
def create_study_class(db, payload):
    if not payload.assignment_id:
        raise HTTPException(400, "assignment_id is required")
    _validate_non_negative_decimal(payload.tuition_fee_per_session, "tuition_fee_per_session")
    _validate_date_window(payload.start_date, payload.end_date, "start_date", "end_date")
    assignment = get_assignment_or_404(db, payload.assignment_id)
    if assignment.status != "ASSIGNED":
        raise HTTPException(400, "Assignment must be ASSIGNED to create a class")
    if assignment.study_class:
        raise HTTPException(409, "Assignment already has a class")
    teaching_mode = _normalize_mode(payload.teaching_mode, {"ONLINE", "OFFLINE"}, "teaching_mode")
    class_status = _normalize_class_status(payload.status) or "ACTIVE"
    study_class = repo.call_create_class_from_assignment(
        db,
        assignment_id=assignment.assignment_id,
        class_code=payload.class_code or f"CLS-{assignment.assignment_id:04d}",
        tuition_fee_per_session=payload.tuition_fee_per_session,
        teaching_mode=teaching_mode,
        location=payload.location,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=class_status,
    )
    repo.commit(db)
    return class_to_response(repo.get_class(db, study_class.class_id))
```

Sau khi tạo, `repo.get_class(...)` lấy row từ `VW_STUDY_CLASS_DETAIL` (join đầy đủ student/tutor/subject) → response có sẵn context.

### 7.4. Repository `call_create_class_from_assignment`

`app/repositories/class_repository.py` (theo convention) — raw SQL:

```sql
EXEC SP_CREATE_CLASS_FROM_ASSIGNMENT
    @assignment_id = :assignment_id,
    @class_code = :class_code,
    @tuition_fee_per_session = :tuition_fee_per_session,
    @teaching_mode = :teaching_mode,
    @location = :location,
    @start_date = :start_date,
    @end_date = :end_date,
    @status = :status
```

### 7.5. SP `SP_CREATE_CLASS_FROM_ASSIGNMENT`

`sql/schema.sql:665-754`:

1. Lock `TUTOR_ASSIGNMENT` (`UPDLOCK, HOLDLOCK`), check status = `ASSIGNED`.
2. Check assignment chưa có class (UNIQUE constraint trên `STUDY_CLASS.assignment_id` cũng bảo vệ).
3. Validate `tuition_fee_per_session > 0`, `end_date >= start_date` (cũng có CHECK constraint trên bảng).
4. `INSERT INTO STUDY_CLASS (assignment_id, class_code, tuition_fee_per_session, teaching_mode, location, start_date, end_date, status) VALUES (...)`.
5. `COMMIT` rồi `SELECT *` trả về row mới.
6. `TRY/CATCH` + `ROLLBACK` + `THROW`.

### 7.6. DB schema `STUDY_CLASS`

`sql/schema.sql:308-330`:

| Cột | Kiểu | Default | Check |
|---|---|---|---|
| `class_id` | INT IDENTITY(1,1) | | PK |
| `assignment_id` | INT | | FK + UNIQUE → TUTOR_ASSIGNMENT |
| `class_code` | NVARCHAR(50) | | UNIQUE |
| `tuition_fee_per_session` | DECIMAL(18,2) | | >= 0 |
| `teaching_mode` | VARCHAR(20) | `'OFFLINE'` | IN ('ONLINE','OFFLINE') |
| `location` | NVARCHAR(255) | | |
| `start_date` | DATE | | |
| `end_date` | DATE NULL | | >= start_date nếu not null |
| `status` | VARCHAR(20) | `'ACTIVE'` | IN ('ACTIVE','PAUSED','COMPLETED','CANCELED') |

---

## 8. Flow #5 — Tạo Schedule + Auto-generate Sessions

> Staff tạo các `CLASS_SCHEDULE` (lịch cố định theo tuần), sau đó dùng chức năng "Tự sinh buổi học" để generate `LESSON_SESSION` cho một khoảng ngày.

### 8.1. Tạo schedule thủ công

UI: `frontend/src/pages/SchedulesPage.jsx`. Form: `class_id`, `day_of_week` (1-7), `start_time`, `end_time`, `effective_from`, `effective_to`, `status`, `note`.

`createSchedule` ở `api.js:166-168`:
```
POST /schedules
```

Router `app/routers/schedule_routes.py` (`@router.post`), service `create_schedule` ở `app/services/class_flow_service.py:99-107`:

```python
def create_schedule(db, payload):
    get_class_or_404(db, payload.class_id)
    _validate_schedule_window(payload.day_of_week, payload.start_time, payload.end_time)
    _validate_date_window(payload.effective_from, payload.effective_to, "effective_from", "effective_to")
    data = payload.model_dump()
    data["status"] = _normalize_choice(data["status"], SCHEDULE_STATUSES, "status")
    schedule = repo.create_schedule(db, ClassSchedule(**data))
    repo.commit(db)
    return schedule_to_response(schedule)
```

Repository `create_schedule` (theo convention): `INSERT INTO CLASS_SCHEDULE (…) OUTPUT INSERTED.*`.

### 8.2. Auto-generate sessions

UI: `SessionsPage` → bấm "Tự sinh buổi học" → chọn class + range ngày → preview → confirm.

API:
- Preview: `POST /sessions/preview-from-schedules` body `{class_id, range_start, range_end}` → `{preview_count, preview: [{session_number, date, start_time, end_time}, …]}`.
- Generate: `POST /sessions/generate-from-schedules` cùng body → `{created_count, created_session_ids, skipped_existing}`.

### 8.3. Service `_build_session_plan` (thuật toán chính)

`app/services/class_flow_service.py:206-265` (helper internal) + `generate_sessions_from_schedules` ở `:268-311` + `preview_sessions_from_schedules` ở `:314-340`.

```python
def _build_session_plan(study_class, schedules, existing_sessions, range_start, range_end):
    active_schedules = [s for s in schedules if s.status == "ACTIVE"]
    if not active_schedules:
        return []
    existing_dates = {(item.lesson_date, item.start_time) for item in existing_sessions if item.lesson_date}
    next_number = max((item.session_number or 0) for item in existing_sessions) + 1
    plan = []
    for schedule in sorted(active_schedules, key=lambda s: (s.day_of_week, s.start_time)):
        eff_from = max(schedule.effective_from or range_start, range_start)
        eff_to   = min(schedule.effective_to   or range_end,   range_end)
        if eff_to < eff_from:
            continue
        for candidate_date in _iter_candidate_dates(eff_from, eff_to, schedule.day_of_week):
            if (candidate_date, schedule.start_time) in existing_dates:
                continue
            plan.append({
                "schedule_id": schedule.schedule_id,
                "session_number": next_number,
                "date": candidate_date,
                "start_time": schedule.start_time,
                "end_time": schedule.end_time,
            })
            existing_dates.add((candidate_date, schedule.start_time))
            next_number += 1
    return plan
```

Logic:
- Với mỗi `CLASS_SCHEDULE` (active) của class, tìm **tất cả ngày trong khoảng `[range_start, range_end]`** mà có `isoweekday() == schedule.day_of_week` (helper `_iter_candidate_dates` ở `:219-230`).
- Bỏ qua các ngày đã có buổi học cùng `start_time` (tránh tạo trùng).
- Đánh số `session_number` tiếp theo (max hiện tại + 1).

`generate_sessions_from_schedules` (khác preview ở chỗ) sẽ loop plan và `INSERT INTO LESSON_SESSION` cho từng entry:

```python
for entry in plan:
    session = repo.create_session(db, LessonSession(
        class_id=class_id,
        schedule_id=entry["schedule_id"],
        session_number=entry["session_number"],
        lesson_date=entry["date"],
        start_time=entry["start_time"],
        end_time=entry["end_time"],
        status="SCHEDULED",
    ))
    created_ids.append(session.session_id)
repo.commit(db)
```

DB có partial unique index `(class_id, session_number) WHERE session_number IS NOT NULL` nên việc tạo tuần tự + commit một lần đảm bảo không trùng.

### 8.4. Repository `create_session`

`app/repositories/class_repository.py` (theo convention): `INSERT INTO LESSON_SESSION (class_id, schedule_id, session_number, lesson_date, start_time, end_time, status) OUTPUT INSERTED.*`.

### 8.5. Sơ đồ

```
SessionsPage "Tự sinh buổi học"
  ├─► previewSessionsFromSchedules({class_id, range_start, range_end})
  │     └─► POST /sessions/preview-from-schedules
  │           └─► service.preview_sessions_from_schedules
  │                 ├─ get_class_or_404
  │                 ├─ _resolve_session_window (auto-fill nếu thiếu)
  │                 ├─► repo.get_schedules (raw SQL)
  │                 ├─► repo.get_sessions  (raw SQL)
  │                 ├─ _build_session_plan (Python algorithm)
  │                 └─ return {preview_count, preview: [...]}
  │
  └─► generateSessionsFromSchedules({class_id, range_start, range_end})
        └─► POST /sessions/generate-from-schedules
              └─► service.generate_sessions_from_schedules
                    ├─ _build_session_plan
                    └─ for each entry: repo.create_session (INSERT)
                    repo.commit(db)
                    return {created_count, created_session_ids}
```

---

## 9. Flow #6 — Cập nhật trạng thái buổi học

> Sau buổi học, tutor/staff cập nhật `LESSON_SESSION.status`: SCHEDULED → COMPLETED (có content_note) / STUDENT_ABSENT / TUTOR_ABSENT / CANCELED.

### 9.1. UI

`SessionsPage` có nút "Hoàn thành" / "Vắng" cho mỗi row. Khi bấm COMPLETED, mở modal nhập `content_note`.

API: `api.js:185-188`:
```js
export const updateSessionStatus = (id, payload) => request(`/sessions/${id}/status`, {
  method: 'PATCH',
  body: JSON.stringify(payload),
});
```

### 9.2. Route + service

`app/routers/session_routes.py`:
```python
@router.patch("/{session_id}/status", response_model=LessonSessionResponse)
def update_session_status(
    session_id: int,
    payload: LessonSessionStatusUpdate,
    actor: CurrentActor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    # ensure session access (tutor/staff/student theo class)
    return service.update_session_status(db, session_id, payload)
```

`app/services/class_flow_service.py:174-181`:

```python
def update_session_status(db, session_id, payload):
    get_session_or_404(db, session_id)
    data = {"status": _normalize_choice(payload.status, SESSION_STATUSES, "status")}
    if "content_note" in payload.model_fields_set:
        data["content_note"] = payload.content_note
    repo.update_session(db, session_id, data)
    repo.commit(db)
    return session_to_response(repo.get_session(db, session_id))
```

### 9.3. DB

`LESSON_SESSION.status` check constraint: `IN ('SCHEDULED', 'COMPLETED', 'STUDENT_ABSENT', 'TUTOR_ABSENT', 'CANCELED')`.

Session ở trạng thái `COMPLETED` là đầu vào cho:
- Realtime tuition summary (`FN_CLASS_TUITION_SUMMARY` đếm COMPLETED).
- Snapshot invoice (`SP_CREATE_INVOICE_FOR_PERIOD` đếm COMPLETED trong period).

---

## 10. Flow #7 — Tạo Invoice + Payment + Realtime Tuition Summary

> Staff tạo hóa đơn học phí cho một period, sau đó ghi nhận thanh toán từ phụ huynh. Realtime tuition summary cho phép xem số liệu fresh từ DB (không snapshot).

### 10.1. Realtime tuition summary

UI: `FinancePage` chọn class → gọi `getClassTuitionSummary(classId)`.

API: `api.js:154`:
```js
export const getClassTuitionSummary = (classId) => request(`/classes/${classId}/tuition-summary`);
```

Route: `app/routers/class_finance.py` (theo convention): `GET /classes/{class_id}/tuition-summary`.

Service: `app/services/class_flow_service.py:191-203`:

```python
def tuition_summary(db, class_id):
    get_class_or_404(db, class_id)
    summary = repo.get_class_tuition_summary(db, class_id)
    if not summary:
        raise HTTPException(404, "Class not found")
    return {
        "class_id": class_id,
        "completed_sessions": summary.completed_sessions,
        "tuition_fee_per_session": _money(summary.tuition_fee_per_session),
        "total_fee": _money(summary.total_fee),
        "paid_amount": _money(summary.paid_amount),
        "remaining_amount": max(_money(summary.remaining_amount), 0.0),
    }
```

Repository: `repo.get_class_tuition_summary` ở `app/repositories/class_repository.py` gọi function SQL:

```sql
SELECT * FROM dbo.FN_CLASS_TUITION_SUMMARY(:class_id)
```

Function `FN_CLASS_TUITION_SUMMARY` ở `sql/schema.sql:502-561`:
- 3 CTE: `completed` (đếm LESSON_SESSION status='COMPLETED'), `invoice_totals` (tổng amount_due + đếm unpaid/overdue), `payment_totals` (tổng SUCCESS payments).
- Trả về 1 row: `class_id, completed_sessions, tuition_fee_per_session, total_fee, total_invoiced, paid_amount (=total_paid_success), remaining_amount, unpaid_invoice_count, overdue_invoice_count`.

### 10.2. Tạo Invoice

UI: `FinancePage` form "Tạo hóa đơn" với `class_id`, `period_start`, `period_end`, `completed_sessions`, `tuition_fee_per_session`, `amount_due`, `amount_paid`, `status`.

Khi user chọn class, `handleClassSelect` tự gọi `getClassTuitionSummary` + `getClassInvoicePeriod` để auto-fill:
```js
const [summary, period] = await Promise.all([
  getClassTuitionSummary(classId),
  getClassInvoicePeriod(classId),
]);
setInvoiceForm({
  class_id: classId,
  period_start: period.period_start,
  period_end: period.period_end,
  completed_sessions: summary.completed_sessions,
  tuition_fee_per_session: summary.tuition_fee_per_session,
  amount_due: summary.completed_sessions * summary.tuition_fee_per_session,  // auto-recalc
});
```

Validation client-side (`validateInvoice`):
- `class_id` required.
- `period_start <= period_end`.
- `completed_sessions >= 0`, `tuition_fee_per_session > 0`, `amount_due > 0`.
- Check trùng period: `getInvoices({ class_id })` rồi tìm invoice ACTIVE cùng period → set `invoiceDuplicate` warning.

API: `createInvoice` ở `api.js:215-217`:
```
POST /invoices
```

Route: `POST /invoices` ở `app/routers/invoices.py`. Service: `create_invoice` ở `app/services/finance_service.py:36-65`:

```python
def create_invoice(db, payload):
    get_class_or_404(db, payload.class_id)
    _validate_invoice_values(period_start, period_end, completed_sessions, tuition_fee_per_session, amount_due, amount_paid)
    existing_invoice = repo.get_invoice_by_class_period(db, payload.class_id, payload.period_start, payload.period_end)
    if existing_invoice:
        raise HTTPException(409, "Invoice already exists for this class and period")
    _normalize_invoice_status(payload.status)
    invoice = repo.create_invoice(db, TuitionInvoice(
        class_id=payload.class_id, period_start, period_end, completed_sessions,
        tuition_fee_per_session, amount_due, amount_paid, status,
    ))
    repo.commit(db)
    return invoice_to_response(repo.get_invoice(db, invoice.invoice_id))
```

Repository `create_invoice` ở `app/repositories/finance_repository.py:103-152` — raw INSERT với OUTPUT INSERTED.*.

### 10.3. Tạo Payment

UI: form "Ghi nhận thanh toán" với `invoice_id`, `amount_paid`, `payment_method`, `note`.

Validation client-side: `paymentAmount <= invoiceRemaining` (= `amount_due - amount_paid`). Nếu vượt, button submit bị disable + hiển thị error inline (`paymentFieldError`).

API: `createPayment` ở `api.js:230-232`:
```
POST /payments
```

Route: `POST /payments` ở `app/routers/payments.py`. Service: `create_payment` ở `app/services/finance_service.py:111-171`:

```python
def create_payment(db, payload):
    payment_amount = _decimal_money(payload.amount_paid)
    _validate_positive_decimal(payment_amount, "Payment amount")
    payment_status = _normalize_payment_status(payload.status) if payload.status else "SUCCESS"
    invoice = None
    if payload.invoice_id:
        invoice = get_invoice_or_404(db, payload.invoice_id)
        if payload.class_id is not None and invoice.class_id != payload.class_id:
            raise HTTPException(400, "class_id must match invoice_id")
    elif payload.class_id:
        # nếu không có invoice_id, tìm invoice theo class + period
        ...
    if invoice and invoice.status == "CANCELED":
        raise HTTPException(400, "Cannot record payment for a canceled invoice")
    if payload.staff_id is not None:
        get_staff_or_404(db, payload.staff_id)
    if payment_status == "SUCCESS":
        # Validate số tiền không vượt remaining
        if invoice:
            remaining_amount = _invoice_remaining_amount(invoice)
        else:
            snapshot = repo.get_class_invoice_snapshot(db, payload.class_id, period_start, period_end)
            remaining_amount = _decimal_money(snapshot["amount_due"])
        if payment_amount > remaining_amount:
            raise HTTPException(400, "Payment amount exceeds invoice remaining amount")
    payment = repo.create_payment(db, TuitionPayment(...), class_id=..., period_start=..., period_end=...)
    repo.commit(db)
    return payment_to_response(payment)
```

Đây là **service-layer validation** quan trọng nhất của finance flow — tuân thủ rule "không chỉ dựa vào DB constraint" trong `AGENTS.md`.

### 10.4. Repository `create_payment`

`app/repositories/finance_repository.py:318-354` — gọi SP:

```sql
EXEC SP_CREATE_TUITION_PAYMENT
    @invoice_id = :invoice_id,
    @class_id = :class_id,
    @period_start = :period_start,
    @period_end = :period_end,
    @amount_paid = :amount_paid,
    @payment_method = :payment_method,
    @payment_date = :payment_date,
    @staff_id = :staff_id,
    @note = :note,
    @status = :status
```

### 10.5. SP `SP_CREATE_TUITION_PAYMENT`

`sql/schema.sql:852-990` — flow:

1. `BEGIN TRAN`, `SET XACT_ABORT ON`.
2. **Nhánh A** (có `@invoice_id`):
   - Lookup invoice; nếu `status = 'CANCELED'` → THROW.
3. **Nhánh B** (không có `@invoice_id`, có `@class_id + period`):
   - Tìm invoice theo `(class_id, period_start, period_end)`.
   - Nếu chưa có, **inline tạo invoice mới** (logic giống `SP_CREATE_INVOICE_FOR_PERIOD`).
4. **Validate**:
   - `FN_INVOICE_REMAINING_AMOUNT(@invoice_id)` lấy remaining.
   - Nếu `status='SUCCESS'` và `@amount_paid > remaining` → `THROW 50010, 'Payment exceeds remaining amount', 1`.
5. `INSERT INTO TUITION_PAYMENT (invoice_id, staff_id, payment_date, amount_paid, payment_method, note, status)`.
6. `COMMIT` rồi trả về `{payment_id, invoice_id}`.

### 10.6. Trigger `TRG_TUITION_PAYMENT_RECALC_INVOICE`

`sql/schema.sql:444-480` — `AFTER INSERT, UPDATE, DELETE` trên `TUITION_PAYMENT`:

```sql
SELECT @invoice_id = COALESCE((SELECT TOP 1 invoice_id FROM inserted),
                              (SELECT TOP 1 invoice_id FROM deleted));
SELECT @total_paid = COALESCE(SUM(amount_paid), 0)
FROM TUITION_PAYMENT
WHERE invoice_id = @invoice_id AND status = 'SUCCESS';

UPDATE TUITION_INVOICE
SET amount_paid = @total_paid,
    status = CASE
        WHEN status = 'CANCELED' THEN 'CANCELED'
        WHEN @total_paid = 0 THEN 'UNPAID'
        WHEN @total_paid < amount_due THEN 'PARTIALLY_PAID'
        ELSE 'PAID'
    END,
    updated_at = SYSUTCDATETIME()
WHERE invoice_id = @invoice_id;
```

Quy tắc: **chỉ `SUCCESS` payments đếm**, `CANCELED`/`REFUNDED` bị bỏ qua.

### 10.7. Realtime vs snapshot

| Cái | Snapshot? | Nguồn |
|---|---|---|
| `TUITION_INVOICE.amount_due` / `amount_paid` / `status` | **Snapshot theo period** (ghi cứng lúc tạo invoice) | `TUITION_INVOICE` table |
| `GET /classes/{id}/tuition-summary` | **Realtime** (tính lại mỗi lần gọi) | `FN_CLASS_TUITION_SUMMARY` → LESSON_SESSION + TUITION_INVOICE + TUITION_PAYMENT |

`FinancePage` reload summary sau khi tạo payment (`getClassTuitionSummary` được gọi lại tự động trong handler) để đảm bảo UI đồng bộ.

### 10.8. Sơ đồ

```
FinancePage (Staff)
  │
  ├─► getClassTuitionSummary(class_id)  (realtime, không cache)
  │     └─► GET /classes/{id}/tuition-summary
  │           └─► service.tuition_summary
  │                 └─► repo.get_class_tuition_summary
  │                       └─► SELECT * FROM FN_CLASS_TUITION_SUMMARY(:class_id)
  │
  ├─► createInvoice(payload)
  │     └─► POST /invoices
  │           └─► service.create_invoice
  │                 ├─ duplicate check (repo.get_invoice_by_class_period)
  │                 ├─► repo.create_invoice (raw INSERT)
  │                 └─ commit
  │
  └─► createPayment(payload)
        └─► POST /payments
              └─► service.create_payment
                    ├─ validate amount_paid > 0
                    ├─ resolve invoice (by id or by class+period)
                    ├─ SERVICE-LAYER check: SUCCESS payment > remaining → 400
                    └─► repo.create_payment
                          └─► EXEC SP_CREATE_TUITION_PAYMENT
                                ├─ resolve / create invoice nếu cần
                                ├─ SP-level check: amount_paid > remaining → THROW
                                └─ INSERT INTO TUITION_PAYMENT
                    COMMIT
        TRG_TUITION_PAYMENT_RECALC_INVOICE tự động fire:
          └─► UPDATE TUITION_INVOICE SET amount_paid, status
        ← response → UI reload summary + list
```

---

## 11. Phụ lục A — Soft delete pattern

Mọi `DELETE` HTTP đều là soft delete. Tổng hợp mapping:

| Endpoint | Service | Repository | DB effect |
|---|---|---|---|
| `DELETE /students/{id}` | `deactivate_student` | `repo.deactivate_student` → `update_by_id(..., {"status": "INACTIVE"})` | `STUDENT.status = 'INACTIVE'` |
| `DELETE /tutors/{id}` | `deactivate_tutor` | tương tự | `TUTOR.status = 'INACTIVE'` |
| `DELETE /subjects/{id}` | `deactivate_subject` | tương tự | `SUBJECT.status = 'INACTIVE'` |
| `DELETE /schedules/{id}` | `delete_schedule` | `repo.deactivate_schedule` | `CLASS_SCHEDULE.status = 'INACTIVE'` |
| `DELETE /learning-requests/{id}` | `cancel_learning_request` | `repo.cancel_learning_request` | `LEARNING_REQUEST.status = 'CANCELED'` |
| `DELETE /assignments/{id}` hoặc `PATCH /assignments/{id}/cancel` | `cancel_assignment` | `repo.cancel_assignment` + `repo.update_learning_request(..., {"status": "PENDING"})` (revert request) | `TUTOR_ASSIGNMENT.status = 'CANCELED'` + revert request |
| `DELETE /classes/{id}` | `cancel_study_class` | `repo.cancel_class` | `STUDY_CLASS.status = 'CANCELED'` |
| `DELETE /sessions/{id}` | `delete_session` | `repo.cancel_session` | `LESSON_SESSION.status = 'CANCELED'` |
| `DELETE /invoices/{id}` | `delete_invoice` | `repo.cancel_invoice` | `TUITION_INVOICE.status = 'CANCELED'` |
| `DELETE /payments/{id}` | `delete_payment` | `repo.cancel_payment` | `TUITION_PAYMENT.status = 'CANCELED'` |

Đặc biệt `cancel_assignment` còn revert `LEARNING_REQUEST.status` về `'PENDING'` để staff có thể phân công lại (xem `app/services/request_flow_service.py:140-148`).

---

## 12. Phụ lục B — SQL objects (View/SP/Function/Trigger)

### 12.1. Views (dùng cho mọi list/detail response)

| View | Join chain | File |
|---|---|---|
| `VW_LEARNING_REQUEST_DETAIL` | LEARNING_REQUEST ⊕ STUDENT + SUBJECT + (OUTER APPLY) TUTOR_ASSIGNMENT ⊕ TUTOR + STAFF | `sql/schema.sql:997-1056` |
| `VW_STUDY_CLASS_DETAIL` | STUDY_CLASS → TUTOR_ASSIGNMENT → LEARNING_REQUEST → STUDENT + SUBJECT; → TUTOR_ASSIGNMENT → TUTOR; → STAFF | `sql/schema.sql:1184-1235` |
| `VW_LESSON_SESSION_DETAIL` | LESSON_SESSION + CLASS_SCHEDULE + chain như trên | `sql/schema.sql:1058-1102` |
| `VW_INVOICE_DETAIL` | TUITION_INVOICE + chain | `sql/schema.sql:1104-1139` |
| `VW_PAYMENT_DETAIL` | TUITION_PAYMENT LEFT JOIN STAFF + chain | `sql/schema.sql:1141-1182` |

### 12.2. Functions

| Function | Trả về | File |
|---|---|---|
| `FN_INVOICE_REMAINING_AMOUNT(@invoice_id)` | DECIMAL(18,2) = `MAX(0, amount_due - amount_paid)` | `sql/schema.sql:483-499` |
| `FN_CLASS_TUITION_SUMMARY(@class_id)` | Table-valued 1 row: completed_sessions, total_fee, paid_amount, remaining_amount, unpaid_invoice_count, overdue_invoice_count | `sql/schema.sql:502-561` |

### 12.3. Stored Procedures (đều có `TRY/CATCH` + `SET XACT_ABORT ON` + `ROLLBACK` + `THROW`)

| SP | Input | Output | File |
|---|---|---|---|
| `SP_ASSIGN_TUTOR_TO_REQUEST` | `@request_id, @tutor_id, @staff_id, @note` | TUTOR_ASSIGNMENT row mới + `LEARNING_REQUEST.status='ASSIGNED'` | `sql/schema.sql:563-662` |
| `SP_CREATE_CLASS_FROM_ASSIGNMENT` | `@assignment_id, @class_code, @tuition_fee_per_session, @teaching_mode, @location, @start_date, @end_date, @status` | STUDY_CLASS row mới | `sql/schema.sql:665-754` |
| `SP_CREATE_INVOICE_FOR_PERIOD` | `@class_id, @period_start, @period_end` | TUITION_INVOICE row mới (đếm COMPLETED sessions, set amount_due) | `sql/schema.sql:757-849` |
| `SP_CREATE_TUITION_PAYMENT` | `@invoice_id?`, `@class_id?`, `@period_start?`, `@period_end?`, `@amount_paid, @payment_method?`, `@payment_date?`, `@staff_id?`, `@note?`, `@status` | `{payment_id, resolved_invoice_id}`; tự tạo invoice nếu thiếu; SP-level check `amount_paid > remaining` → THROW | `sql/schema.sql:852-990` |

### 12.4. Trigger

| Trigger | Fire | Logic | File |
|---|---|---|---|
| `TRG_TUITION_PAYMENT_RECALC_INVOICE` | AFTER INSERT/UPDATE/DELETE trên TUITION_PAYMENT | Tính lại `TUITION_INVOICE.amount_paid` (chỉ SUCCESS) + `status` (CANCELED/UNPAID/PARTIALLY_PAID/PAID) | `sql/schema.sql:444-480` |

---

## Đọc tiếp

- Bộ docs khác: `docs/current_status.md` (trạng thái hiện tại), `docs/api_contract.md` (API chi tiết), `docs/agent_worklog.md` (lịch sử thay đổi).
- Nếu cần walkthrough cho luồng phụ (Tutor Capabilities/Availability, Tutor Profile), nội dung ở phần 1-3 đã đủ ngữ cảnh — chỉ cần tra cứu endpoint tương ứng trong `docs/api_contract.md` rồi dò theo pattern router → service → repository → SQL y hệt như 7 flow trên.

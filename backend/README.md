# Backend

FastAPI backend cho SmartTutor Platform, ket noi SQL Server bang SQLAlchemy + pyodbc.

## Cong nghe

- Python
- FastAPI
- SQLAlchemy
- pyodbc
- SQL Server
- Pydantic
- Uvicorn

## Cau truc

| Duong dan | Vai tro |
| --- | --- |
| `app/main.py` | Khoi tao FastAPI app, CORS, include routers |
| `app/config.py` | Doc bien moi truong |
| `app/database.py` | Tao SQLAlchemy engine, SessionLocal, Base, get_db |
| `app/models/` | SQLAlchemy models map cac bang SQL Server |
| `app/schemas/` | Pydantic request/response schemas |
| `app/repositories/` | CRUD/query truc tiep voi DB |
| `app/services/` | Nghiep vu va mapping response cho frontend |
| `app/routers/` | API endpoints |

## Cai ODBC Driver

Can cai Microsoft ODBC Driver for SQL Server tren may chay backend.

Driver mac dinh trong `.env.example`:

```text
ODBC Driver 17 for SQL Server
```

Neu may ban dung driver khac, sua `DB_DRIVER` trong `.env`.

## Tao database

Chay script:

```text
../sql/schema.sql
```

Bang SQL Server Management Studio, Azure Data Studio, hoac `sqlcmd`.

`../sql/schema.sql` hien la ban schema SQL Server `FINAL CLEAN` va duoc xem la nguon su that cho backend. Schema nay da gom trigger tinh lai hoa don hoc phi va view `VW_STUDY_CLASS_DETAIL`.

De nap du lieu toi thieu phuc vu smoke test backend, co the chay:

```text
../sql/minimal_seed.sql
```

De nap du lieu demo day du hon cho auth, requests, classes, sessions, invoices/payments, co the chay:

```text
../sql/sample_data.sql
```

Bo `sample_data.sql` hien tai da du phong cho demo end-to-end:

- 3 tai khoan staff
- 7 tai khoan student
- 7 tai khoan tutor
- nhieu subject / capability / availability
- nhieu learning request o cac trang thai `PENDING`, `ASSIGNED`, `CANCELED`
- 6 assignment
- 6 class
- schedule, session, invoice, payment du de test dashboard va luong hoc phi

Mat khau demo mac dinh theo role:

- staff: `staff123`
- student: `student123`
- tutor: `tutor123`

Danh sach tai khoan demo chi tiet va cac flow test goi y:

```text
../sql/demo_accounts.md
```

Quan trong: khi nap file seed co tieng Viet bang `sqlcmd` tren Windows, phai chi dinh UTF-8 input de tranh loi vo dau/mojibake. Co the dung script san co:

```powershell
cd ..
powershell -ExecutionPolicy Bypass -File .\sql\reset_demo_utf8.ps1 -Seed sample
```

Neu chay `sqlcmd` truc tiep, dung:

```powershell
sqlcmd -S localhost -d TutorCenterDB -U sa -P 123456 -C -f 65001 -i .\sql\sample_data.sql
```

Phase 1 smoke test de xuat:

```powershell
uv run python -m compileall app
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Sau do kiem tra:

- `GET /`
- `GET /health`
- `GET /subjects`
- `GET /classes`

## Cau hinh moi truong

Tao file `.env` tu `.env.example`:

```powershell
Copy-Item .env.example .env
```

SQL Authentication:

```text
DB_SERVER=localhost
DB_NAME=TutorCenterDB
DB_USER=sa
DB_PASSWORD=YourPassword
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUSTED_CONNECTION=no
DB_TRUST_SERVER_CERTIFICATE=yes
```

Windows Authentication:

```text
DB_SERVER=localhost
DB_NAME=TutorCenterDB
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUSTED_CONNECTION=yes
DB_TRUST_SERVER_CERTIFICATE=yes
```

## Cai dependencies

```powershell
cd backend
uv venv .venv
uv pip install -r requirements.txt
```

## Chay backend

```powershell
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

## CORS

Backend dang cho phep frontend local:

- `http://localhost:3000`
- `http://localhost:5173`

Co the sua bang bien:

```text
FRONTEND_ORIGINS=http://localhost:3000,http://localhost:5173
```

## API chinh

- `POST /auth/login`
- `POST /auth/register`
- `GET /dashboard/summary`
- `/students`
- `/tutors`
- `/subjects`
- `/learning-requests`
- `/assignments`
- `/classes`
- `/schedules`
- `/sessions`
- `/invoices`
- `/payments`

## Luu y schema

Backend giu mo hinh chuan hoa:

```text
LEARNING_REQUEST -> TUTOR_ASSIGNMENT -> STUDY_CLASS
```

`STUDY_CLASS` khong co `student_id`, `tutor_id`, `subject_id` truc tiep. Cac API can hien thong tin lop cho frontend se join qua:

```text
STUDY_CLASS
-> TUTOR_ASSIGNMENT
-> LEARNING_REQUEST
-> STUDENT
-> SUBJECT

TUTOR_ASSIGNMENT
-> TUTOR
```

Remap hien tai cua backend theo schema `FINAL CLEAN`:

- `USER_ACCOUNT.username` duoc dung song song voi `email` cho auth/display.
- `STUDENT.contact_email`, `TUTOR.contact_email` duoc map ra field API `email` de giu frontend it phai sua.
- `LEARNING_REQUEST.learning_goal`, `preferred_area`, `preferred_mode` duoc map ve API `target`, `area`, `teaching_mode` de tuong thich contract frontend hien tai.
- `LESSON_SESSION.lesson_date` duoc tra ra field API `date`.
- `TUITION_INVOICE.period_start`, `period_end`, `amount_due`, `amount_paid` la field canonical cua invoice.
- `TUITION_PAYMENT.amount_paid`, `payment_date`, `payment_method`, `status` la field canonical cua payment.

## Tai lieu lien quan

- `../docs/frontend_analysis.md`
- `../docs/frontend_api_contract.md`

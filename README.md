# SmartTutor Platform

SmartTutor Platform là project môn Database cho trung tâm gia sư, gồm:

- `frontend/`: React + Vite
- `backend/`: FastAPI + SQLAlchemy + pyodbc
- `sql/`: schema và seed SQL Server
- `docs/`: tài liệu trạng thái, contract, và kế hoạch hoàn thiện

## Database

Schema nguồn sự thật là `sql/schema.sql`.

Chạy seed:

```powershell
sqlcmd -C -S localhost -d TutorCenterDB -U sa -P 123456 -i sql\minimal_seed.sql
sqlcmd -C -S localhost -d TutorCenterDB -U sa -P 123456 -i sql\sample_data.sql
```

## Backend

Copy env mẫu:

```powershell
Copy-Item backend\.env.example backend\.env
```

Chạy backend:

```powershell
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Kiểm tra:

- `http://localhost:8000/health`
- `http://localhost:8000/docs`

## Frontend

Copy env mẫu:

```powershell
Copy-Item frontend\.env.example frontend\.env
```

Chạy frontend:

```powershell
cd frontend
npm install
npm run dev
```

Build frontend:

```powershell
cd frontend
npm run build
```

## Notes

- `backend/.venv` đã được chuẩn bị sẵn, nên ưu tiên `uv`.
- Frontend mặc định gọi backend tại `http://localhost:8000` thông qua `VITE_API_BASE_URL`.
- `docs/api_contract.md` là contract canonical cho backend/frontend.

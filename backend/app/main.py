from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    assignments,
    auth,
    classes,
    dashboard,
    invoices,
    learning_requests,
    payments,
    schedules,
    sessions,
    students,
    subjects,
    tutors,
)


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": settings.app_name, "status": "ok"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(students.router)
app.include_router(tutors.router)
app.include_router(subjects.router)
app.include_router(learning_requests.router)
app.include_router(assignments.router)
app.include_router(classes.router)
app.include_router(schedules.router)
app.include_router(sessions.router)
app.include_router(invoices.router)
app.include_router(payments.router)

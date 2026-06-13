from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings


def build_odbc_connection_string() -> str:
    parts = [
        f"DRIVER={{{settings.db_driver}}}",
        f"SERVER={settings.db_server}",
        f"DATABASE={settings.db_name}",
    ]

    if settings.db_trusted_connection:
        parts.append("Trusted_Connection=yes")
    else:
        parts.extend([f"UID={settings.db_user}", f"PWD={settings.db_password}"])

    if settings.db_trust_server_certificate:
        parts.append("TrustServerCertificate=yes")

    return ";".join(parts) + ";"


DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={quote_plus(build_odbc_connection_string())}"

engine: Engine | None = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)
Base = declarative_base()


def get_engine() -> Engine:
    global engine
    if engine is None:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        SessionLocal.configure(bind=engine)
    return engine


def create_session() -> Session:
    get_engine()
    return SessionLocal()


def get_db():
    db = create_session()
    try:
        yield db
    finally:
        db.close()

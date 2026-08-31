# database.py
# Responsible for setting up the database connection using SQLAlchemy.
#
# Supports two backends:
#   - PostgreSQL  (production)  — set DATABASE_URL env var to a postgres:// URI
#   - SQLite      (development) — default fallback, no env var needed
#
# The correct engine arguments are chosen automatically based on the URL scheme.

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Read DATABASE_URL from the environment.
# Docker Compose injects this for the backend service (pointing at the db service).
# When running locally without Docker the SQLite fallback is used automatically.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./study_planner.db",   # local development default
)

# psycopg2 and older tooling sometimes emit "postgres://" instead of
# "postgresql://". SQLAlchemy 1.4+ requires the latter, so normalise it.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs check_same_thread=False to allow FastAPI's thread-pool to reuse
# a single connection across threads.  This flag must NOT be passed to Postgres.
_is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    # Connection pool tuning for PostgreSQL in a containerised environment.
    # pool_pre_ping sends a lightweight SELECT 1 before each checkout so
    # stale connections (e.g. after a db restart) are detected and recycled.
    pool_pre_ping=not _is_sqlite,
)

# SessionLocal is the factory that creates individual database sessions.
# autocommit=False  → we manually commit transactions
# autoflush=False   → changes are not flushed to the DB until commit
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for all SQLAlchemy models (tables)
class Base(DeclarativeBase):
    pass


def get_db():
    """
    FastAPI dependency that yields a database session per request.
    The session is always closed in the finally block, even on errors.

    Usage in routes:
        def my_route(db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

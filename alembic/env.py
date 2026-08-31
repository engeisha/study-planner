# alembic/env.py
# Alembic migration environment.
#
# URL resolution order:
#   1. DATABASE_URL environment variable  (set in Docker / CI)
#   2. sqlalchemy.url in alembic.ini      (local fallback)
#
# This means the same migration commands work both locally (SQLite) and
# inside the Docker backend container (PostgreSQL) without any code changes.

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ── Import application metadata ────────────────────────────────────────────
from app.database import Base       # noqa: F401
import app.models.task              # noqa: F401 — registers Task with Base

# ── Alembic Config ─────────────────────────────────────────────────────────
config = context.config

# Set up Python logging from alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Override sqlalchemy.url from the environment if available ──────────────
_db_url = os.getenv("DATABASE_URL")
if _db_url:
    # Normalise legacy "postgres://" prefix that some platforms emit
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    # Inject into the alembic config so both offline and online modes pick it up
    config.set_main_option("sqlalchemy.url", _db_url)

target_metadata = Base.metadata


# ── Offline migration ──────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """
    Emit raw SQL to stdout / a file without a live DB connection.
    Useful for reviewing what will be applied before running it.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online migration ───────────────────────────────────────────────────────

def run_migrations_online() -> None:
    """
    Apply migrations directly against the live database.
    Default mode used by `alembic upgrade head`.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

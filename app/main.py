# main.py
# Entry point of the FastAPI application.
#
# Responsibilities:
#   - Create the FastAPI app instance
#   - Create database tables on startup
#   - Mount the static files directory
#   - Register route handlers
#   - Serve the SPA frontend at "/"

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import engine, Base
from app.routes import tasks

# Import all models so SQLAlchemy knows about them before creating tables
import app.models.task  # noqa: F401 — side-effect import to register the model


def create_tables():
    """
    Create all database tables defined via SQLAlchemy models.
    This runs automatically when the app starts.
    If the tables already exist, SQLAlchemy skips creation (safe to re-run).
    """
    Base.metadata.create_all(bind=engine)


# Create tables immediately when the module is loaded
create_tables()

# Create the main FastAPI application instance
app = FastAPI(
    title="Study Planner API",
    description="A simple REST API to manage study tasks. Supports full CRUD operations.",
    version="1.0.0",
)

# Register the tasks router
# All /tasks endpoints defined in routes/tasks.py are now active
app.include_router(tasks.router)

# Mount the static directory so that /static/<filename> is served directly
# (e.g. /static/index.html, future JS/CSS assets, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    """
    Serve the single-page frontend dashboard.
    Navigating to http://localhost:8000/ returns index.html.
    Excluded from the OpenAPI schema — use /docs for the API reference.
    """
    return FileResponse("app/static/index.html")

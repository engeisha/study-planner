# tests/test_tasks.py
# Integration tests for the Study Planner API using pytest and FastAPI's TestClient.
#
# Key design decisions:
#   - Uses an in-memory SQLite database (separate from production)
#   - Overrides FastAPI's get_db dependency so tests never touch the real database
#   - Each test function receives a fresh client via the `client` fixture

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# ---------------------------------------------------------------------------
# Test database setup
# Uses a separate in-memory SQLite database so tests are isolated.
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite:///./test_study_planner.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """
    Replacement for the real get_db dependency.
    Points to the test database instead of the production database.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """
    Pytest fixture that:
      1. Creates all tables in the test database
      2. Overrides the get_db dependency with the test version
      3. Provides a TestClient for sending HTTP requests
      4. Drops all tables after the test finishes (clean state)
    """
    # Create fresh tables for this test
    Base.metadata.create_all(bind=test_engine)

    # Override the dependency in the FastAPI app
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Teardown: remove all tables after the test
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Sample payload used across multiple tests
# ---------------------------------------------------------------------------

SAMPLE_TASK = {
    "title": "Read Chapter 5",
    "description": "Read and summarise chapter 5 of the textbook.",
    "subject": "Mathematics",
    "due_date": "2026-09-01",
    "completed": False,
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_create_task(client):
    """POST /tasks should create a task and return 201 with the task data."""
    response = client.post("/tasks/", json=SAMPLE_TASK)

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == SAMPLE_TASK["title"]
    assert data["subject"] == SAMPLE_TASK["subject"]
    assert data["due_date"] == SAMPLE_TASK["due_date"]
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data


def test_get_all_tasks_empty(client):
    """GET /tasks should return an empty list when no tasks exist."""
    response = client.get("/tasks/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_all_tasks(client):
    """GET /tasks should return all created tasks."""
    # Create two tasks first
    client.post("/tasks/", json=SAMPLE_TASK)
    client.post("/tasks/", json={**SAMPLE_TASK, "title": "Solve Exercise Set 3"})

    response = client.get("/tasks/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_single_task(client):
    """GET /tasks/{id} should return the correct task."""
    create_response = client.post("/tasks/", json=SAMPLE_TASK)
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == SAMPLE_TASK["title"]


def test_get_nonexistent_task(client):
    """GET /tasks/{id} for a task that does not exist should return 404."""
    response = client.get("/tasks/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_task(client):
    """PUT /tasks/{id} should update the specified fields of a task."""
    create_response = client.post("/tasks/", json=SAMPLE_TASK)
    task_id = create_response.json()["id"]

    update_payload = {"completed": True, "title": "Read Chapter 5 (Done)"}
    response = client.put(f"/tasks/{task_id}", json=update_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["title"] == "Read Chapter 5 (Done)"
    # Fields not included in the update should remain unchanged
    assert data["subject"] == SAMPLE_TASK["subject"]


def test_update_nonexistent_task(client):
    """PUT /tasks/{id} for a task that does not exist should return 404."""
    response = client.put("/tasks/99999", json={"title": "Ghost Task"})

    assert response.status_code == 404


def test_delete_task(client):
    """DELETE /tasks/{id} should delete the task and return 204."""
    create_response = client.post("/tasks/", json=SAMPLE_TASK)
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    # Verify the task no longer exists
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_task(client):
    """DELETE /tasks/{id} for a task that does not exist should return 404."""
    response = client.delete("/tasks/99999")

    assert response.status_code == 404


def test_create_task_missing_required_fields(client):
    """POST /tasks without required fields should return 422 Unprocessable Entity."""
    # Missing title and subject
    response = client.post("/tasks/", json={"due_date": "2026-09-01"})

    assert response.status_code == 422


def test_create_task_empty_title(client):
    """POST /tasks with an empty title should return 422."""
    payload = {**SAMPLE_TASK, "title": "   "}
    response = client.post("/tasks/", json=payload)

    assert response.status_code == 422

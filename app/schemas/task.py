# schemas/task.py
# Pydantic schemas for request validation and response serialization.
#
# There are three schemas:
#   - TaskCreate  : used when a client sends data to CREATE a task (POST)
#   - TaskUpdate  : used when a client sends data to UPDATE a task (PUT)
#   - TaskResponse: used to send task data back to the client (response model)

from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, field_validator

# Constrained literal types keep validation tight and self-documenting
PriorityType = Literal["High", "Medium", "Low"]
CategoryType = Literal["Assignment", "Exam", "Reading", "Project", "General"]


class TaskCreate(BaseModel):
    """
    Schema for creating a new task.
    All required fields must be provided by the client.
    """
    title: str
    description: str | None = None    # Optional field
    subject: str
    due_date: date                     # Expected format: YYYY-MM-DD
    completed: bool = False            # Defaults to False if not provided
    priority: PriorityType = "Medium"  # Defaults to Medium
    category: CategoryType = "General" # Defaults to General

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, value: str) -> str:
        """Ensure the title is not just whitespace."""
        if not value.strip():
            raise ValueError("Title must not be empty or whitespace.")
        return value.strip()

    @field_validator("subject")
    @classmethod
    def subject_must_not_be_empty(cls, value: str) -> str:
        """Ensure the subject is not just whitespace."""
        if not value.strip():
            raise ValueError("Subject must not be empty or whitespace.")
        return value.strip()


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.
    All fields are optional — the client only sends what they want to change.
    """
    title: str | None = None
    description: str | None = None
    subject: str | None = None
    due_date: date | None = None
    completed: bool | None = None
    priority: PriorityType | None = None
    category: CategoryType | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, value: str | None) -> str | None:
        """If a title is provided, it must not be blank."""
        if value is not None and not value.strip():
            raise ValueError("Title must not be empty or whitespace.")
        return value.strip() if value else value

    @field_validator("subject")
    @classmethod
    def subject_must_not_be_empty(cls, value: str | None) -> str | None:
        """If a subject is provided, it must not be blank."""
        if value is not None and not value.strip():
            raise ValueError("Subject must not be empty or whitespace.")
        return value.strip() if value else value


class TaskResponse(BaseModel):
    """
    Schema used to return task data to the client.
    Includes all fields including id and created_at (read-only fields).
    """
    id: int
    title: str
    description: str | None
    subject: str
    due_date: date
    completed: bool
    priority: str
    category: str
    created_at: datetime

    # This tells Pydantic to read data from SQLAlchemy model attributes
    # (not just plain dicts)
    model_config = {"from_attributes": True}

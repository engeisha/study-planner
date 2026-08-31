# models/task.py
# Defines the Task database table using SQLAlchemy ORM.
# Each attribute here corresponds to a column in the 'tasks' table.

from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Task(Base):
    """
    SQLAlchemy model that maps to the 'tasks' table in SQLite.
    """
    __tablename__ = "tasks"

    # Primary key — auto-incremented by SQLite
    id = Column(Integer, primary_key=True, index=True)

    # Title of the study task (e.g., "Read Chapter 3")
    title = Column(String, nullable=False)

    # Optional longer description of what the task involves
    description = Column(String, nullable=True)

    # The subject this task belongs to (e.g., "Mathematics")
    subject = Column(String, nullable=False)

    # The date the task is due (stored as a date, not datetime)
    due_date = Column(Date, nullable=False)

    # Whether the student has completed this task — defaults to False
    completed = Column(Boolean, default=False, nullable=False)

    # Task urgency level: "High", "Medium", or "Low" — defaults to "Medium"
    priority = Column(String, default="Medium", nullable=False)

    # Broad grouping for the task type — defaults to "General"
    # Allowed values: Assignment, Exam, Reading, Project, General
    category = Column(String, default="General", nullable=False)

    # Automatically set to the current UTC timestamp when the record is created
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

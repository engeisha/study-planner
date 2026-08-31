# routes/tasks.py
# Defines all the API endpoints for the Task resource.
#
# Each route:
#   1. Receives the HTTP request
#   2. Validates input via Pydantic schemas
#   3. Calls database operations
#   4. Returns a response
#
# Database logic is kept inside this file but separated into clearly
# named helper functions to keep responsibilities clean.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

# APIRouter groups related routes together
# They are registered in main.py using app.include_router()
router = APIRouter(
    prefix="/tasks",       # All routes here start with /tasks
    tags=["Tasks"],        # Groups endpoints under "Tasks" in Swagger UI
)


# ---------------------------------------------------------------------------
# Helper / CRUD functions
# These functions contain the actual database logic.
# Keeping them separate from the route functions makes the code easier to read
# and will make it simple to extract them into a dedicated crud.py later.
# ---------------------------------------------------------------------------

def get_task_or_404(task_id: int, db: Session) -> Task:
    """
    Retrieve a task by its ID.
    Raises a 404 HTTP error if the task does not exist.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found."
        )
    return task


def create_task_in_db(data: TaskCreate, db: Session) -> Task:
    """
    Insert a new Task record into the database and return it.
    """
    new_task = Task(
        title=data.title,
        description=data.description,
        subject=data.subject,
        due_date=data.due_date,
        completed=data.completed,
        priority=data.priority,
        category=data.category,
    )
    db.add(new_task)
    db.commit()
    # Refresh loads the auto-generated fields (id, created_at) back into the object
    db.refresh(new_task)
    return new_task


def update_task_in_db(task: Task, data: TaskUpdate, db: Session) -> Task:
    """
    Apply partial updates to an existing Task record.
    Only fields that were actually provided (not None) are updated.
    """
    # model_dump(exclude_unset=True) returns only the fields the client sent
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task_in_db(task: Task, db: Session) -> None:
    """
    Delete a Task record from the database.
    """
    db.delete(task)
    db.commit()


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new study task",
)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new study task.

    - **title**: Required. Cannot be empty.
    - **description**: Optional free-text description.
    - **subject**: Required. Cannot be empty.
    - **due_date**: Required. Format: YYYY-MM-DD.
    - **completed**: Optional. Defaults to false.
    """
    return create_task_in_db(task_data, db)


@router.get(
    "/",
    response_model=list[TaskResponse],
    summary="Get all study tasks",
)
def get_all_tasks(db: Session = Depends(get_db)):
    """
    Return a list of all study tasks.
    Returns an empty list if no tasks exist.
    """
    return db.query(Task).all()


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a single study task by ID",
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Return a single study task by its ID.
    Returns 404 if the task does not exist.
    """
    return get_task_or_404(task_id, db)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update an existing study task",
)
def update_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)):
    """
    Update one or more fields of an existing task.
    Returns 404 if the task does not exist.
    Only fields included in the request body are updated.
    """
    task = get_task_or_404(task_id, db)
    return update_task_in_db(task, task_data, db)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a study task",
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete an existing task by ID.
    Returns 404 if the task does not exist.
    Returns 204 No Content on success (no response body).
    """
    task = get_task_or_404(task_id, db)
    delete_task_in_db(task, db)

# Study Planner API

A beginner-friendly REST API built with **FastAPI** and **SQLite** that lets students manage their study tasks. Supports full CRUD operations.

---

## What the project does

Students can:
- Create study tasks with a title, subject, description, and due date
- View all their tasks or look up a single task by ID
- Update any field of an existing task (e.g., mark it as completed)
- Delete tasks they no longer need

---

## Technology used

| Tool | Purpose |
|---|---|
| Python 3.12+ | Programming language |
| FastAPI | Web framework for building the REST API |
| Uvicorn | ASGI server that runs the FastAPI app |
| SQLAlchemy | ORM for database interactions |
| SQLite | Lightweight file-based database |
| Pydantic | Data validation and serialisation |
| Pytest | Testing framework |

---

## Folder structure

```
study-planner/
│
├── app/
│   ├── __init__.py
│   ├── main.py          ← App entry point; registers routes and creates DB tables
│   ├── database.py      ← Database engine, session factory, and get_db dependency
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py      ← SQLAlchemy Task model (maps to the 'tasks' table)
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py      ← Pydantic schemas for request validation and responses
│   │
│   └── routes/
│       ├── __init__.py
│       └── tasks.py     ← All /tasks API endpoints
│
├── tests/
│   ├── __init__.py
│   └── test_tasks.py    ← Pytest integration tests
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## How the application works

```
HTTP Request
    ↓
FastAPI Route Handler  (routes/tasks.py)
    ↓
Pydantic Validation    (schemas/task.py)
    ↓
Database Operation     (routes/tasks.py helper functions)
    ↓
SQLAlchemy ORM         (models/task.py)
    ↓
SQLite Database        (study_planner.db)
    ↓
HTTP Response          (Pydantic serialisation)
```

When the application starts, SQLAlchemy automatically creates the `study_planner.db` file and the `tasks` table if they do not already exist.

---

## How to install dependencies

Make sure you are inside the project folder and your virtual environment is activated:

```bash
# Activate virtual environment (Windows CMD)
.venv\Scripts\activate.bat

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## How to run the application

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at: **http://127.0.0.1:8000**

The `--reload` flag makes the server restart automatically when you save a file (useful during development).

---

## How to run tests

```bash
python -m pytest tests/ -v
```

Tests use a separate in-memory database and never affect the production `study_planner.db`.

---

## Available API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/tasks/` | Create a new task |
| GET | `/tasks/` | Get all tasks |
| GET | `/tasks/{task_id}` | Get a single task by ID |
| PUT | `/tasks/{task_id}` | Update an existing task |
| DELETE | `/tasks/{task_id}` | Delete a task |

### Interactive documentation

| URL | Description |
|---|---|
| http://127.0.0.1:8000/docs | Swagger UI — try endpoints in your browser |
| http://127.0.0.1:8000/redoc | ReDoc — alternative documentation view |

---

## Task fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | Yes | Cannot be empty |
| `description` | string | No | Free-text |
| `subject` | string | Yes | Cannot be empty |
| `due_date` | date | Yes | Format: `YYYY-MM-DD` |
| `completed` | boolean | No | Defaults to `false` |
| `id` | integer | — | Auto-generated |
| `created_at` | datetime | — | Auto-generated |

### Example request body (POST /tasks/)

```json
{
  "title": "Read Chapter 5",
  "description": "Read and summarise chapter 5 of the textbook.",
  "subject": "Mathematics",
  "due_date": "2026-09-01",
  "completed": false
}
```

---

## How the CRUD flow works

1. **CREATE** — `POST /tasks/`  
   The client sends a JSON body. Pydantic validates it. SQLAlchemy inserts a new row into the `tasks` table. The new task (including its auto-generated `id` and `created_at`) is returned.

2. **READ ALL** — `GET /tasks/`  
   SQLAlchemy queries all rows from the `tasks` table and returns them as a JSON array.

3. **READ ONE** — `GET /tasks/{task_id}`  
   SQLAlchemy queries the row with the matching `id`. Returns 404 if not found.

4. **UPDATE** — `PUT /tasks/{task_id}`  
   Only the fields included in the request body are updated. Returns 404 if the task does not exist.

5. **DELETE** — `DELETE /tasks/{task_id}`  
   Deletes the row from the database. Returns `204 No Content` on success. Returns 404 if the task does not exist.





I ADDED A NEW LINE
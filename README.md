# mini-task-tracker

A minimal task tracker API built with FastAPI, designed for feature-based code extensions.

## Features

- ✅ Health check endpoint
- ✅ Task CRUD endpoints (create, read, update, delete)
- ✅ Task status support (pending, in_progress, done)
- ✅ Input validation with Pydantic
- ✅ Comprehensive test coverage
- ✅ Minimal web UI (no framework)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd mini-task-tracker

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Server

```bash
# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**Open http://localhost:8000/ for UI** — a simple web interface to view and create tasks.

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/tasks` | Create a new task |
| GET | `/tasks` | List all tasks |
| GET | `/tasks/{id}` | Get a specific task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |

### Task Status Values

- `pending` (default)
- `in_progress`
- `done`

## curl Examples

### Health Check

```bash
curl http://localhost:8000/health
```

### Create a Task

```bash
# Minimal task (title only)
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries"}'

# Task with all fields
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Complete project", "description": "Finish the API implementation", "status": "in_progress"}'
```

### List All Tasks

```bash
curl http://localhost:8000/tasks
```

### Get a Specific Task

```bash
curl http://localhost:8000/tasks/1
```

### Update a Task

```bash
# Update status only
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'

# Update multiple fields
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated title", "description": "New description", "status": "in_progress"}'
```

### Delete a Task

```bash
curl -X DELETE http://localhost:8000/tasks/1
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_tasks.py -v

# Run with coverage
pytest --cov=app
```

## Project Structure

```
mini-task-tracker/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI app, endpoints, and UI
│   └── models.py      # Pydantic models
├── tests/
│   ├── __init__.py
│   ├── test_health.py # Health endpoint tests
│   ├── test_tasks.py  # Task CRUD tests
│   └── test_ui.py     # UI endpoint tests
├── requirements.txt
└── README.md
```

## Feature Backlog

The following features are intentionally left for future implementation:

- Pagination and filtering for task listing
- Task categories/tags
- Due dates and priorities
- Persistent storage (database integration)
- User authentication

Each feature should be implemented as an extension of the existing codebase.


from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, List

from app.models import Task, TaskCreate, TaskUpdate, TaskStatus

app = FastAPI(title="Mini Task Tracker", version="1.0.0")


# HTML template for the UI
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mini Task Tracker</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover { background: #0056b3; }
        .task-list {
            list-style: none;
            padding: 0;
        }
        .task-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .task-title {
            font-weight: bold;
            font-size: 1.1em;
        }
        .task-status {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-left: 10px;
        }
        .status-pending { background: #ffc107; color: #000; }
        .status-in_progress { background: #17a2b8; color: #fff; }
        .status-done { background: #28a745; color: #fff; }
        .task-description {
            color: #666;
            margin-top: 5px;
        }
        .task-id {
            color: #999;
            font-size: 0.85em;
        }
        .empty-message {
            color: #666;
            font-style: italic;
        }
        #create-form {
            background: white;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <h1>Mini Task Tracker</h1>
    
    <div id="create-form">
        <h2>Create New Task</h2>
        <form id="taskForm">
            <div class="form-group">
                <label for="title">Title *</label>
                <input type="text" id="title" name="title" required>
            </div>
            <div class="form-group">
                <label for="description">Description</label>
                <input type="text" id="description" name="description">
            </div>
            <div class="form-group">
                <label for="status">Status</label>
                <select id="status" name="status">
                    <option value="pending">Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="done">Done</option>
                </select>
            </div>
            <button type="submit">Create Task</button>
        </form>
    </div>
    
    <h2>Tasks</h2>
    <ul id="taskList" class="task-list">
        <li class="empty-message">Loading tasks...</li>
    </ul>
    
    <script>
        async function loadTasks() {
            try {
                const response = await fetch('/tasks');
                const tasks = await response.json();
                const taskList = document.getElementById('taskList');
                
                if (tasks.length === 0) {
                    taskList.innerHTML = '<li class="empty-message">No tasks yet. Create one above!</li>';
                    return;
                }
                
                taskList.innerHTML = tasks.map(task => `
                    <li class="task-item">
                        <span class="task-id">#${task.id}</span>
                        <span class="task-title">${escapeHtml(task.title)}</span>
                        <span class="task-status status-${task.status}">${task.status.replace('_', ' ')}</span>
                        ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
                    </li>
                `).join('');
            } catch (error) {
                console.error('Failed to load tasks:', error);
                document.getElementById('taskList').innerHTML = 
                    '<li class="empty-message">Failed to load tasks.</li>';
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        document.getElementById('taskForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                title: document.getElementById('title').value,
                description: document.getElementById('description').value || null,
                status: document.getElementById('status').value
            };
            
            try {
                const response = await fetch('/tasks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    document.getElementById('taskForm').reset();
                    await loadTasks();
                } else {
                    const error = await response.json();
                    alert('Failed to create task: ' + JSON.stringify(error.detail));
                }
            } catch (error) {
                console.error('Failed to create task:', error);
                alert('Failed to create task.');
            }
        });
        
        // Load tasks on page load
        loadTasks();
    </script>
</body>
</html>
"""

# In-memory storage for tasks
tasks_db: Dict[int, Task] = {}
task_id_counter: int = 0


def get_next_id() -> int:
    """Generate the next unique task ID."""
    global task_id_counter
    task_id_counter += 1
    return task_id_counter


def reset_db() -> None:
    """Reset the database (useful for testing)."""
    global tasks_db, task_id_counter
    tasks_db = {}
    task_id_counter = 0


@app.get("/", response_class=HTMLResponse)
def home():
    """Serve the main UI page."""
    return HTML_PAGE


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task_data: TaskCreate) -> Task:
    """Create a new task."""
    task_id = get_next_id()
    task = Task(
        id=task_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status
    )
    tasks_db[task_id] = task
    return task


@app.get("/tasks", response_model=List[Task])
def list_tasks() -> List[Task]:
    """Get all tasks."""
    return list(tasks_db.values())


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    """Get a specific task by ID."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_data: TaskUpdate) -> Task:
    """Update an existing task."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    existing_task = tasks_db[task_id]
    update_data = task_data.model_dump(exclude_unset=True)
    
    updated_task = Task(
        id=existing_task.id,
        title=update_data.get("title", existing_task.title),
        description=update_data.get("description", existing_task.description),
        status=update_data.get("status", existing_task.status)
    )
    tasks_db[task_id] = updated_task
    return updated_task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    """Delete a task."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    return None

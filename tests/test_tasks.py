import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    """Reset database before each test."""
    reset_db()
    yield
    reset_db()


class TestCreateTask:
    """Tests for POST /tasks endpoint."""

    def test_create_task_minimal(self):
        """Create a task with only title."""
        response = client.post("/tasks", json={"title": "Test Task"})
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Test Task"
        assert data["description"] is None
        assert data["status"] == "pending"

    def test_create_task_full(self):
        """Create a task with all fields."""
        response = client.post("/tasks", json={
            "title": "Full Task",
            "description": "A detailed description",
            "status": "in_progress"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Full Task"
        assert data["description"] == "A detailed description"
        assert data["status"] == "in_progress"

    def test_create_task_invalid_status(self):
        """Creating a task with invalid status should fail."""
        response = client.post("/tasks", json={
            "title": "Bad Task",
            "status": "invalid_status"
        })
        assert response.status_code == 422

    def test_create_task_missing_title(self):
        """Creating a task without title should fail."""
        response = client.post("/tasks", json={"description": "No title"})
        assert response.status_code == 422

    def test_create_multiple_tasks_increments_id(self):
        """Each new task should get a unique incremented ID."""
        response1 = client.post("/tasks", json={"title": "Task 1"})
        response2 = client.post("/tasks", json={"title": "Task 2"})
        assert response1.json()["id"] == 1
        assert response2.json()["id"] == 2


class TestListTasks:
    """Tests for GET /tasks endpoint."""

    def test_list_tasks_empty(self):
        """Listing tasks when none exist returns empty list."""
        response = client.get("/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_tasks_with_data(self):
        """Listing tasks returns all created tasks."""
        client.post("/tasks", json={"title": "Task 1"})
        client.post("/tasks", json={"title": "Task 2"})
        
        response = client.get("/tasks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Task 1"
        assert data[1]["title"] == "Task 2"


class TestGetTask:
    """Tests for GET /tasks/{id} endpoint."""

    def test_get_task_success(self):
        """Get an existing task by ID."""
        create_response = client.post("/tasks", json={"title": "My Task"})
        task_id = create_response.json()["id"]
        
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "My Task"

    def test_get_task_not_found(self):
        """Getting a non-existent task returns 404."""
        response = client.get("/tasks/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"


class TestUpdateTask:
    """Tests for PUT /tasks/{id} endpoint."""

    def test_update_task_title(self):
        """Update only the title of a task."""
        client.post("/tasks", json={"title": "Original"})
        
        response = client.put("/tasks/1", json={"title": "Updated"})
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"

    def test_update_task_status(self):
        """Update the status of a task."""
        client.post("/tasks", json={"title": "Task"})
        
        response = client.put("/tasks/1", json={"status": "done"})
        assert response.status_code == 200
        assert response.json()["status"] == "done"

    def test_update_task_all_fields(self):
        """Update all fields of a task."""
        client.post("/tasks", json={"title": "Task"})
        
        response = client.put("/tasks/1", json={
            "title": "New Title",
            "description": "New Description",
            "status": "in_progress"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "New Description"
        assert data["status"] == "in_progress"

    def test_update_task_not_found(self):
        """Updating a non-existent task returns 404."""
        response = client.put("/tasks/999", json={"title": "Updated"})
        assert response.status_code == 404

    def test_update_task_invalid_status(self):
        """Updating with invalid status should fail."""
        client.post("/tasks", json={"title": "Task"})
        
        response = client.put("/tasks/1", json={"status": "bad_status"})
        assert response.status_code == 422

    def test_update_task_preserves_unset_fields(self):
        """Updating some fields preserves other fields."""
        client.post("/tasks", json={
            "title": "Original",
            "description": "Original Description",
            "status": "pending"
        })
        
        # Update only title
        response = client.put("/tasks/1", json={"title": "Updated Title"})
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Original Description"
        assert data["status"] == "pending"


class TestDeleteTask:
    """Tests for DELETE /tasks/{id} endpoint."""

    def test_delete_task_success(self):
        """Delete an existing task."""
        client.post("/tasks", json={"title": "To Delete"})
        
        response = client.delete("/tasks/1")
        assert response.status_code == 204
        
        # Verify task is gone
        get_response = client.get("/tasks/1")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self):
        """Deleting a non-existent task returns 404."""
        response = client.delete("/tasks/999")
        assert response.status_code == 404


class TestStatusValidation:
    """Tests for status validation."""

    def test_valid_status_pending(self):
        """Status 'pending' is valid."""
        response = client.post("/tasks", json={"title": "Task", "status": "pending"})
        assert response.status_code == 201
        assert response.json()["status"] == "pending"

    def test_valid_status_in_progress(self):
        """Status 'in_progress' is valid."""
        response = client.post("/tasks", json={"title": "Task", "status": "in_progress"})
        assert response.status_code == 201
        assert response.json()["status"] == "in_progress"

    def test_valid_status_done(self):
        """Status 'done' is valid."""
        response = client.post("/tasks", json={"title": "Task", "status": "done"})
        assert response.status_code == 201
        assert response.json()["status"] == "done"

    def test_invalid_status_rejected(self):
        """Invalid status values are rejected."""
        response = client.post("/tasks", json={"title": "Task", "status": "completed"})
        assert response.status_code == 422

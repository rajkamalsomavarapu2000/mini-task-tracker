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


def test_home_returns_html():
    """GET / returns status 200 and Content-Type includes text/html."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_home_contains_expected_html_marker():
    """GET / response body contains expected HTML title."""
    response = client.get("/")
    assert "<title>Mini Task Tracker</title>" in response.text


def test_home_contains_status_dropdown_function():
    """GET / response contains the renderStatusDropdown JavaScript function."""
    response = client.get("/")
    assert "renderStatusDropdown" in response.text
    assert "task-status-select" in response.text


def test_home_contains_update_status_function():
    """GET / response contains the updateTaskStatus JavaScript function."""
    response = client.get("/")
    assert "updateTaskStatus" in response.text
    assert "PATCH" in response.text
    assert "/status" in response.text


def test_status_dropdown_options_in_html():
    """GET / response contains all status options for dropdowns."""
    response = client.get("/")
    html = response.text
    # Verify status options are defined in the renderStatusDropdown function
    assert "'todo'" in html or '"todo"' in html
    assert "'in_progress'" in html or '"in_progress"' in html
    assert "'done'" in html or '"done"' in html
    assert "To Do" in html
    assert "In Progress" in html
    assert "Done" in html


class TestTaskListStatusDropdown:
    """Tests to verify status dropdown is rendered for tasks."""

    def test_task_list_endpoint_returns_task_with_status(self):
        """Creating a task returns it with status for dropdown rendering."""
        # Create a task
        create_response = client.post("/tasks", json={"title": "Test Task"})
        assert create_response.status_code == 201
        task = create_response.json()
        assert task["status"] == "todo"
        
        # Get tasks list
        list_response = client.get("/tasks")
        assert list_response.status_code == 200
        tasks = list_response.json()
        assert len(tasks) == 1
        assert tasks[0]["id"] == task["id"]
        assert tasks[0]["status"] == "todo"

    def test_patch_status_updates_task_for_ui(self):
        """PATCH /tasks/{id}/status updates status which UI can reflect."""
        # Create a task
        create_response = client.post("/tasks", json={"title": "UI Task"})
        task_id = create_response.json()["id"]
        
        # Update status via PATCH (simulating dropdown change)
        patch_response = client.patch(
            f"/tasks/{task_id}/status",
            json={"status": "in_progress"}
        )
        assert patch_response.status_code == 200
        assert patch_response.json()["status"] == "in_progress"
        
        # Verify the task list reflects the updated status
        list_response = client.get("/tasks")
        tasks = list_response.json()
        assert tasks[0]["status"] == "in_progress"

    def test_patch_status_to_done_updates_task(self):
        """Changing status to done via PATCH is reflected in task list."""
        # Create a task
        client.post("/tasks", json={"title": "Complete Me"})
        
        # Update to done
        patch_response = client.patch("/tasks/1/status", json={"status": "done"})
        assert patch_response.status_code == 200
        
        # Verify via GET
        get_response = client.get("/tasks/1")
        assert get_response.json()["status"] == "done"

    def test_ui_has_css_for_status_dropdown(self):
        """UI contains CSS styling for status dropdown."""
        response = client.get("/")
        html = response.text
        assert ".task-status-select" in html
        assert ".task-status-select:disabled" in html

    def test_ui_has_error_handling_css(self):
        """UI contains CSS for error messages."""
        response = client.get("/")
        assert ".task-error" in response.text

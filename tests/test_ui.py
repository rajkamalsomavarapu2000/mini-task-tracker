from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home_returns_html():
    """GET / returns status 200 and Content-Type includes text/html."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_home_contains_expected_html_marker():
    """GET / response body contains expected HTML title."""
    response = client.get("/")
    assert "<title>Mini Task Tracker</title>" in response.text

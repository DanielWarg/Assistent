"""
Test health endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Jarvis Core API"
    assert data["status"] == "running"


def test_health_live():
    """Test health live endpoint."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_health_ready():
    """Test health ready endpoint."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    assert "timestamp" in data


def test_info_endpoint():
    """Test info endpoint."""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jarvis Core"
    assert data["version"] == "0.1.0"
    assert "environment" in data
    assert "debug" in data

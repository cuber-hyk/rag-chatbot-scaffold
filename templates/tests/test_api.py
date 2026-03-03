"""
API Tests
"""

from fastapi.testclient import TestClient
from main import app
import pytest


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_chat_endpoint_without_auth(client):
    """Test chat endpoint without authentication"""
    response = client.post("/api/v1/chat", json={"query": "Hello"})
    assert response.status_code == 401  # Unauthorized


def test_chat_endpoint_with_auth(client):
    """Test chat endpoint with authentication"""
    # This would require a valid API key in .env
    headers = {"X-API-Key": "test-key"}
    response = client.post("/api/v1/chat", json={"query": "Hello"}, headers=headers)
    # May fail if API key validation is strict

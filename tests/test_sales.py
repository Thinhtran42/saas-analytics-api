import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test basic health check"""
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_generate_fake_sales():
    """Test fake sales data generation"""
    response = client.post("/sales-data/generate-fake?count=5")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["count"] == 5

def test_read_sales_data():
    """Test reading sales data"""
    response = client.get("/sales-data/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
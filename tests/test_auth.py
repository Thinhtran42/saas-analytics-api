import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    """Test user registration"""
    response = client.post(
        "/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    assert "id" in response.json()

def test_login_user():
    """Test user login"""
    # First register
    client.post(
        "/register",
        json={"email": "login@example.com", "password": "testpass123"}
    )

    # Then login
    response = client.post(
        "/login",
        data={"username": "login@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_invalid_login():
    """Test login with invalid credentials"""
    response = client.post(
        "/login",
        data={"username": "wrong@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 400
# tests/test_users.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_user():
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass",
        },
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"


def test_login():
    client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass",
        },
    )
    response = client.post(
        "/users/login", data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

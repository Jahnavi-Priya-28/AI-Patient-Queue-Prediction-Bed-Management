import pytest


def test_register_and_login(client):
    # 1. Register Patient User
    register_payload = {
        "email": "testpatient@example.com",
        "password": "SecurePassword123!",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "role": "PATIENT"
    }
    response = client.post("/api/auth/register", json=register_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testpatient@example.com"
    assert data["role"] == "PATIENT"

    # 2. Login User
    login_payload = {
        "email": "testpatient@example.com",
        "password": "SecurePassword123!"
    }
    login_res = client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["user"]["email"] == "testpatient@example.com"

    # 3. Test /me endpoint with Bearer Token
    access_token = token_data["access_token"]
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "testpatient@example.com"


def test_duplicate_registration_fails(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "SecurePassword123!",
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "PATIENT"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_invalid_login_password(client):
    payload = {
        "email": "wrongpw@example.com",
        "password": "CorrectPassword123!",
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "PATIENT"
    }
    client.post("/api/auth/register", json=payload)

    login_res = client.post("/api/auth/login", json={"email": "wrongpw@example.com", "password": "WrongPassword!"})
    assert login_res.status_code == 401
    assert "Invalid email or password" in login_res.json()["detail"]

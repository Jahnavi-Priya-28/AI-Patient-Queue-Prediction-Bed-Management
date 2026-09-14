from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.organization import Organization
from app.models.user import User
from tests.conftest import TestingSessionLocal


def _seed_org(name="Test Hospital", slug="test-hospital"):
    db = TestingSessionLocal()
    org = db.query(Organization).filter(Organization.slug == slug).first()
    if not org:
        org = Organization(name=name, slug=slug, is_active=True)
        db.add(org)
        db.commit()
        db.refresh(org)
    org_id = org.id
    db.close()
    return org_id


def _seed_user(email, role, password="SecurePassword123!", active=True, org_id=None):
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            organization_id=org_id,
            email=email,
            password_hash=hash_password(password),
            role=role,
            first_name="Test",
            last_name=role.value.title(),
            is_active=active,
        )
        db.add(user)
    else:
        user.organization_id = org_id
        user.role = role
        user.is_active = active
    db.commit()
    db.close()


def test_register_creates_patient_and_login_uses_email_password(client):
    response = client.post("/api/auth/register", json={
        "email": "testpatient@example.com",
        "password": "SecurePassword123!",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "role": "SUPER_ADMIN",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testpatient@example.com"
    assert data["role"] == "PATIENT"
    assert data["organization_id"] is not None
    assert "login_id" not in data

    login_res = client.post("/api/auth/login", json={"email": "testpatient@example.com", "password": "SecurePassword123!"})
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["user"]["role"] == "PATIENT"

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_data['access_token']}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "testpatient@example.com"


def test_duplicate_registration_fails(client):
    payload = {"email": "duplicate@example.com", "password": "SecurePassword123!", "first_name": "Jane", "last_name": "Doe"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_invalid_login_password(client):
    client.post("/api/auth/register", json={"email": "wrongpw@example.com", "password": "CorrectPassword123!", "first_name": "Jane", "last_name": "Doe"})
    login_res = client.post("/api/auth/login", json={"email": "wrongpw@example.com", "password": "WrongPassword!"})
    assert login_res.status_code == 401
    assert "Invalid email or password" in login_res.json()["detail"]


def test_inactive_account_rejected(client):
    org_id = _seed_org("Inactive Hospital", "inactive-hospital")
    _seed_user("inactive@example.com", UserRole.PATIENT, active=False, org_id=org_id)
    login_res = client.post("/api/auth/login", json={"email": "inactive@example.com", "password": "SecurePassword123!"})
    assert login_res.status_code == 403
    assert "inactive" in login_res.json()["detail"].lower()


def test_hospital_admin_can_create_staff_in_own_org(client):
    org_id = _seed_org("Admin Hospital", "admin-hospital")
    _seed_user("admin@example.com", UserRole.HOSPITAL_ADMIN, org_id=org_id)
    login_res = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "SecurePassword123!"})
    token = login_res.json()["access_token"]

    response = client.post(
        "/api/auth/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": "RECEPTIONIST", "email": "reception@example.com", "password": "SecurePassword123!", "first_name": "Riya", "last_name": "Reception"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "RECEPTIONIST"
    assert response.json()["organization_id"] == org_id


def test_patient_and_doctor_cannot_create_admin_users(client):
    org_id = _seed_org("RBAC Hospital", "rbac-hospital")
    _seed_user("doctor@example.com", UserRole.DOCTOR, org_id=org_id)
    login_res = client.post("/api/auth/login", json={"email": "doctor@example.com", "password": "SecurePassword123!"})
    token = login_res.json()["access_token"]
    response = client.post(
        "/api/auth/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": "HOSPITAL_ADMIN", "email": "bad-admin@example.com", "password": "SecurePassword123!", "first_name": "Bad", "last_name": "Admin"},
    )
    assert response.status_code == 403

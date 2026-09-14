from app.core.security import hash_password
from app.models.department import Department
from app.models.enums import UserRole
from app.models.organization import Organization
from app.models.user import User
from tests.conftest import TestingSessionLocal


def _seed_org(name="Domain Hospital", slug="domain-hospital"):
    db = TestingSessionLocal()
    org = db.query(Organization).filter(Organization.slug == slug).first()
    if not org:
        org = Organization(name=f"{name} {slug}", slug=slug, is_active=True)
        db.add(org)
        db.commit()
        db.refresh(org)
    org_id = org.id
    db.close()
    return org_id


def _auth_headers(client, email="domain.admin@example.com", role=UserRole.HOSPITAL_ADMIN, org_slug="domain-hospital"):
    org_id = _seed_org(slug=org_slug)
    db = TestingSessionLocal()
    if not db.query(User).filter(User.email == email).first():
        db.add(User(
            organization_id=org_id,
            email=email,
            password_hash=hash_password("SecurePassword123!"),
            role=role,
            first_name="Test",
            last_name="User",
            is_active=True,
        ))
        db.commit()
    db.close()
    login = client.post("/api/auth/login", json={"email": email, "password": "SecurePassword123!"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}, org_id


def test_list_departments_is_org_scoped(client):
    headers, org_id = _auth_headers(client)
    other_org_id = _seed_org("Other Hospital", "other-hospital")
    db = TestingSessionLocal()
    db.add(Department(organization_id=org_id, name="Test Cardiology", code="CARD", description="Cardiology Test", active=True))
    db.add(Department(organization_id=other_org_id, name="Other Oncology", code="ONC", description="Other hospital", active=True))
    db.commit()
    db.close()

    response = client.get("/api/departments", headers=headers)
    assert response.status_code == 200
    codes = {item["code"] for item in response.json()}
    assert "CARD" in codes
    assert "ONC" not in codes


def test_list_doctors_requires_authenticated_user(client):
    unauthenticated = client.get("/api/doctors")
    assert unauthenticated.status_code == 401

    headers, _ = _auth_headers(client, "doctor.list.admin@example.com", org_slug="doctor-list-hospital")
    response = client.get("/api/doctors", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_beds_requires_staff_role(client):
    unauthenticated = client.get("/api/beds")
    assert unauthenticated.status_code == 401


def test_dashboard_analytics_requires_staff_role(client):
    patient = client.post("/api/auth/register", json={
        "email": "analytics.patient@example.com",
        "password": "SecurePassword123!",
        "first_name": "Pat",
        "last_name": "Analytics",
    }).json()
    patient_login = client.post("/api/auth/login", json={"email": patient["email"], "password": "SecurePassword123!"}).json()
    patient_res = client.get("/api/analytics/dashboard-metrics", headers={"Authorization": f"Bearer {patient_login['access_token']}"})
    assert patient_res.status_code == 403

    headers, _ = _auth_headers(client, "metrics.admin@example.com", org_slug="metrics-hospital")
    response = client.get("/api/analytics/dashboard-metrics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_patients" in data
    assert "waiting_patients" in data
    assert "available_beds" in data


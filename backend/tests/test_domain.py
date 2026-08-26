import pytest
from app.models.department import Department
from tests.conftest import TestingSessionLocal


def test_list_departments(client):
    # Seed department
    db = TestingSessionLocal()
    dept = Department(name="Test Cardiology", code="CARD", description="Cardiology Test", active=True)
    db.add(dept)
    db.commit()
    db.close()

    response = client.get("/api/departments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["code"] == "CARD"


def test_list_doctors(client):
    response = client.get("/api/doctors")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_beds(client):
    response = client.get("/api/beds")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dashboard_analytics(client):
    response = client.get("/api/analytics/dashboard-metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_patients" in data
    assert "waiting_patients" in data
    assert "available_beds" in data

"""Tests for /patients endpoints."""
import uuid
from datetime import datetime, UTC

import pytest

from app.db.models import TimelineEvent as DBTimelineEvent
from app.services.abha import validate_abha_format

# ── helpers ───────────────────────────────────────────────────────────────────

BASE_PAYLOAD = {
    "family_name": "Sharma",
    "given_names": ["Raj", "Kumar"],
    "dob": "1985-03-15",
    "gender": "male",
    "blood_group": "O+",
    "abha_id": "12-3456-7890-1234",
    "emergency_contact": {
        "name": "Priya Sharma",
        "relationship": "spouse",
        "phone": "+919876543210",
    },
}

PRACTITIONER_PAYLOAD = {
    "family_name": "Kapoor",
    "given_names": ["Arun"],
    "specialty": "Cardiology",
    "registration_number": "MCI-12345",
}


async def _register(client, overrides: dict = {}) -> dict:
    return await client.post("/patients/register", json={**BASE_PAYLOAD, **overrides})


async def _register_practitioner(client) -> str:
    resp = await client.post("/practitioners/register", json=PRACTITIONER_PAYLOAD)
    assert resp.status_code == 201
    return resp.json()["id"]


# ── ABHA format unit tests ────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "abha_id,expected",
    [
        ("12-3456-7890-1234", True),
        ("00-0000-0000-0000", True),
        ("1-3456-7890-1234", False),
        ("12-345-7890-1234", False),
        ("AB-3456-7890-1234", False),
        ("123456789012345", False),
        ("", False),
    ],
)
def test_abha_format_validation(abha_id, expected):
    assert validate_abha_format(abha_id) == expected


# ── POST /patients/register ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_success(client):
    resp = await _register(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["abha_id"] == "12-3456-7890-1234"
    assert data["family_name"] == "Sharma"
    assert data["given_names"] == ["Raj", "Kumar"]
    assert data["gender"] == "male"
    assert data["blood_group"] == "O+"
    assert data["active"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_register_without_abha(client):
    resp = await _register(client, {"abha_id": None})
    assert resp.status_code == 201
    assert resp.json()["abha_id"] is None


@pytest.mark.asyncio
async def test_register_minimal(client):
    payload = {
        "family_name": "Patel",
        "given_names": ["Anita"],
        "dob": "1990-07-01",
        "gender": "female",
    }
    resp = await client.post("/patients/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["blood_group"] is None
    assert data["emergency_contact"] is None


@pytest.mark.asyncio
async def test_register_duplicate_abha(client):
    await _register(client)
    resp = await _register(client)
    assert resp.status_code == 409
    assert "ABHA ID already registered" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_abha_format(client):
    resp = await _register(client, {"abha_id": "not-valid"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_gender(client):
    resp = await _register(client, {"gender": "alien"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_emergency_contact_persisted(client):
    contact = (await _register(client)).json()["emergency_contact"]
    assert contact["name"] == "Priya Sharma"
    assert contact["relationship"] == "spouse"
    assert contact["phone"] == "+919876543210"


@pytest.mark.asyncio
async def test_register_with_valid_cardiologist(client):
    practitioner_id = await _register_practitioner(client)
    resp = await _register(client, {"primary_cardiologist_id": practitioner_id})
    assert resp.status_code == 201
    assert resp.json()["primary_cardiologist_id"] == practitioner_id


@pytest.mark.asyncio
async def test_register_with_nonexistent_cardiologist(client):
    resp = await _register(client, {"primary_cardiologist_id": str(uuid.uuid4())})
    assert resp.status_code == 422
    assert "Practitioner not found" in resp.json()["detail"]


# ── GET /patients/{id} ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_patient_success(client):
    patient_id = (await _register(client)).json()["id"]
    resp = await client.get(f"/patients/{patient_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == patient_id
    assert resp.json()["family_name"] == "Sharma"


@pytest.mark.asyncio
async def test_get_patient_not_found(client):
    resp = await client.get(f"/patients/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_patient_profile_roundtrip(client):
    created = (await _register(client)).json()
    fetched = (await client.get(f"/patients/{created['id']}")).json()
    for field in ("abha_id", "family_name", "given_names", "gender", "blood_group", "active"):
        assert fetched[field] == created[field]


# ── GET /patients/by-abha/{abha_id} ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_by_abha_success(client):
    created = (await _register(client)).json()
    resp = await client.get("/patients/by-abha/12-3456-7890-1234")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


@pytest.mark.asyncio
async def test_get_by_abha_not_found(client):
    resp = await client.get("/patients/by-abha/99-9999-9999-9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_by_abha_patient_without_abha_not_reachable(client):
    await _register(client, {"abha_id": None})
    resp = await client.get("/patients/by-abha/12-3456-7890-0000")
    assert resp.status_code == 404


# ── GET /patients/{id}/timeline ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_timeline_empty(client):
    patient_id = (await _register(client)).json()["id"]
    resp = await client.get(f"/patients/{patient_id}/timeline")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_timeline_not_found(client):
    resp = await client.get(f"/patients/{uuid.uuid4()}/timeline")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_timeline_with_events(client, db_session):
    patient_id = (await _register(client)).json()["id"]

    events = [
        DBTimelineEvent(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            event_type="lab",
            timestamp=datetime(2024, 1, 10, 9, 0, 0),
            source_service="lab-service",
            structured_data={"hba1c": 6.2},
            summary_text="HbA1c 6.2%",
        ),
        DBTimelineEvent(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            event_type="ecg",
            timestamp=datetime(2024, 1, 15, 14, 30, 0),
            source_service="avhita-ai",
            structured_data={"rhythm": "NSR", "hr_bpm": 72},
            summary_text="Normal sinus rhythm",
        ),
        DBTimelineEvent(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            event_type="alert",
            timestamp=datetime(2024, 1, 8, 6, 0, 0),
            source_service="rpm-bridge",
            structured_data={"spo2": 91},
            summary_text="SpO2 below threshold",
        ),
    ]
    for e in events:
        db_session.add(e)
    await db_session.commit()

    resp = await client.get(f"/patients/{patient_id}/timeline")
    items = resp.json()
    assert len(items) == 3
    assert items[0]["event_type"] == "alert"   # earliest timestamp
    assert items[1]["event_type"] == "lab"
    assert items[2]["event_type"] == "ecg"
    assert items[1]["structured_data"]["hba1c"] == 6.2


# ── POST /patients/{id}/timeline ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_timeline_event(client):
    patient_id = (await _register(client)).json()["id"]
    payload = {
        "event_type": "ecg",
        "timestamp": "2024-03-01T10:00:00",
        "source_service": "rpm-bridge",
        "structured_data": {"ecg_label": "Normal", "confidence": 0.97},
        "summary_text": "ECG: Normal (confidence: 97%)",
    }
    resp = await client.post(f"/patients/{patient_id}/timeline", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["event_type"] == "ecg"
    assert data["patient_id"] == patient_id
    assert data["source_service"] == "rpm-bridge"
    assert data["structured_data"]["confidence"] == 0.97
    assert "id" in data


@pytest.mark.asyncio
async def test_create_timeline_event_patient_not_found(client):
    payload = {
        "event_type": "lab",
        "timestamp": "2024-03-01T10:00:00",
        "source_service": "lab-service",
    }
    resp = await client.post(f"/patients/{uuid.uuid4()}/timeline", json=payload)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_timeline_event_invalid_type(client):
    patient_id = (await _register(client)).json()["id"]
    payload = {
        "event_type": "bloodtest",  # not a valid EventTypeEnum
        "timestamp": "2024-03-01T10:00:00",
        "source_service": "lab-service",
    }
    resp = await client.post(f"/patients/{patient_id}/timeline", json=payload)
    assert resp.status_code == 422

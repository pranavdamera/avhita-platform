"""Tests for /practitioners endpoints."""
import uuid

import pytest

VALID_PAYLOAD = {
    "family_name": "Kapoor",
    "given_names": ["Arun", "Singh"],
    "specialty": "Cardiology",
    "registration_number": "MCI-99001",
    "qualification": ["MBBS", "MD", "DM Cardiology"],
}


async def _register(client, overrides: dict = {}) -> dict:
    return await client.post("/practitioners/register", json={**VALID_PAYLOAD, **overrides})


# ── POST /practitioners/register ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_success(client):
    resp = await _register(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["family_name"] == "Kapoor"
    assert data["given_names"] == ["Arun", "Singh"]
    assert data["specialty"] == "Cardiology"
    assert data["registration_number"] == "MCI-99001"
    assert data["qualification"] == ["MBBS", "MD", "DM Cardiology"]
    assert data["active"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_register_minimal(client):
    payload = {
        "family_name": "Mehta",
        "given_names": ["Rohit"],
    }
    resp = await client.post("/practitioners/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["registration_number"] is None
    assert data["specialty"] is None
    assert data["qualification"] is None


@pytest.mark.asyncio
async def test_register_duplicate_registration_number(client):
    await _register(client)
    resp = await _register(client)
    assert resp.status_code == 409
    assert "Registration number already exists" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_register_two_practitioners_no_reg_number(client):
    # Two practitioners without reg number should both succeed (nullable unique)
    p1 = await _register(client, {"registration_number": None})
    p2 = await _register(client, {"registration_number": None})
    assert p1.status_code == 201
    assert p2.status_code == 201
    assert p1.json()["id"] != p2.json()["id"]


# ── GET /practitioners/{id} ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_practitioner_success(client):
    practitioner_id = (await _register(client)).json()["id"]
    resp = await client.get(f"/practitioners/{practitioner_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == practitioner_id
    assert data["specialty"] == "Cardiology"


@pytest.mark.asyncio
async def test_get_practitioner_not_found(client):
    resp = await client.get(f"/practitioners/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_practitioner_roundtrip(client):
    created = (await _register(client)).json()
    fetched = (await client.get(f"/practitioners/{created['id']}")).json()
    for field in ("family_name", "given_names", "specialty", "registration_number", "active"):
        assert fetched[field] == created[field]

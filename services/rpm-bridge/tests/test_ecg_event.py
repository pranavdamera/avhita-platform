"""Tests for POST /rpm-bridge/ecg-event."""
import pytest

VALID_PAYLOAD = {
    "patient_abha_id": "12-3456-7890-1234",
    "ecg_label": "Normal",
    "confidence": 0.97,
    "alert": False,
    "features": {"hr_bpm": 72, "pr_interval_ms": 160, "qrs_duration_ms": 90},
    "timestamp": "2024-01-15T10:30:00",
}


# ── Happy path ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ecg_event_success(client_with_patient):
    client, mock = client_with_patient
    resp = await client.post("/rpm-bridge/ecg-event", json=VALID_PAYLOAD)

    assert resp.status_code == 201
    data = resp.json()
    assert data["ecg_label"] == "Normal"
    assert data["alert"] is False
    assert data["summary_text"] == "ECG: Normal (confidence: 97%)"
    assert "timeline_event_id" in data
    assert "patient_id" in data


@pytest.mark.asyncio
async def test_ecg_event_calls_ehr_by_abha(client_with_patient):
    client, mock = client_with_patient
    await client.post("/rpm-bridge/ecg-event", json=VALID_PAYLOAD)

    abha_calls = [c for c in mock.calls if c[0] == "get_patient_by_abha"]
    assert len(abha_calls) == 1
    assert abha_calls[0][1] == "12-3456-7890-1234"


@pytest.mark.asyncio
async def test_ecg_event_creates_timeline_event(client_with_patient):
    client, mock = client_with_patient
    await client.post("/rpm-bridge/ecg-event", json=VALID_PAYLOAD)

    timeline_calls = [c for c in mock.calls if c[0] == "create_timeline_event"]
    assert len(timeline_calls) == 1
    _, patient_id, event = timeline_calls[0]
    assert event["event_type"] == "ecg"
    assert event["source_service"] == "rpm-bridge"
    assert event["structured_data"]["ecg_label"] == "Normal"
    assert event["structured_data"]["confidence"] == 0.97
    assert event["structured_data"]["features"]["hr_bpm"] == 72


@pytest.mark.asyncio
async def test_ecg_alert_prefixes_summary(client_with_patient):
    client, mock = client_with_patient
    resp = await client.post(
        "/rpm-bridge/ecg-event",
        json={**VALID_PAYLOAD, "ecg_label": "AFib", "confidence": 0.93, "alert": True},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["alert"] is True
    assert data["summary_text"].startswith("[ALERT]")
    assert "AFib" in data["summary_text"]
    assert "93%" in data["summary_text"]


@pytest.mark.asyncio
async def test_ecg_event_empty_features(client_with_patient):
    client, _ = client_with_patient
    resp = await client.post(
        "/rpm-bridge/ecg-event",
        json={**VALID_PAYLOAD, "features": {}},
    )
    assert resp.status_code == 201


# ── Validation errors ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_invalid_abha_format(client_with_patient):
    client, _ = client_with_patient
    resp = await client.post(
        "/rpm-bridge/ecg-event",
        json={**VALID_PAYLOAD, "patient_abha_id": "not-valid"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_confidence_above_one(client_with_patient):
    client, _ = client_with_patient
    resp = await client.post(
        "/rpm-bridge/ecg-event",
        json={**VALID_PAYLOAD, "confidence": 1.1},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_confidence_below_zero(client_with_patient):
    client, _ = client_with_patient
    resp = await client.post(
        "/rpm-bridge/ecg-event",
        json={**VALID_PAYLOAD, "confidence": -0.01},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_missing_required_fields(client_with_patient):
    client, _ = client_with_patient
    resp = await client.post("/rpm-bridge/ecg-event", json={"patient_abha_id": "12-3456-7890-1234"})
    assert resp.status_code == 422


# ── Patient not found ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_patient_not_found(client_no_patient):
    client, _ = client_no_patient
    resp = await client.post("/rpm-bridge/ecg-event", json=VALID_PAYLOAD)
    assert resp.status_code == 404
    assert "12-3456-7890-1234" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_patient_not_found_no_timeline_call(client_no_patient):
    client, mock = client_no_patient
    await client.post("/rpm-bridge/ecg-event", json=VALID_PAYLOAD)
    timeline_calls = [c for c in mock.calls if c[0] == "create_timeline_event"]
    assert len(timeline_calls) == 0


# ── Health check ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health(client_with_patient):
    client, _ = client_with_patient
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "rpm-bridge"

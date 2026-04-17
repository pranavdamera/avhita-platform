import uuid
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.services.clinic_ehr import get_clinic_ehr_client
from main import app

# ── Mock clinic-ehr client ────────────────────────────────────────────────────

class MockClinicEHRClient:
    def __init__(
        self,
        patient: dict[str, Any] | None = None,
        created_event: dict[str, Any] | None = None,
    ):
        self.patient = patient
        self.created_event = created_event or {
            "id": str(uuid.uuid4()),
            "patient_id": patient["id"] if patient else str(uuid.uuid4()),
            "event_type": "ecg",
            "timestamp": "2024-01-01T00:00:00",
            "source_service": "rpm-bridge",
            "structured_data": {},
            "summary_text": "",
        }
        self.calls: list[tuple] = []

    async def get_patient_by_abha(self, abha_id: str) -> dict[str, Any] | None:
        self.calls.append(("get_patient_by_abha", abha_id))
        return self.patient

    async def create_timeline_event(
        self, patient_id: str, event: dict[str, Any]
    ) -> dict[str, Any]:
        self.calls.append(("create_timeline_event", patient_id, event))
        return self.created_event


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_client_fixture(mock_ehr: MockClinicEHRClient):
    app.dependency_overrides[get_clinic_ehr_client] = lambda: mock_ehr

    async def _inner():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac
        app.dependency_overrides.clear()

    return _inner


SAMPLE_PATIENT = {
    "id": str(uuid.uuid4()),
    "abha_id": "12-3456-7890-1234",
    "family_name": "Sharma",
    "given_names": ["Raj"],
    "dob": "1985-03-15",
    "gender": "male",
}

SAMPLE_EVENT_ID = str(uuid.uuid4())


@pytest_asyncio.fixture
async def client_with_patient():
    """Client where clinic-ehr returns a valid patient and accepts timeline events."""
    patient = {**SAMPLE_PATIENT}
    mock = MockClinicEHRClient(
        patient=patient,
        created_event={
            "id": SAMPLE_EVENT_ID,
            "patient_id": patient["id"],
            "event_type": "ecg",
            "timestamp": "2024-01-15T10:30:00",
            "source_service": "rpm-bridge",
            "structured_data": {},
            "summary_text": "",
        },
    )
    app.dependency_overrides[get_clinic_ehr_client] = lambda: mock
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac, mock
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_no_patient():
    """Client where clinic-ehr returns 404 for any ABHA lookup."""
    mock = MockClinicEHRClient(patient=None)
    app.dependency_overrides[get_clinic_ehr_client] = lambda: mock
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac, mock
    app.dependency_overrides.clear()

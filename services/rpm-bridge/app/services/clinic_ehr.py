from typing import Any

import httpx

from app.config import settings


class ClinicEHRClient:
    """Thin async HTTP wrapper for clinic-ehr internal API calls."""

    def __init__(self, base_url: str):
        self._base_url = base_url

    async def get_patient_by_abha(self, abha_id: str) -> dict[str, Any] | None:
        async with httpx.AsyncClient(base_url=self._base_url) as client:
            resp = await client.get(f"/patients/by-abha/{abha_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()

    async def create_timeline_event(
        self, patient_id: str, event: dict[str, Any]
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=self._base_url) as client:
            resp = await client.post(f"/patients/{patient_id}/timeline", json=event)
            resp.raise_for_status()
            return resp.json()


def get_clinic_ehr_client() -> ClinicEHRClient:
    return ClinicEHRClient(settings.clinic_ehr_url)

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.ecg import ECGEventRequest, ECGEventResponse
from app.services.clinic_ehr import ClinicEHRClient, get_clinic_ehr_client

router = APIRouter(tags=["rpm"])


@router.post(
    "/ecg-event",
    response_model=ECGEventResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_ecg_event(
    body: ECGEventRequest,
    ehr: ClinicEHRClient = Depends(get_clinic_ehr_client),
) -> ECGEventResponse:
    patient = await ehr.get_patient_by_abha(body.patient_abha_id)
    if patient is None:
        raise HTTPException(
            status_code=404,
            detail=f"No patient found for ABHA ID {body.patient_abha_id}",
        )

    summary = f"ECG: {body.ecg_label} (confidence: {body.confidence:.0%})"
    if body.alert:
        summary = f"[ALERT] {summary}"

    event_payload = {
        "event_type": "ecg",
        "timestamp": body.timestamp.isoformat(),
        "source_service": "rpm-bridge",
        "structured_data": {
            "ecg_label": body.ecg_label,
            "confidence": body.confidence,
            "alert": body.alert,
            "features": body.features,
        },
        "summary_text": summary,
    }

    created = await ehr.create_timeline_event(patient["id"], event_payload)

    return ECGEventResponse(
        timeline_event_id=created["id"],
        patient_id=patient["id"],
        ecg_label=body.ecg_label,
        alert=body.alert,
        summary_text=summary,
    )

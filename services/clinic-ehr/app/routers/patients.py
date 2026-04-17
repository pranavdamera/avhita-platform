import uuid
from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models as db
from app.db.session import get_db
from app.models.patient import (
    PatientProfile,
    PatientRegisterRequest,
    TimelineEvent,
    TimelineEventCreate,
)
from app.services.abha import verify_with_nha

router = APIRouter(tags=["patients"])


@router.post(
    "/register",
    response_model=PatientProfile,
    status_code=status.HTTP_201_CREATED,
)
async def register_patient(
    body: PatientRegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> PatientProfile:
    if body.abha_id:
        existing = await session.scalar(
            select(db.Patient).where(db.Patient.abha_id == body.abha_id)
        )
        if existing:
            raise HTTPException(status_code=409, detail="ABHA ID already registered")

        if not await verify_with_nha(body.abha_id):
            raise HTTPException(status_code=422, detail="ABHA ID could not be verified with NHA")

    if body.primary_cardiologist_id:
        practitioner = await session.get(db.Practitioner, body.primary_cardiologist_id)
        if not practitioner:
            raise HTTPException(status_code=422, detail="Practitioner not found")

    patient = db.Patient(
        id=str(uuid.uuid4()),
        abha_id=body.abha_id,
        family_name=body.family_name,
        given_names=body.given_names,
        dob=body.dob,
        gender=body.gender.value,
        blood_group=body.blood_group.value if body.blood_group else None,
        emergency_contact=body.emergency_contact.model_dump() if body.emergency_contact else None,
        primary_cardiologist_id=body.primary_cardiologist_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session.add(patient)
    await session.commit()
    await session.refresh(patient)
    return PatientProfile.model_validate(patient)


# Defined before /{patient_id} so the literal "by-abha" segment takes precedence
@router.get("/by-abha/{abha_id}", response_model=PatientProfile)
async def get_patient_by_abha(
    abha_id: str,
    session: AsyncSession = Depends(get_db),
) -> PatientProfile:
    patient = await session.scalar(
        select(db.Patient).where(db.Patient.abha_id == abha_id)
    )
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientProfile.model_validate(patient)


@router.get("/{patient_id}", response_model=PatientProfile)
async def get_patient(
    patient_id: str,
    session: AsyncSession = Depends(get_db),
) -> PatientProfile:
    patient = await session.get(db.Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientProfile.model_validate(patient)


@router.get("/{patient_id}/timeline", response_model=list[TimelineEvent])
async def get_patient_timeline(
    patient_id: str,
    session: AsyncSession = Depends(get_db),
) -> list[TimelineEvent]:
    patient = await session.get(db.Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    result = await session.execute(
        select(db.TimelineEvent)
        .where(db.TimelineEvent.patient_id == patient_id)
        .order_by(db.TimelineEvent.timestamp)
    )
    return [TimelineEvent.model_validate(e) for e in result.scalars().all()]


@router.post(
    "/{patient_id}/timeline",
    response_model=TimelineEvent,
    status_code=status.HTTP_201_CREATED,
)
async def create_timeline_event(
    patient_id: str,
    body: TimelineEventCreate,
    session: AsyncSession = Depends(get_db),
) -> TimelineEvent:
    patient = await session.get(db.Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    event = db.TimelineEvent(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        event_type=body.event_type.value,
        timestamp=body.timestamp,
        source_service=body.source_service,
        structured_data=body.structured_data,
        summary_text=body.summary_text,
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return TimelineEvent.model_validate(event)

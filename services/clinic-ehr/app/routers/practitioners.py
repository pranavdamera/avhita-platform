import uuid
from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models as db
from app.db.session import get_db
from app.models.practitioner import PractitionerProfile, PractitionerRegisterRequest

router = APIRouter(tags=["practitioners"])


@router.post(
    "/register",
    response_model=PractitionerProfile,
    status_code=status.HTTP_201_CREATED,
)
async def register_practitioner(
    body: PractitionerRegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> PractitionerProfile:
    if body.registration_number:
        existing = await session.scalar(
            select(db.Practitioner).where(
                db.Practitioner.registration_number == body.registration_number
            )
        )
        if existing:
            raise HTTPException(
                status_code=409, detail="Registration number already exists"
            )

    practitioner = db.Practitioner(
        id=str(uuid.uuid4()),
        registration_number=body.registration_number,
        family_name=body.family_name,
        given_names=body.given_names,
        specialty=body.specialty,
        qualification=body.qualification,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session.add(practitioner)
    await session.commit()
    await session.refresh(practitioner)
    return PractitionerProfile.model_validate(practitioner)


@router.get("/{practitioner_id}", response_model=PractitionerProfile)
async def get_practitioner(
    practitioner_id: str,
    session: AsyncSession = Depends(get_db),
) -> PractitionerProfile:
    practitioner = await session.get(db.Practitioner, practitioner_id)
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return PractitionerProfile.model_validate(practitioner)

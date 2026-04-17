from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PractitionerRegisterRequest(BaseModel):
    registration_number: Optional[str] = None  # MCI / NMC registration number
    family_name: str
    given_names: list[str]
    specialty: Optional[str] = None   # e.g. "Cardiology", "General Medicine"
    qualification: Optional[list[str]] = None  # e.g. ["MBBS", "MD", "DM Cardiology"]


class PractitionerProfile(BaseModel):
    id: str
    registration_number: Optional[str]
    family_name: str
    given_names: list[str]
    specialty: Optional[str]
    qualification: Optional[list[str]]
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

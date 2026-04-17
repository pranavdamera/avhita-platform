from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, field_validator

from app.services.abha import validate_abha_format


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    unknown = "unknown"


class BloodGroupEnum(str, Enum):
    A_pos = "A+"
    A_neg = "A-"
    B_pos = "B+"
    B_neg = "B-"
    AB_pos = "AB+"
    AB_neg = "AB-"
    O_pos = "O+"
    O_neg = "O-"


class EventTypeEnum(str, Enum):
    consultation = "consultation"
    lab = "lab"
    ecg = "ecg"
    document = "document"
    alert = "alert"


class EmergencyContact(BaseModel):
    name: str
    relationship: str
    phone: str


# ── Request / Response schemas ────────────────────────────────────────────────

class PatientRegisterRequest(BaseModel):
    abha_id: Optional[str] = None
    family_name: str
    given_names: list[str]
    dob: date
    gender: GenderEnum
    blood_group: Optional[BloodGroupEnum] = None
    emergency_contact: Optional[EmergencyContact] = None
    primary_cardiologist_id: Optional[str] = None

    @field_validator("abha_id")
    @classmethod
    def check_abha_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not validate_abha_format(v):
            raise ValueError("ABHA ID must match XX-XXXX-XXXX-XXXX (digits only)")
        return v


class PatientProfile(BaseModel):
    id: str
    abha_id: Optional[str]
    family_name: str
    given_names: list[str]
    dob: date
    gender: GenderEnum
    blood_group: Optional[BloodGroupEnum]
    emergency_contact: Optional[EmergencyContact]
    primary_cardiologist_id: Optional[str]
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TimelineEventCreate(BaseModel):
    event_type: EventTypeEnum
    timestamp: datetime
    source_service: str
    structured_data: Optional[dict[str, Any]] = None
    summary_text: Optional[str] = None


class TimelineEvent(BaseModel):
    id: str
    patient_id: str
    event_type: EventTypeEnum
    timestamp: datetime
    source_service: str
    structured_data: Optional[dict[str, Any]] = None
    summary_text: Optional[str] = None

    model_config = {"from_attributes": True}

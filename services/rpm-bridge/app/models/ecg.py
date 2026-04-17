from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.services.abha import validate_abha_format
from pydantic import field_validator


class ECGEventRequest(BaseModel):
    patient_abha_id: str
    ecg_label: str          # e.g. "Normal", "AFib", "LBBB", "PVC"
    confidence: float = Field(ge=0.0, le=1.0)
    alert: bool
    features: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime

    @field_validator("patient_abha_id")
    @classmethod
    def check_abha_format(cls, v: str) -> str:
        if not validate_abha_format(v):
            raise ValueError("patient_abha_id must match XX-XXXX-XXXX-XXXX (digits only)")
        return v


class ECGEventResponse(BaseModel):
    timeline_event_id: str
    patient_id: str
    ecg_label: str
    alert: bool
    summary_text: str

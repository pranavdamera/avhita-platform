"""
SQLAlchemy ORM models mirroring FHIR R4 Patient and Observation resources.

Patient   → FHIR Patient (https://hl7.org/fhir/R4/patient.html)
TimelineEvent → FHIR Observation / AuditEvent (category-keyed composite)
"""
import uuid
from datetime import datetime, UTC

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Patient(Base):
    """FHIR R4 Patient resource.

    Notable FHIR mappings:
      id                       → Patient.id
      abha_id                  → Patient.identifier[system=abdm:abha]
      family_name              → Patient.name[use=official].family
      given_names (JSON list)  → Patient.name[use=official].given
      dob                      → Patient.birthDate
      gender                   → Patient.gender
      blood_group              → Patient.extension[blood-group]  (NCP extension)
      emergency_contact (JSON) → Patient.contact
      primary_cardiologist_id  → Patient.generalPractitioner[0]
    """

    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    abha_id = Column(String(17), unique=True, nullable=True, index=True)
    family_name = Column(String(255), nullable=False)
    given_names = Column(JSON, nullable=False)  # list[str]
    dob = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)  # male|female|other|unknown
    blood_group = Column(String(5), nullable=True)
    emergency_contact = Column(JSON, nullable=True)  # EmergencyContact dict
    primary_cardiologist_id = Column(String(36), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    timeline_events = relationship(
        "TimelineEvent",
        back_populates="patient",
        order_by="TimelineEvent.timestamp",
    )


class TimelineEvent(Base):
    """Composite FHIR resource representing a patient timeline entry.

    Maps to FHIR Observation (lab/ecg/alert/rpm) or DocumentReference
    (document/consultation), categorised by event_type.

      patient_id      → Observation.subject
      event_type      → Observation.category.code
      timestamp       → Observation.effectiveDateTime
      source_service  → Observation.performer (service name)
      structured_data → Observation.component (arbitrary key/value JSON)
      summary_text    → Observation.note[0].text
    """

    __tablename__ = "timeline_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(
        String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type = Column(String(20), nullable=False)  # EventTypeEnum values
    timestamp = Column(DateTime, nullable=False)
    source_service = Column(String(100), nullable=False)
    structured_data = Column(JSON, nullable=True)
    summary_text = Column(String(1000), nullable=True)

    patient = relationship("Patient", back_populates="timeline_events")

# clinic-ehr

Core EHR service. Owns the canonical patient record, encounters, prescriptions, and lab results.
Exposes a FHIR R4 API surface alongside internal REST endpoints.

## Responsibilities

- Patient CRUD and search
- Encounter / visit lifecycle (open → in-progress → closed)
- Prescription and medication administration records
- Lab result ingestion and storage
- FHIR R4 read/write endpoints (`/fhir/r4/...`)

## Key design decisions

- Patient identity is resolved via `shared/patient-identity` before any write — never bypass this.
- FHIR resources are the source of truth for external consumers; internal models map 1:1.
- All DB access via SQLAlchemy async sessions; no raw SQL outside migrations.

## Env vars required

```
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=
ABDM_GATEWAY_URL=http://abdm-gateway:8000
```

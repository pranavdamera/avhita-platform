# avhita-platform

EHR platform for Indian clinics, connecting RPM devices and AI intelligence via ABDM/FHIR.

## Services

| Service | Purpose |
|---|---|
| `services/clinic-ehr` | Core EHR: patients, visits, prescriptions, FHIR R4 APIs |
| `services/rpm-bridge` | Bridges avhita-ai RPM data into EHR (device readings, alerts) |
| `services/intelligence` | Clinical AI: SOAP notes, risk scoring, differential dx |
| `services/abdm-gateway` | ABDM / ABHA ID integration, health record linking |

## Shared modules

- `shared/fhir-models` — Pydantic FHIR R4 models (Patient, Observation, Encounter, etc.)
- `shared/patient-identity` — ABHA ID resolution and deduplication

## Key conventions

- All inter-service communication uses FHIR R4 resources where applicable.
- Patient identity is always resolved via `shared/patient-identity` before writes.
- ABDM interactions must go through `services/abdm-gateway` — never call ABDM APIs directly.
- Secrets are never committed; use `.env` files and a secrets manager in prod.

## Running locally

```bash
docker-compose up
```

## Stack

- Python 3.12 / FastAPI per service
- PostgreSQL (one schema per service, shared DB in dev)
- Redis for queuing RPM telemetry
- FHIR R4 for data interchange

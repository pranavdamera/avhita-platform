# rpm-bridge

Receives telemetry from avhita-ai (RPM devices: BP, SpO2, glucose, ECG) and writes
FHIR Observation resources to clinic-ehr. Also generates alert events when readings
breach patient-specific thresholds.

## Responsibilities

- Ingest RPM readings from avhita-ai via webhook or Redis queue
- Validate and normalise device payloads into FHIR Observation format
- POST Observations to clinic-ehr's FHIR endpoint
- Evaluate threshold rules and emit alert events

## Key design decisions

- Stateless where possible — state lives in clinic-ehr.
- Uses Redis for async ingestion queue (avhita-ai pushes, bridge consumes).
- Threshold rules are fetched from clinic-ehr per patient; cached with short TTL.

## Env vars required

```
CLINIC_EHR_URL=http://clinic-ehr:8000
REDIS_URL=redis://redis:6379/0
```

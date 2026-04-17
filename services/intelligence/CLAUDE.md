# intelligence

Clinical AI service. Generates SOAP notes, risk scores, and differential diagnoses
from encounter context and patient history. Powered by Claude (Anthropic SDK).

## Responsibilities

- SOAP note generation from structured encounter data
- Patient risk stratification (cardiovascular, diabetic, etc.)
- Differential diagnosis suggestions from symptoms + vitals
- Clinical summary for discharge / referral letters

## Key design decisions

- Calls clinic-ehr to fetch patient context before each inference request.
- Uses prompt caching (Anthropic beta) for system prompts and guidelines.
- All AI outputs are advisory — must be reviewed by a clinician before actioning.
- No PHI is logged; strip identifiers before sending to any external model API.

## Env vars required

```
ANTHROPIC_API_KEY=
CLINIC_EHR_URL=http://clinic-ehr:8000
```

# abdm-gateway

Single point of integration with India's ABDM (Ayushman Bharat Digital Mission).
Handles ABHA ID creation, consent management, and health record sharing as HIP/HIU.

## Responsibilities

- ABHA ID creation and mobile/Aadhaar verification
- Consent artifact lifecycle (request → grant → revoke)
- HIP: push health records to the ABDM network on consent grant
- HIU: pull health records from other providers under patient consent
- Callback endpoints for ABDM gateway callbacks (async flows)

## Key design decisions

- No other service calls ABDM APIs directly — all traffic routes through this gateway.
- Consent artefacts are stored locally and cross-referenced with clinic-ehr patient IDs.
- Encryption of health records follows ABDM spec (X25519 key exchange).

## Env vars required

```
ABDM_BASE_URL=https://dev.abdm.gov.in
ABDM_CLIENT_ID=
ABDM_CLIENT_SECRET=
HIP_ID=
CLINIC_EHR_URL=http://clinic-ehr:8000
```

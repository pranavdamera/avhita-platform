import re

_ABHA_RE = re.compile(r"^\d{2}-\d{4}-\d{4}-\d{4}$")


def validate_abha_format(abha_id: str) -> bool:
    return bool(_ABHA_RE.match(abha_id))


async def verify_with_nha(abha_id: str) -> bool:
    # Stub: returns True until ABDM sandbox credentials are provisioned.
    # Replace with POST /v1/registration/aadhaar/verifyOTP (NHA Health ID API v2).
    return True

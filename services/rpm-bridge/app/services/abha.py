import re

_ABHA_RE = re.compile(r"^\d{2}-\d{4}-\d{4}-\d{4}$")


def validate_abha_format(abha_id: str) -> bool:
    return bool(_ABHA_RE.match(abha_id))

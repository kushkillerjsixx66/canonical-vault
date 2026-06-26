from typing import Any


def record_violation(violation: dict[str, Any]) -> dict[str, Any]:
    """
    Primitive for recording a violation.

    In a real system, this would persist to Vault or filesystem.
    Here we just return a normalized record.
    """
    return {
        "status": "recorded",
        "violation": violation,
    }

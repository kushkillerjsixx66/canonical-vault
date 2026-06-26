from typing import Any


def summarize_violations(violations: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Summarize violations into a simple structure.
    """
    by_type: dict[str, int] = {}
    for v in violations:
        t = v.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    return {
        "total": len(violations),
        "by_type": by_type,
        "violations": violations,
    }

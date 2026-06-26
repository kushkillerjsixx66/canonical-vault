from typing import Any


class LineageTracker:
    """
    Canonical lineage tracker for Vara.

    This is the epistemic spine that Stumpy expects:
    each entry carries seq, operator_id, role, altitude.
    """

    def __init__(self) -> None:
        self._seq = 0

    def extend(self, identity: dict[str, Any], runtime_state: dict[str, Any]) -> list[dict[str, Any]]:
        self._seq += 1
        entry = {
            "seq": self._seq,
            "operator_id": identity.get("operator_id"),
            "role": identity.get("role"),
            "altitude": runtime_state.get("altitude"),
        }
        return [entry]

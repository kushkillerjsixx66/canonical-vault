import time
from typing import Any


class DriftDetectorProcess:
    """Watches events for altitude and epistemic drift."""

    VALID_ALTITUDES = ("governance", "epistemic", "runtime", "operator")

    def __init__(self, event_queue, violation_queue) -> None:
        self._event_queue = event_queue
        self._violation_queue = violation_queue
        self._running = True

    def run(self) -> None:
        while self._running:
            try:
                event = self._event_queue.get(timeout=1.0)
            except Exception:
                time.sleep(0.1)
                continue
            self._inspect_event(event)

    def inspect_event(self, event: dict[str, Any]) -> list[dict]:
        """Return drift findings synchronously; inspection publishes them."""
        return self._inspect_event(event)

    def _inspect_event(self, event: dict[str, Any]) -> list[dict]:
        payload = event.get("payload", {})
        altitude = payload.get("altitude")
        findings: list[dict] = []

        if altitude and altitude not in self.VALID_ALTITUDES:
            findings.append({
                "type": "altitude_drift",
                "source": event.get("source"),
                "payload": payload,
            })

        if event.get("type") == "epistemic_state" and not payload.get("lineage"):
            findings.append({
                "type": "epistemic_drift",
                "source": event.get("source"),
                "payload": payload,
            })

        for finding in findings:
            self._violation_queue.put(finding)

        return findings

    def stop(self) -> None:
        self._running = False

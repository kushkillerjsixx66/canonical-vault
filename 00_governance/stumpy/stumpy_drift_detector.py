import time
from typing import Any


class DriftDetectorProcess:
    """
    Watches events for altitude and epistemic drift.

    Detection is synchronous at the evaluator boundary. Queue publication is
    retained for compatibility, but callers that need deterministic governance
    results consume the returned findings directly.
    """

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
        """Return all drift findings synchronously and publish them."""
        findings = self._inspect_event(event)
        for finding in findings:
            self._violation_queue.put(finding)
        return findings

    def _inspect_event(self, event: dict[str, Any]) -> list[dict]:
        payload = event.get("payload", {})
        altitude = payload.get("altitude")
        findings: list[dict] = []

        if altitude and altitude not in ("governance", "epistemic", "runtime", "operator"):
            findings.append({
                "type": "altitude_drift",
                "source": event.get("source"),
                "payload": payload,
            })

        if event.get("type") == "epistemic_state":
            lineage = payload.get("lineage")
            if not lineage:
                findings.append({
                    "type": "epistemic_drift",
                    "source": event.get("source"),
                    "payload": payload,
                })

        return findings

    def stop(self) -> None:
        self._running = False

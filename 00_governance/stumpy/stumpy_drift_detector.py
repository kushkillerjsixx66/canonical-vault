import time
from typing import Any


class DriftDetectorProcess:
    """
    Watches events for altitude and epistemic drift.
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
                # Background drift checks could be added here.
                time.sleep(0.1)
                continue

            self._inspect_event(event)

    def _inspect_event(self, event: dict[str, Any]) -> None:
        payload = event.get("payload", {})
        altitude = payload.get("altitude")

        if altitude and altitude not in ("governance", "epistemic", "runtime", "operator"):
            self._violation_queue.put({
                "type": "altitude_drift",
                "source": event.get("source"),
                "payload": payload,
            })

        # Simple epistemic drift example
        if event.get("type") == "epistemic_state":
            lineage = payload.get("lineage")
            if not lineage:
                self._violation_queue.put({
                    "type": "epistemic_drift",
                    "source": event.get("source"),
                    "payload": payload,
                })

    def stop(self) -> None:
        self._running = False

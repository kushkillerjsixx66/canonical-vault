import time
from typing import Any


class DriftDetectorProcess:
    """
    Runs in its own process.

    Watches events for:
    - epistemic drift
    - runtime altitude drift
    - governance violations
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
                # Periodic background checks could go here.
                continue

            self._inspect_event(event)

    def _inspect_event(self, event: dict[str, Any]) -> None:
        source = event.get("source")
        payload = event.get("payload", {})

        # Example: simple altitude drift check
        altitude = payload.get("altitude")
        if altitude and altitude not in ("governance", "epistemic", "runtime", "operator"):
            self._violation_queue.put({
                "type": "altitude_drift",
                "source": source,
                "payload": payload,
            })

    def stop(self) -> None:
        self._running = False

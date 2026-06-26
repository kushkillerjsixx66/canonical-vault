from typing import Any


class EnforcementProcess:
    """
    Runs in its own process.

    Applies enforcement pipelines to violations and high‑risk events.
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
                continue

            self._route_event(event)

    def _route_event(self, event: dict[str, Any]) -> None:
        etype = event.get("type")

        if etype == "runtime_state":
            self._handle_runtime_state(event)
        elif etype == "epistemic_state":
            self._handle_epistemic_state(event)
        else:
            # Unknown event types can be escalated.
            self._violation_queue.put({
                "type": "unknown_event_type",
                "event": event,
            })

    def _handle_runtime_state(self, event: dict[str, Any]) -> None:
        # Placeholder: enforce runtime invariants via Veil supervision.
        payload = event.get("payload", {})
        if payload.get("unsafe"):
            self._violation_queue.put({
                "type": "runtime_violation",
                "event": event,
            })

    def _handle_epistemic_state(self, event: dict[str, Any]) -> None:
        # Placeholder: enforce epistemic invariants via Vara bridge.
        payload = event.get("payload", {})
        if payload.get("corrupted"):
            self._violation_queue.put({
                "type": "epistemic_violation",
                "event": event,
            })

    def stop(self) -> None:
        self._running = False

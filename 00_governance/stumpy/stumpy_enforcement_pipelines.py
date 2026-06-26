from typing import Any


class EnforcementProcess:
    """
    Applies enforcement pipelines to high‑risk events.
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
        payload = event.get("payload", {})

        if etype == "runtime_state":
            self._enforce_runtime(payload)
        elif etype == "epistemic_state":
            self._enforce_epistemic(payload)
        elif etype == "operator_state":
            self._enforce_operator(payload)
        elif etype == "vault_state":
            self._enforce_vault(payload)
        else:
            # Unknown event types escalated.
            self._violation_queue.put({
                "type": "unknown_event_type",
                "event": event,
            })

    def _enforce_runtime(self, payload: dict[str, Any]) -> None:
        if payload.get("unsafe"):
            self._violation_queue.put({
                "type": "runtime_enforcement_triggered",
                "payload": payload,
            })

    def _enforce_epistemic(self, payload: dict[str, Any]) -> None:
        if payload.get("corrupted"):
            self._violation_queue.put({
                "type": "epistemic_enforcement_triggered",
                "payload": payload,
            })

    def _enforce_operator(self, payload: dict[str, Any]) -> None:
        if payload.get("posture") == "hostile":
            self._violation_queue.put({
                "type": "operator_enforcement_triggered",
                "payload": payload,
            })

    def _enforce_vault(self, payload: dict[str, Any]) -> None:
        if payload.get("integrity") is False:
            self._violation_queue.put({
                "type": "vault_enforcement_triggered",
                "payload": payload,
            })

    def stop(self) -> None:
        self._running = False

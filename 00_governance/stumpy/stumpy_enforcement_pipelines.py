from typing import Any


class EnforcementProcess:
    """
    Applies enforcement pipelines to high-risk events.

    Routing returns findings synchronously while preserving queue publication
    for compatibility with existing consumers.
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

            self.route_event(event)

    def route_event(self, event: dict[str, Any]) -> list[dict]:
        """Return enforcement findings synchronously and publish them."""
        findings = self._route_event(event)
        for finding in findings:
            self._violation_queue.put(finding)
        return findings

    def _route_event(self, event: dict[str, Any]) -> list[dict]:
        etype = event.get("type")
        payload = event.get("payload", {})
        findings: list[dict] = []

        if etype == "runtime_state":
            findings.extend(self._enforce_runtime(payload))
        elif etype == "epistemic_state":
            findings.extend(self._enforce_epistemic(payload))
        elif etype == "operator_state":
            findings.extend(self._enforce_operator(payload))
        elif etype == "vault_state":
            findings.extend(self._enforce_vault(payload))
        else:
            findings.append({
                "type": "unknown_event_type",
                "event": event,
            })

        return findings

    def _enforce_runtime(self, payload: dict[str, Any]) -> list[dict]:
        if payload.get("unsafe"):
            return [{
                "type": "runtime_enforcement_triggered",
                "payload": payload,
            }]
        return []

    def _enforce_epistemic(self, payload: dict[str, Any]) -> list[dict]:
        if payload.get("corrupted"):
            return [{
                "type": "epistemic_enforcement_triggered",
                "payload": payload,
            }]
        return []

    def _enforce_operator(self, payload: dict[str, Any]) -> list[dict]:
        if payload.get("posture") == "hostile":
            return [{
                "type": "operator_enforcement_triggered",
                "payload": payload,
            }]
        return []

    def _enforce_vault(self, payload: dict[str, Any]) -> list[dict]:
        if payload.get("integrity") is False:
            return [{
                "type": "vault_enforcement_triggered",
                "payload": payload,
            }]
        return []

    def stop(self) -> None:
        self._running = False

from typing import Any


class RuntimeBus:
    """
    Canonical bus from Veil into Stumpy.

    Emits:
    - type: runtime_state
    - source: veil
    - payload: { identity, altitude, posture, ... }
    """

    def __init__(self, stumpy_event_queue) -> None:
        self._queue = stumpy_event_queue

    def emit_runtime_state(self, identity: dict[str, Any], runtime_state: dict[str, Any]) -> None:
        payload: dict[str, Any] = {
            "identity": identity,
            **runtime_state,
        }
        self._queue.put({
            "type": "runtime_state",
            "source": "veil",
            "payload": payload,
        })

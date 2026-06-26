"""
Supervision hooks for Veil.

Veil reports runtime_state events into Stumpy's event queue.
"""


def emit_runtime_event(queue, payload: dict) -> None:
    queue.put({
        "type": "runtime_state",
        "source": "veil",
        "payload": payload,
    })

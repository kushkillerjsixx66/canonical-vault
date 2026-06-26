"""
Supervision hooks for Veil.
"""


def emit_runtime_event(queue, payload: dict) -> None:
    queue.put({
        "type": "runtime_state",
        "source": "veil",
        "payload": payload,
    })

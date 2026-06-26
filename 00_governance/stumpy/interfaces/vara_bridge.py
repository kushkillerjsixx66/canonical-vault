"""
Bridge between Stumpy and Vara.

Stumpy does not call Vara directly; it sends events that Vara
subscribes to, or receives Vara‑originated epistemic_state events.
"""


def emit_epistemic_event(queue, payload: dict) -> None:
    queue.put({
        "type": "epistemic_state",
        "source": "vara",
        "payload": payload,
    })

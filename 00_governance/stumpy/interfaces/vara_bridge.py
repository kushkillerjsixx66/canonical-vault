"""
Bridge between Stumpy and Vara.
"""


def emit_epistemic_event(queue, payload: dict) -> None:
    queue.put({
        "type": "epistemic_state",
        "source": "vara",
        "payload": payload,
    })

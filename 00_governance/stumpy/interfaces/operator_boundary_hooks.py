"""
Operator boundary hooks.
"""


def emit_operator_event(queue, payload: dict) -> None:
    queue.put({
        "type": "operator_state",
        "source": "operator",
        "payload": payload,
    })

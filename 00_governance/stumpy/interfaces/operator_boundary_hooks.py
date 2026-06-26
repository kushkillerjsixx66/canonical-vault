"""
Operator boundary hooks.

Used when operator posture or altitude needs to be enforced.
"""


def emit_operator_event(queue, payload: dict) -> None:
    queue.put({
        "type": "operator_state",
        "source": "operator",
        "payload": payload,
    })

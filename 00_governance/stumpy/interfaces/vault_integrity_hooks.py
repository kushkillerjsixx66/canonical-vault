"""
Hooks for Vault integrity checks.
"""


def emit_vault_event(queue, payload: dict) -> None:
    queue.put({
        "type": "vault_state",
        "source": "vault",
        "payload": payload,
    })

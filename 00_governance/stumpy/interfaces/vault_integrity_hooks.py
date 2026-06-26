"""
Hooks for Vault integrity checks.

Vault can emit lineage or integrity events into Stumpy.
"""


def emit_vault_event(queue, payload: dict) -> None:
    queue.put({
        "type": "vault_state",
        "source": "vault",
        "payload": payload,
    })

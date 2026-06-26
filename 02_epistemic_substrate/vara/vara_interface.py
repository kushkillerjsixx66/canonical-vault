from typing import Any

from .vara_core import Vara


class VaraInterface:
    """
    Canonical interface for Veil and other modules to talk to Vara.
    """

    def __init__(self, stumpy_event_queue) -> None:
        self._vara = Vara(stumpy_event_queue)

    def handle_veil_state(self, identity: dict[str, Any], runtime_state: dict[str, Any]) -> None:
        """
        Veil calls this with:
        - identity: operator identity (with sovereignty)
        - runtime_state: Veil's current runtime state (with altitude)
        """
        self._vara.supervise_veil(identity, runtime_state)

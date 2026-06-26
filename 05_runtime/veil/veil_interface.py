from typing import Any
from .veil_core import Veil


class VeilInterface:
    """
    Canonical interface for the runtime system to talk to Veil.
    """

    def __init__(self, stumpy_event_queue, vara_interface) -> None:
        self._veil = Veil(stumpy_event_queue, vara_interface)

    def submit_runtime_update(self, identity: dict[str, Any], raw_state: dict[str, Any]) -> None:
        """
        Called by the runtime system.

        identity:
            - operator_id
            - role
            - sovereignty

        raw_state:
            - altitude
            - posture (optional)
            - any other runtime metadata
        """
        self._veil.update_state(identity, raw_state)

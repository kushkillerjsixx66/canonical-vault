from typing import Any
from .veil_posture import PostureInterpreter
from .veil_runtime_bus import RuntimeBus


class Veil:
    """
    Canonical Veil.

    Responsibilities:
    - Interpret operator posture.
    - Maintain runtime altitude.
    - Emit runtime_state events to Stumpy.
    - Forward runtime state to Vara.
    """

    def __init__(self, stumpy_event_queue, vara_interface) -> None:
        self._bus = RuntimeBus(stumpy_event_queue)
        self._posture = PostureInterpreter()
        self._vara = vara_interface

    def update_state(self, identity: dict[str, Any], raw_state: dict[str, Any]) -> None:
        """
        Main entrypoint: runtime updates come here.

        raw_state must include:
        - altitude
        - posture (optional)
        """
        posture = self._posture.interpret(raw_state)
        runtime_state = {
            **raw_state,
            "posture": posture,
        }

        # Emit runtime_state to Stumpy
        self._bus.emit_runtime_state(identity, runtime_state)

        # Forward to Vara for epistemic supervision
        self._vara.handle_veil_state(identity, runtime_state)

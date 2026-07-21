from dataclasses import dataclass
from typing import Any

from .vara_lineage import LineageTracker


@dataclass
class EpistemicContext:
    identity: dict[str, Any]
    runtime_state: dict[str, Any]
    lineage: list[dict[str, Any]]


# Imported after EpistemicContext is defined: vara_epistemic_bus imports
# EpistemicContext back from this module, so importing it any earlier
# creates a circular import (ImportError: cannot import name
# 'EpistemicContext' from partially initialized module 'vara.vara_core').
from .vara_epistemic_bus import EpistemicBus


class Vara:
    """
    Canonical Epistemic Supervisor.

    Responsibilities:
    - Supervise Veil (runtime altitude, posture).
    - Construct epistemic context.
    - Emit epistemic_state events to Stumpy.
    """

    def __init__(self, stumpy_event_queue) -> None:
        self._lineage = LineageTracker()
        self._bus = EpistemicBus(stumpy_event_queue)

    def supervise_veil(self, identity: dict[str, Any], runtime_state: dict[str, Any]) -> None:
        """
        Main entrypoint: Veil calls this whenever runtime state changes.
        """
        lineage = self._lineage.extend(identity, runtime_state)
        ctx = EpistemicContext(
            identity=identity,
            runtime_state=runtime_state,
            lineage=lineage,
        )
        self._bus.emit_epistemic_context(ctx)

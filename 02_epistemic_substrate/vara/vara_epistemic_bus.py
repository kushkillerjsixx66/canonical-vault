from typing import Any
from .vara_core import EpistemicContext


class EpistemicBus:
    """
    Canonical bus from Vara into Stumpy.

    Emits:
    - type: epistemic_state
    - source: vara
    - payload: { identity, runtime, lineage }
    """

    def __init__(self, stumpy_event_queue) -> None:
        self._queue = stumpy_event_queue

    def emit_epistemic_context(self, ctx: EpistemicContext) -> None:
        payload: dict[str, Any] = {
            "identity": ctx.identity,
            "runtime": ctx.runtime_state,
            "lineage": ctx.lineage,
        }
        self._queue.put({
            "type": "epistemic_state",
            "source": "vara",
            "payload": payload,
        })

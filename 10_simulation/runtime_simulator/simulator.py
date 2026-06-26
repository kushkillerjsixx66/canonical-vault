import time
from typing import Any, List

from boot.lattice_boot.boot_sequence import LatticeBoot


class RuntimeSimulator:
    """
    Canonical Runtime Simulator.

    Drives:
    - Veil (runtime boundary)
    - Vara (epistemic supervisor)
    - Stumpy (governance engine)

    By emitting:
    - altitude shifts
    - posture changes
    - identity variations
    """

    def __init__(self, delay: float = 0.2):
        self.delay = delay
        self.boot = LatticeBoot()
        self.components = None

    def start(self):
        self.components = self.boot.start()

    def stop(self):
        self.boot.stop()

    # ------------------------------------------------------------------
    # SCENARIOS
    # ------------------------------------------------------------------

    def scenario_basic_runtime(self):
        """
        Simple runtime altitude + neutral posture.
        """
        veil = self.components["veil"]

        identity = {"operator_id": "op1", "role": "root", "sovereignty": "root"}
        state = {"altitude": "runtime", "posture": "neutral"}

        veil.submit_runtime_update(identity, state)
        time.sleep(self.delay)

    def scenario_altitude_drift(self):
        """
        Simulate altitude drift to trigger governance.
        """
        veil = self.components["veil"]

        identity = {"operator_id": "op1", "role": "root", "sovereignty": "root"}
        states: List[dict[str, Any]] = [
            {"altitude": "runtime", "posture": "focused"},
            {"altitude": "epistemic", "posture": "elevated"},
            {"altitude": "nonsense", "posture": "hostile"},
        ]

        for s in states:
            veil.submit_runtime_update(identity, s)
            time.sleep(self.delay)

    def scenario_operator_shift(self):
        """
        Simulate different operators and roles.
        """
        veil = self.components["veil"]

        identities = [
            {"operator_id": "op1", "role": "root", "sovereignty": "root"},
            {"operator_id": "op2", "role": "editor", "sovereignty": "tenant"},
        ]

        state = {"altitude": "runtime", "posture": "focused"}

        for ident in identities:
            veil.submit_runtime_update(ident, state)
            time.sleep(self.delay)

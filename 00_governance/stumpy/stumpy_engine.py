import multiprocessing as mp
from typing import Optional

from .stumpy_governance_bus import GovernanceBus
from .stumpy_drift_detector import DriftDetectorProcess
from .stumpy_enforcement_pipelines import EnforcementProcess
from .stumpy_identity_guard import IdentityGuard
from .invariants.constitutional_invariants import ConstitutionalInvariants


class StumpyEngine:
    """
    Operator‑grade governance engine.

    Runs as a supervisor over:
    - governance bus
    - drift detector
    - enforcement pipelines
    - identity guard
    """

    def __init__(self) -> None:
        self.event_queue: mp.Queue = mp.Queue()
        self.violation_queue: mp.Queue = mp.Queue()

        self.bus = GovernanceBus(self.event_queue, self.violation_queue)
        self.drift_proc = DriftDetectorProcess(self.event_queue, self.violation_queue)
        self.enforcement_proc = EnforcementProcess(self.event_queue, self.violation_queue)
        self.identity_guard = IdentityGuard()
        self.constitution = ConstitutionalInvariants()

        self._processes: list[mp.Process] = []

    def start(self) -> None:
        """Start multi‑process governance engine."""
        self._processes = [
            mp.Process(target=self.drift_proc.run, name="StumpyDriftDetector"),
            mp.Process(target=self.enforcement_proc.run, name="StumpyEnforcement"),
        ]

        for p in self._processes:
            p.daemon = True
            p.start()

        self.bus.start()

    def stop(self) -> None:
        """Gracefully stop all governance processes."""
        for p in self._processes:
            if p.is_alive():
                p.terminate()
        self.bus.stop()

    def submit_event(self, event: dict) -> None:
        """
        Entrypoint for the rest of the system.

        Example event:
        {
            "type": "runtime_state",
            "source": "veil",
            "payload": {...}
        }
        """
        self.event_queue.put(event)

    def get_violations(self) -> list[dict]:
        """Drain violation queue."""
        violations = []
        while not self.violation_queue.empty():
            violations.append(self.violation_queue.get())
        return violations

    def verify_identity(self, identity: dict) -> bool:
        """Delegate to identity guard."""
        return self.identity_guard.verify(identity)

    def assert_constitutional(self) -> None:
        """Run constitutional invariant checks at startup."""
        self.constitution.assert_all()

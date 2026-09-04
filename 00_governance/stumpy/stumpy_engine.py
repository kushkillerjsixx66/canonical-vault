import multiprocessing as mp
from threading import Lock

from .stumpy_governance_bus import GovernanceBus
from .stumpy_drift_detector import DriftDetectorProcess
from .stumpy_enforcement_pipelines import EnforcementProcess
from .stumpy_identity_guard import IdentityGuard
from .invariants.constitutional_invariants import ConstitutionalInvariants


class StumpyEngine:
    """
    Operator-grade governance engine.

    GovernanceBus is the sole consumer of the public event queue. It fans
    events into deterministic governance evaluators and the engine retains
    observed violations for reporting.
    """

    def __init__(self) -> None:
        self.event_queue: mp.Queue = mp.Queue()
        self.violation_queue: mp.Queue = mp.Queue()

        self.bus = GovernanceBus(self.event_queue, self.violation_queue)
        self.drift_proc = DriftDetectorProcess(None, self.violation_queue)
        self.enforcement_proc = EnforcementProcess(None, self.violation_queue)
        self.identity_guard = IdentityGuard()
        self.constitution = ConstitutionalInvariants()

        self._violation_history: list[dict] = []
        self._history_lock = Lock()
        self._running = False

        self._register_handlers()

    def _register_handlers(self) -> None:
        for event_type in ("runtime_state", "epistemic_state", "operator_state", "vault_state"):
            self.bus.register_handler(event_type, self._handle_governance_event)

    def _handle_governance_event(self, event: dict) -> None:
        """Evaluate an event and retain findings synchronously.

        The public event queue is asynchronous, but governance evaluation is
        deterministic. Findings therefore must be returned directly by the
        evaluators rather than immediately re-reading a multiprocessing.Queue,
        whose feeder thread can make get_nowait() observe a false empty state.
        """
        violations = []
        violations.extend(self.drift_proc.inspect_event(event))
        violations.extend(self.enforcement_proc.route_event(event))

        if not violations:
            return

        with self._history_lock:
            self._violation_history.extend(violations)

        # Preserve the violation queue as an outward-facing notification bus.
        for violation in violations:
            self.violation_queue.put(violation)

    def start(self) -> None:
        """Start the deterministic governance event consumer."""
        if self._running:
            return
        self._running = True
        self.bus.start()

    def stop(self) -> None:
        """Gracefully stop the governance event consumer."""
        self._running = False
        self.bus.stop()

    def submit_event(self, event: dict) -> None:
        """Submit an event to the canonical Stumpy ingestion queue."""
        self.event_queue.put(event)

    def get_violations(self) -> list[dict]:
        """Return accumulated violations without relying on Queue.empty()."""
        with self._history_lock:
            return list(self._violation_history)

    def generate_report(self) -> str:
        """Generate a compact human-readable report from retained violations."""
        violations = self.get_violations()
        lines = [f"Total violations: {len(violations)}"]
        for index, violation in enumerate(violations, 1):
            vtype = violation.get("type", "unknown")
            source = violation.get("source")
            if source:
                lines.append(f"{index}. {vtype} ({source})")
            else:
                lines.append(f"{index}. {vtype}")
        return "\n".join(lines)

    def verify_identity(self, identity: dict) -> bool:
        """Delegate to identity guard."""
        return self.identity_guard.verify(identity)

    def assert_constitutional(self) -> None:
        """Run constitutional invariant checks at startup."""
        self.constitution.assert_all()

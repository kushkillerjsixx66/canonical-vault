from dataclasses import dataclass
from typing import Any

from .invariants.constitutional_invariants import ConstitutionalInvariants
from .invariants.epistemic_invariants import EpistemicInvariants
from .invariants.runtime_invariants import RuntimeInvariants
from .invariants.sovereignty_invariants import SovereigntyInvariants


@dataclass
class KernelContext:
    identity: dict[str, Any]
    runtime_state: dict[str, Any]
    epistemic_state: dict[str, Any]


class StumpyKernel:
    """
    Minimal core that knows how to evaluate invariants
    against a given context.
    """

    def __init__(self) -> None:
        self.constitution = ConstitutionalInvariants()
        self.epistemic = EpistemicInvariants()
        self.runtime = RuntimeInvariants()
        self.sovereignty = SovereigntyInvariants()

    def evaluate(self, ctx: KernelContext) -> list[dict]:
        violations: list[dict] = []

        if not self.constitution.check(ctx.identity, ctx.runtime_state, ctx.epistemic_state):
            violations.append({"type": "constitutional_violation", "context": ctx})

        if not self.epistemic.check(ctx.epistemic_state):
            violations.append({"type": "epistemic_violation", "context": ctx.epistemic_state})

        if not self.runtime.check(ctx.runtime_state):
            violations.append({"type": "runtime_violation", "context": ctx.runtime_state})

        if not self.sovereignty.check(ctx.identity):
            violations.append({"type": "sovereignty_violation", "context": ctx.identity})

        return violations

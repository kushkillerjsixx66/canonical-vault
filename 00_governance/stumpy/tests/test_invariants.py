from ..invariants.runtime_invariants import RuntimeInvariants
from ..invariants.epistemic_invariants import EpistemicInvariants
from ..invariants.sovereignty_invariants import SovereigntyInvariants


def test_runtime_invariants():
    inv = RuntimeInvariants()
    assert inv.check({"altitude": "runtime"})
    assert not inv.check({"altitude": "nonsense"})


def test_epistemic_invariants():
    inv = EpistemicInvariants()
    assert inv.check({"lineage": ["root"]})
    assert not inv.check({"lineage": "root"})


def test_sovereignty_invariants():
    inv = SovereigntyInvariants()
    assert inv.check({"sovereignty": "root"})
    assert not inv.check({"sovereignty": "invalid"})

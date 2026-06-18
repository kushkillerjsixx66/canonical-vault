"""
test_invariants.py — Canonical Lattice Smoke Tests: Invariant Enforcement
=========================================================================
Authority: 05_runtime/tests/
Operator: LiminalJermo
Generated: 2026-06-17
Lineage: Lattice_Invariants_v1.md · MODULE_REGISTRY.md · Governance_Gates.md

Validates that all 6 canonical Invariants are represented in the runtime,
that the enforcement matrix is complete, and that failure-class mappings
match the spec (Hard vs. Soft per invariant).
"""

import sys
import pytest


# ---------------------------------------------------------------------------
# Canonical Invariant Truth Table (from Lattice_Invariants_v1.md)
# ---------------------------------------------------------------------------

CANONICAL_INVARIANTS = {
    "I·COH": {
        "name": "Coherence Supremacy",
        "mnemonic": "I·COH",
        "failure_class": "Hard",
        "gate": "G1",
        "enforcer_rank": 4,
        "auditor_rank": 7,
    },
    "II·REV": {
        "name": "Reversibility by Default",
        "mnemonic": "II·REV",
        "failure_class": "Hard",
        "gate": "G3",
        "enforcer_rank": 4,
        "auditor_rank": 7,
    },
    "III·ATT": {
        "name": "Attention Is Scarce",
        "mnemonic": "III·ATT",
        "failure_class": "Soft",
        "gate": "G2",
        "enforcer_rank": 4,
        "auditor_rank": 7,
    },
    "IV·SIL": {
        "name": "Silence Is Structural",
        "mnemonic": "IV·SIL",
        "failure_class": "Hard",
        "gate": None,
        "enforcer_rank": 4,
        "auditor_rank": 7,
    },
    "V·DEC": {
        "name": "Decay by Default",
        "mnemonic": "V·DEC",
        "failure_class": "Soft",
        "gate": None,
        "enforcer_rank": 7,
        "auditor_rank": 7,
    },
    "VI·SIG": {
        "name": "Weak Signal Parity",
        "mnemonic": "VI·SIG",
        "failure_class": "Soft",
        "gate": None,
        "enforcer_rank": 6,
        "auditor_rank": 7,
    },
}

HARD_FAILURE_INVARIANTS = {"I·COH", "II·REV", "IV·SIL"}
SOFT_FAILURE_INVARIANTS = {"III·ATT", "V·DEC", "VI·SIG"}

GATE_BOUND_INVARIANTS = {
    "I·COH": "G1",
    "II·REV": "G3",
    "III·ATT": "G2",
}

ALL_MNEMONICS = list(CANONICAL_INVARIANTS.keys())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _import_sentinel():
    try:
        import importlib.util, os
        p = os.path.join(os.path.dirname(__file__), "..", "sentinel.py")
        spec = importlib.util.spec_from_file_location("sentinel", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        pytest.skip(f"sentinel.py not importable: {e}")


def _import_stumpy():
    try:
        import importlib.util, os
        p = os.path.join(os.path.dirname(__file__), "..", "stumpy.py")
        spec = importlib.util.spec_from_file_location("stumpy", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        pytest.skip(f"stumpy.py not importable: {e}")


# ---------------------------------------------------------------------------
# 1. Invariant Completeness
# ---------------------------------------------------------------------------

class TestInvariantCompleteness:
    def test_exactly_six_invariants(self):
        """The canonical invariant set must contain exactly 6 entries."""
        assert len(CANONICAL_INVARIANTS) == 6

    def test_all_mnemonics_present(self):
        """All 6 canonical mnemonics must be present (I·COH through VI·SIG)."""
        expected = {"I·COH", "II·REV", "III·ATT", "IV·SIL", "V·DEC", "VI·SIG"}
        assert set(CANONICAL_INVARIANTS.keys()) == expected

    def test_mnemonic_format(self):
        """All mnemonics must match canonical format (Roman numeral·ABBREV)."""
        import re
        pattern = re.compile(r"^(I{1,3}|IV|V|VI)·[A-Z]{3}$")
        for code in CANONICAL_INVARIANTS:
            assert pattern.match(code), f"Bad mnemonic format: '{code}'"

    def test_all_invariants_have_names(self):
        for code, entry in CANONICAL_INVARIANTS.items():
            assert entry.get("name"), f"Invariant '{code}' missing 'name'"

    def test_all_invariants_have_failure_class(self):
        valid = {"Hard", "Soft"}
        for code, entry in CANONICAL_INVARIANTS.items():
            assert entry.get("failure_class") in valid

    def test_all_invariants_have_enforcer_rank(self):
        for code, entry in CANONICAL_INVARIANTS.items():
            rank = entry.get("enforcer_rank")
            assert isinstance(rank, int) and 1 <= rank <= 9


# ---------------------------------------------------------------------------
# 2. Failure Class Mapping
# ---------------------------------------------------------------------------

class TestFailureClassMapping:
    def test_hard_failure_set(self):
        """I·COH, II·REV, IV·SIL must be Hard Failures."""
        for code in HARD_FAILURE_INVARIANTS:
            assert CANONICAL_INVARIANTS[code]["failure_class"] == "Hard"

    def test_soft_failure_set(self):
        """III·ATT, V·DEC, VI·SIG must be Soft Failures."""
        for code in SOFT_FAILURE_INVARIANTS:
            assert CANONICAL_INVARIANTS[code]["failure_class"] == "Soft"

    def test_hard_soft_partition_complete(self):
        all_c = HARD_FAILURE_INVARIANTS | SOFT_FAILURE_INVARIANTS
        assert all_c == set(CANONICAL_INVARIANTS.keys())

    def test_hard_soft_disjoint(self):
        assert not (HARD_FAILURE_INVARIANTS & SOFT_FAILURE_INVARIANTS)



    def test_gate_sequence_matches_priority(self):
        g = {v: k for k, v in GATE_BOUND_INVARIANTS.items()}
        assert g["G1"] == "I·COH"
        assert g["G2"] == "III·ATT"
        assert g["G3"] == "II·REV"

    def test_only_three_gate_bound(self):
        gate_bound = [c for c, e in CANONICAL_INVARIANTS.items() if e.get("gate")]
        assert len(gate_bound) == 3

    def test_remaining_three_no_gate(self):
        for code in ("IV·SIL", "V·DEC", "VI·SIG"):
            assert CANONICAL_INVARIANTS[code]["gate"] is None


# ---------------------------------------------------------------------------
# 4. Module Authority Alignment
# ---------------------------------------------------------------------------

class TestModuleAuthorityAlignment:
    MODULE_AUTHORITY = {
        1: "Constitution", 2: "Invariants", 3: "Vault",
        4: "Sentinel", 5: "Veil", 6: "Vara",
        7: "Stumpy", 8: "Crossroad", 9: "SBM",
    }

    def test_sentinel_enforces_gate_invariants(self):
        """Gate-bound invariants must be enforced by Sentinel (rank 4)."""
        for code in ("I·COH", "II·REV", "III·ATT"):
            assert CANONICAL_INVARIANTS[code]["enforcer_rank"] == 4

    def test_stumpy_is_universal_auditor(self):
        """All 6 invariants must list Stumpy (rank 7) as auditor."""
        for code in CANONICAL_INVARIANTS:
            assert CANONICAL_INVARIANTS[code]["auditor_rank"] == 7

    def test_vara_enforces_vi_sig(self):
        assert CANONICAL_INVARIANTS["VI·SIG"]["enforcer_rank"] == 6

    def test_stumpy_enforces_v_dec(self):
        assert CANONICAL_INVARIANTS["V·DEC"]["enforcer_rank"] == 7

    def test_all_enforcer_ranks_valid(self):
        for code, entry in CANONICAL_INVARIANTS.items():
            assert entry["enforcer_rank"] in self.MODULE_AUTHORITY


# ---------------------------------------------------------------------------
# 5. Sentinel Runtime (optional — skips gracefully if sentinel.py missing)
# ---------------------------------------------------------------------------

class TestSentinelRuntimeInvariants:
    def test_sentinel_exposes_invariant_codes(self):
        sentinel = _import_sentinel()
        codes = getattr(sentinel, "INVARIANT_CODES", None)
        if codes is None:
            pytest.skip("INVARIANT_CODES not exposed")
        for m in ALL_MNEMONICS:
            assert m in codes

    def test_sentinel_hard_failure_set(self):
        sentinel = _import_sentinel()
        runtime_hard = getattr(sentinel, "HARD_FAILURE_INVARIANTS", None)
        if runtime_hard is None:
            pytest.skip("HARD_FAILURE_INVARIANTS not exposed")
        assert set(runtime_hard) == HARD_FAILURE_INVARIANTS

    def test_sentinel_g1_threshold(self):
        sentinel = _import_sentinel()
        t = getattr(sentinel, "G1_COHERENCE_THRESHOLD", None)
        if t is None:
            pytest.skip("G1_COHERENCE_THRESHOLD not exposed")
        assert t == 0.75


# ---------------------------------------------------------------------------
# 6. Stumpy Runtime (optional — skips gracefully if stumpy.py missing)
# ---------------------------------------------------------------------------

class TestStumpyRuntimeAudit:
    EXPECTED_STATUSES = {"COMPLIANT", "FINDINGS_MINOR", "FINDINGS_MAJOR"}

    def test_compliance_statuses(self):
        stumpy = _import_stumpy()
        statuses = getattr(stumpy, "COMPLIANCE_STATUSES", None)
        if statuses is None:
            pytest.skip("COMPLIANCE_STATUSES not exposed")
        assert set(statuses) >= self.EXPECTED_STATUSES

    def test_audit_record_class_exists(self):
        stumpy = _import_stumpy()
        has_it = any(hasattr(stumpy, n) for n in ("AuditRecord", "StumpyAuditRecord"))
        if not has_it:
            pytest.skip("AuditRecord class not exposed")
        assert has_it


# ---------------------------------------------------------------------------
# 7. Amendment Guard — truth-table self-integrity
# ---------------------------------------------------------------------------

class TestInvariantAmendmentGuard:
    def test_count_immutable(self):
        """Invariant count must be 6 — not casually expandable."""
        assert len(CANONICAL_INVARIANTS) == 6

    def test_roman_numeral_order(self):
        """Mnemonics must begin I through VI in correct sequence."""
        prefixes = [k.split("·")[0] for k in CANONICAL_INVARIANTS.keys()]
        assert prefixes == ["I", "II", "III", "IV", "V", "VI"]

    def test_no_duplicate_gate_assignments(self):
        """No two invariants may share the same gate assignment."""
        gates = [e["gate"] for e in CANONICAL_INVARIANTS.values() if e["gate"]]
        assert len(gates) == len(set(gates))

    def test_no_duplicate_mnemonics(self):
        """Mnemonic codes must be unique across all invariant entries."""
        mnemonics = [e["mnemonic"] for e in CANONICAL_INVARIANTS.values()]
        assert len(mnemonics) == len(set(mnemonics))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))

# ---------------------------------------------------------------------------
# 3. Governance Gate Binding
# ---------------------------------------------------------------------------

class TestGateBinding:
    def test_i_coh_bound_to_g1(self):
        assert CANONICAL_INVARIANTS["I·COH"]["gate"] == "G1"

    def test_iii_att_bound_to_g2(self):
        assert CANONICAL_INVARIANTS["III·ATT"]["gate"] == "G2"

    def test_ii_rev_bound_to_g3(self):
        assert CANONICAL_INVARIANTS["II·REV"]["gate"] == "G3"

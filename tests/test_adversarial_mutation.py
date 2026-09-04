"""Adversarial mutation tests for constitutional coherence detection.

These tests deliberately corrupt isolated repository copies and require Stumpy's
coherence probe to reject every mutation. The production repository is never
mutated by the tests themselves.
"""

from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BEHAVIORAL_PATH = ROOT / "05_runtime" / "stumpy" / "behavioral.py"


def _load_behavioral():
    spec = importlib.util.spec_from_file_location("stumpy_behavioral_mutation_test", BEHAVIORAL_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load {BEHAVIORAL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestAdversarialCoherenceMutations(unittest.TestCase):
    def _mutated_repository(self) -> Path:
        temp = tempfile.mkdtemp(prefix="lattice-mutation-")
        destination = Path(temp) / "canonical-vault"
        shutil.copytree(
            ROOT,
            destination,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
        )
        self.addCleanup(shutil.rmtree, temp, ignore_errors=True)
        return destination

    def _assert_coherence_rejects(self, mutate) -> None:
        repository = self._mutated_repository()
        mutate(repository)
        behavioral = _load_behavioral()
        observed, reason = behavioral.probe_coherence(str(repository))
        self.assertFalse(observed, reason)

    def test_remove_canonical_invariant_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "00_governance" / "authority_graph.yaml"
            lines = path.read_text(encoding="utf-8").splitlines()
            lines.remove("  - constraint_enforcement")
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        self._assert_coherence_rejects(mutate)

    def test_add_undeclared_runtime_invariant_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "05_runtime" / "stumpy" / "audit_matrix.py"
            text = path.read_text(encoding="utf-8")
            text = text.replace(
                '    "constraint_enforcement",\n',
                '    "constraint_enforcement",\n    "unauthorized_invariant",\n',
            )
            path.write_text(text, encoding="utf-8")

        self._assert_coherence_rejects(mutate)

    def test_reordered_invariant_universe_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "05_runtime" / "stumpy" / "audit_matrix.py"
            text = path.read_text(encoding="utf-8")
            text = text.replace(
                '    "coherence",\n    "reversibility",\n',
                '    "reversibility",\n    "coherence",\n',
            )
            path.write_text(text, encoding="utf-8")

        self._assert_coherence_rejects(mutate)

    def test_duplicate_runtime_invariant_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "05_runtime" / "stumpy" / "audit_matrix.py"
            text = path.read_text(encoding="utf-8")
            text = text.replace(
                '    "constraint_enforcement",\n',
                '    "constraint_enforcement",\n    "constraint_enforcement",\n',
            )
            path.write_text(text, encoding="utf-8")

        self._assert_coherence_rejects(mutate)

    def test_runtime_invariant_rename_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "05_runtime" / "stumpy" / "audit_matrix.py"
            text = path.read_text(encoding="utf-8")
            text = text.replace('    "score_honesty",\n', '    "score_integrity",\n')
            path.write_text(text, encoding="utf-8")

        self._assert_coherence_rejects(mutate)

    def test_missing_canonical_invariant_declaration_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "00_governance" / "authority_graph.yaml"
            text = path.read_text(encoding="utf-8")
            text = text.replace("canonical_invariants:\n", "")
            path.write_text(text, encoding="utf-8")

        self._assert_coherence_rejects(mutate)


if __name__ == "__main__":
    unittest.main()

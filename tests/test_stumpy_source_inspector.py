import tempfile
from pathlib import Path

import pytest

from importlib import import_module

RepositorySourceInspector = import_module("05_runtime.stumpy.source_inspector").RepositorySourceInspector


def test_source_inspector_captures_digest_and_metadata():
    with tempfile.TemporaryDirectory() as root:
        path = Path(root) / "fixture.py"
        path.write_text("alpha = 1\nbeta = 2\n", encoding="utf-8")
        inspector = RepositorySourceInspector(root)
        observation = inspector.observe("fixture.py")
        assert observation.path == "fixture.py"
        assert observation.bytes_read == len("alpha = 1\nbeta = 2\n".encode())
        assert observation.line_count == 2
        assert len(observation.digest) == 64


def test_source_inspector_produces_bound_evidence():
    with tempfile.TemporaryDirectory() as root:
        Path(root, "fixture.py").write_text("x = 1\n", encoding="utf-8")
        evidence = RepositorySourceInspector(root).evidence(
            evidence_id="SRC-001",
            claim_id="CLAIM-001",
            relative_path="fixture.py",
        )
        assert evidence.source_ref == "fixture.py"
        assert evidence.verify_digest()
        assert evidence.is_independently_observable()


def test_source_inspector_rejects_path_escape():
    with tempfile.TemporaryDirectory() as root:
        inspector = RepositorySourceInspector(root)
        with pytest.raises(ValueError):
            inspector.observe("../outside.py")

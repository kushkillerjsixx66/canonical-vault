"""Read-only repository source evidence acquisition for Stumpy."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Optional

from .evidence import EvidenceKind, EvidenceRecord


@dataclass(frozen=True)
class SourceObservation:
    path: str
    digest: str
    bytes_read: int
    line_count: int
    content: str


class RepositorySourceInspector:
    """Acquire immutable source evidence without modifying repository state."""

    def __init__(self, repository_root: str | Path):
        self.root = Path(repository_root).resolve()

    def observe(self, relative_path: str) -> SourceObservation:
        candidate = (self.root / relative_path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("source path escapes repository root") from exc
        if not candidate.is_file():
            raise FileNotFoundError(relative_path)
        content = candidate.read_text(encoding="utf-8")
        raw = content.encode("utf-8")
        return SourceObservation(
            path=relative_path,
            digest=hashlib.sha256(raw).hexdigest(),
            bytes_read=len(raw),
            line_count=len(content.splitlines()),
            content=content,
        )

    def evidence(
        self,
        *,
        evidence_id: str,
        claim_id: str,
        relative_path: str,
        evaluator_id: str = "stumpy.source_inspector",
        evaluator_version: str = "1.0.0",
    ) -> EvidenceRecord:
        observation = self.observe(relative_path)
        return EvidenceRecord.create(
            evidence_id=evidence_id,
            claim_id=claim_id,
            kind=EvidenceKind.SOURCE,
            target=relative_path,
            method="read-only-source-observation",
            evaluator_id=evaluator_id,
            evaluator_version=evaluator_version,
            source_ref=relative_path,
            payload={
                "sha256": observation.digest,
                "bytes_read": observation.bytes_read,
                "line_count": observation.line_count,
            },
        )

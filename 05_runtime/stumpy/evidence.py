"""Evidence primitives for Stumpy.

Evidence is immutable, content-addressed, and explicitly bound to a claim.
This module never mutates canonical state and never decides truth by itself.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, Mapping, Optional


class EvidenceKind(str, Enum):
    SOURCE = "SOURCE"
    SPECIFICATION = "SPECIFICATION"
    RUNTIME = "RUNTIME"
    TEST = "TEST"
    STATE = "STATE"
    LINEAGE = "LINEAGE"
    RECEIPT = "RECEIPT"
    ASSERTION = "ASSERTION"


def _canonical_payload(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    claim_id: str
    kind: EvidenceKind
    target: str
    method: str
    evaluator_id: str
    evaluator_version: str
    captured_at: str
    digest: Optional[str] = None
    source_ref: Optional[str] = None
    lineage_ref: Optional[str] = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        evidence_id: str,
        claim_id: str,
        kind: EvidenceKind,
        target: str,
        method: str,
        evaluator_id: str,
        evaluator_version: str,
        payload: Mapping[str, Any],
        source_ref: Optional[str] = None,
        lineage_ref: Optional[str] = None,
    ) -> "EvidenceRecord":
        normalized = dict(payload)
        digest = hashlib.sha256(_canonical_payload(normalized)).hexdigest()
        return cls(
            evidence_id=evidence_id,
            claim_id=claim_id,
            kind=kind,
            target=target,
            method=method,
            evaluator_id=evaluator_id,
            evaluator_version=evaluator_version,
            captured_at=datetime.now(timezone.utc).isoformat(),
            digest=digest,
            source_ref=source_ref,
            lineage_ref=lineage_ref,
            payload=normalized,
        )

    def is_assertion_only(self) -> bool:
        return self.kind is EvidenceKind.ASSERTION

    def verify_digest(self) -> bool:
        if self.digest is None:
            return False
        return hashlib.sha256(_canonical_payload(dict(self.payload))).hexdigest() == self.digest

    def is_independently_observable(self) -> bool:
        return self.kind is not EvidenceKind.ASSERTION and bool(self.method) and bool(self.evaluator_id)

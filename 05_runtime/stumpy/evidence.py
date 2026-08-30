"""Evidence primitives for Stumpy.

The module deliberately models evidence as immutable records. It does not
perform canonical mutation or decide constitutional truth by itself.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
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
        digest = hashlib.sha256(
            repr(sorted(payload.items())).encode("utf-8")
        ).hexdigest()
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
            payload=dict(payload),
        )

    def is_assertion_only(self) -> bool:
        return self.kind is EvidenceKind.ASSERTION

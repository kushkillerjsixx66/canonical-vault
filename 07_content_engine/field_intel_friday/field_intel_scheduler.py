from typing import Any, List
from datetime import datetime, UTC
from pathlib import Path

from vara.scan_pipeline.vara_scan_pipeline import VaraScanPipeline
from vault_pipeline.vault_chain.vault_chain import VaultChain
from .field_intel_reporter import FieldIntelReporter


class FieldIntelScheduler:
    """Canonical Field INTEL Friday Scheduler."""

    _vault_root = "vault"

    def __init__(self, stumpy_event_queue, vault_root=None):
        root = self._vault_root if vault_root is None else vault_root
        self._pipeline = VaraScanPipeline(stumpy_event_queue)
        self._chain = VaultChain(root=Path(root) / "chain")
        self._reporter = FieldIntelReporter()
        self._vault_root = root

    def run(self, artifacts: List[dict[str, Any]], runtime_state: dict[str, Any]) -> str:
        lineage_entries = self._chain.load_all()
        results = []

        for artifact in artifacts:
            result = self._pipeline.run(
                artifact=artifact,
                lineage=lineage_entries,
                runtime_state=runtime_state,
            )
            if result:
                results.append(result)

        report = self._reporter.render(results)
        return self._store_report(report)

    def _store_report(self, report: str) -> str:
        ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        root = Path(self._vault_root)
        report_dir = root / "intel_reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        path = report_dir / f"field_intel_{ts}.txt"
        path.write_text(report)
        return str(path)

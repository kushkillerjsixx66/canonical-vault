from typing import Any, List
from datetime import datetime

from vara.scan_pipeline.vara_scan_pipeline import VaraScanPipeline
from vault_pipeline.vault_chain.vault_chain import VaultChain
from .field_intel_reporter import FieldIntelReporter


class FieldIntelScheduler:
    """
    Canonical Field INTEL Friday Scheduler.

    Responsibilities:
    - Load all lineage entries from Vault Chain
    - Identify artifacts eligible for scanning
    - Run Vara Scan Pipeline on each
    - Collect results
    - Generate Field INTEL Friday report
    - Store report in Vault
    """

    def __init__(self, stumpy_event_queue, vault_root="vault"):
        self._pipeline = VaraScanPipeline(stumpy_event_queue)
        self._chain = VaultChain(root=f"{vault_root}/chain")
        self._reporter = FieldIntelReporter()
        self._vault_root = vault_root

    def run(self, artifacts: List[dict[str, Any]], runtime_state: dict[str, Any]) -> str:
        """
        Executes the full Field INTEL Friday cycle.

        Returns the path to the generated report.
        """
        lineage_entries = self._chain.load_all()
        results = []

        for artifact in artifacts:
            # Each artifact is scanned with the full lineage chain
            result = self._pipeline.run(
                artifact=artifact,
                lineage=lineage_entries,
                runtime_state=runtime_state,
            )
            if result:
                results.append(result)

        report = self._reporter.render(results)
        path = self._store_report(report)
        return path

    # ------------------------------------------------------------------
    # INTERNAL STORAGE
    # ------------------------------------------------------------------

    def _store_report(self, report: str) -> str:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = f"{self._vault_root}/intel_reports/field_intel_{ts}.txt"

        import os
        os.makedirs(f"{self._vault_root}/intel_reports", exist_ok=True)

        with open(path, "w") as f:
            f.write(report)

        return path

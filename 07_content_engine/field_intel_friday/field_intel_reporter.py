from typing import List
from vara.scan.vara_scan_schema import VaraScanResult


class FieldIntelReporter:
    """
    Canonical Field INTEL Friday Reporter.

    Produces a human-readable intelligence summary.
    """

    def render(self, results: List[VaraScanResult]) -> str:
        lines = []
        lines.append("=== FIELD INTEL FRIDAY REPORT ===")
        lines.append(f"Total scans: {len(results)}\n")

        for r in results:
            seq = r.lineage[-1]["seq"]
            lines.append(f"--- Artifact Lineage #{seq} ---")

            lines.append("Weak Signals:")
            for s in r.weak_signals:
                lines.append(f"- {s.key}: {s.description}")

            lines.append("Anomalies:")
            for a in r.anomalies:
                lines.append(f"- {a.field}: {a.reason}")

            lines.append("Trends:")
            for t in r.trends:
                lines.append(f"- {t.name} ({len(t.signals)} signals)")

            lines.append("")

        return "\n".join(lines)

from .vara_scan_schema import VaraScanResult


class VaraScanReporter:
    def render(self, scan: VaraScanResult) -> str:
        lines = []
        lines.append("=== VARA SCAN REPORT ===")
        lines.append(f"Lineage entries: {len(scan.lineage)}")

        lines.append("\nWeak Signals:")
        for s in scan.weak_signals:
            lines.append(f"- {s.key}: {s.description}")

        lines.append("\nEmergent Trends:")
        for t in scan.trends:
            lines.append(f"- {t.name} ({len(t.signals)} signals)")

        lines.append("\nAnomalies:")
        for a in scan.anomalies:
            lines.append(f"- {a.field}: {a.reason}")

        lines.append("\nUnspecified Fields:")
        for u in scan.unspecified:
            lines.append(f"- {u}")

        return "\n".join(lines)

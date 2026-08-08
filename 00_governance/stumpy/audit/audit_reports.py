"""
audit_reports.py
Stumpy Governance Engine — audit report rendering and structured output.

Operator: JRM-01 @liminaljermo  Version: 1.1  Revised: 2026-08-08
REMEDIATION: expanded from bare render_report() stub — added AuditReport
             dataclass, multi-format rendering (text/json), and section headers.
"""

from __future__ import annotations
import json
import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .audit_payload import AuditSummary


@dataclass
class AuditReport:
    """
    Full audit report envelope — wraps an AuditSummary with metadata
    and exposes text + JSON rendering.
    """
    report_id:   str          = field(
        default_factory=lambda: f"RPT-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    )
    generated_at: str         = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat()
    )
    subsystem:   str          = "stumpy"
    window_start: Optional[str] = None
    window_end:   Optional[str] = None
    summary:     Optional[AuditSummary] = None

    # ------------------------------------------------------------------ #
    def render_text(self) -> str:
        """Return a human-readable plain-text audit report."""
        s = self.summary
        lines: List[str] = [
            "=" * 60,
            f"CANON AUDIT REPORT  [{self.report_id}]",
            f"Generated : {self.generated_at}",
            f"Subsystem : {self.subsystem}",
        ]
        if self.window_start or self.window_end:
            lines.append(f"Window    : {self.window_start} → {self.window_end}")
        lines.append("=" * 60)

        if s is None:
            lines.append("No summary data.")
            return "\n".join(lines)

        lines += [
            f"Total violations : {s.total}",
            f"Escalated        : {s.escalated}",
            "",
            "── By Severity ──",
        ]
        for sev, cnt in sorted(s.by_severity.items()):
            lines.append(f"  {sev:<12} {cnt}")

        lines += ["", "── By Subsystem ──"]
        for sub, cnt in sorted(s.by_subsystem.items()):
            lines.append(f"  {sub:<20} {cnt}")

        lines += ["", "── By Type ──"]
        for vtype, cnt in sorted(s.by_type.items()):
            lines.append(f"  {vtype:<25} {cnt}")

        if s.violations:
            lines += ["", "── Violation Details ──"]
            for v in s.violations:
                inv  = v.get("invariant", "?")
                desc = v.get("description", v.get("message", ""))
                sev  = v.get("severity", "?")
                sub  = v.get("subsystem", "?")
                lines.append(f"  [{sev}] {sub} / {inv} : {desc}")

        lines.append("=" * 60)
        return "\n".join(lines)

    def render_json(self) -> str:
        """Return a JSON-serializable dict of the full report."""
        return json.dumps({
            "report_id":    self.report_id,
            "generated_at": self.generated_at,
            "subsystem":    self.subsystem,
            "window_start": self.window_start,
            "window_end":   self.window_end,
            "summary":      self.summary.to_dict() if self.summary else None,
        }, indent=2)


# ─── backward-compatible function (preserved from original stub) ────────── #

def render_report(summary: dict) -> str:
    """
    Render a human-readable report from a raw summary dict.

    Kept for backward compatibility with callers that pass a plain dict
    (e.g. from summarize_violations()).  For new callers prefer AuditReport.
    """
    lines = [f"Total violations: {summary.get('total', 0)}"]
    for t, count in summary.get("by_type", {}).items():
        lines.append(f"  - {t}: {count}")
    sev = summary.get("by_severity", {})
    if sev:
        lines.append("By severity:")
        for s, c in sev.items():
            lines.append(f"  - {s}: {c}")
    return "\n".join(lines)

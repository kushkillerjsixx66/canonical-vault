def render_report(summary: dict) -> str:
    """
    Render a human‑readable report from a summary.
    """
    lines = [f"Total violations: {summary['total']}"]
    for t, count in summary["by_type"].items():
        lines.append(f"- {t}: {count}")
    return "\n".join(lines)

#!/usr/bin/env python3
"""Canonical Vault repository/index self-audit.

Version 0.1 intentionally observes and reports. It never mutates canonical state.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1"
DEFAULT_INDEX = "VAULT_INDEX.md"
PATH_RE = re.compile(r"`([^`]+)`")
STATUS_RE = re.compile(r"\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)
IGNORED_DECLARATION_PREFIXES = ("http://", "https://")
DIRECTORY_NAMES = {"dir", "directory"}


@dataclass(frozen=True)
class Finding:
    finding_id: str
    state: str
    plane: str
    path: str
    related_paths: tuple[str, ...]
    claim: str
    observation: str
    evidence: tuple[str, ...]
    severity: str
    recommended_action: str
    requires_operator: bool
    repository_revision: str


def run_git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True, stderr=subprocess.STDOUT
    ).strip()


def tracked_files(repo: Path) -> set[str]:
    return set(run_git(repo, "ls-files").splitlines())


def revision(repo: Path) -> str:
    return run_git(repo, "rev-parse", "HEAD")


def indexed_paths(index_text: str, files: set[str]) -> set[str]:
    paths: set[str] = set()
    for match in PATH_RE.findall(index_text):
        candidate = match.strip()
        if not candidate or candidate.startswith(IGNORED_DECLARATION_PREFIXES):
            continue
        if candidate in files:
            paths.add(candidate)
    return paths


def declared_missing_paths(index_text: str, files: set[str]) -> set[str]:
    missing: set[str] = set()
    for match in PATH_RE.findall(index_text):
        candidate = match.strip()
        if not candidate or candidate.startswith(IGNORED_DECLARATION_PREFIXES):
            continue
        if candidate.endswith("/"):
            continue
        if candidate not in files and not candidate.startswith(".patch_backup_"):
            # Only treat path-like declarations as filesystem claims.
            if "/" in candidate or "." in Path(candidate).name:
                missing.add(candidate)
    return missing


def backup_files(files: set[str]) -> set[str]:
    return {p for p in files if p.startswith(".patch_backup_")}


def build_findings(repo: Path, index_name: str = DEFAULT_INDEX) -> list[Finding]:
    files = tracked_files(repo)
    rev = revision(repo)
    index_path = repo / index_name
    text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    indexed = indexed_paths(text, files)
    missing = declared_missing_paths(text, files)
    backups = backup_files(files)

    findings: list[Finding] = []

    if not index_path.exists():
        findings.append(Finding(
            "IDX-001", "MISSING", "canonical-index", index_name, (),
            "The canonical repository index exists.",
            "The configured index file is absent.", (index_name,), "HIGH",
            "Restore or explicitly replace the canonical index under operator control.", True, rev,
        ))
        return findings

    undiscovered = sorted(files - indexed)
    # Exclude the index itself and common repository metadata from discovery noise.
    undiscovered = [p for p in undiscovered if p != index_name and not p.startswith(".git/")]

    if undiscovered:
        findings.append(Finding(
            "IDX-002", "DISCOVERED", "canonical-index", "VAULT_INDEX.md", tuple(undiscovered),
            "Tracked repository artifacts are represented by the canonical index.",
            f"{len(undiscovered)} tracked artifacts are not represented by an exact indexed path.",
            tuple(undiscovered[:50]), "MEDIUM",
            "Classify each artifact and update the index only after governed review.", True, rev,
        ))

    if missing:
        findings.append(Finding(
            "IDX-003", "MISSING", "canonical-index", "VAULT_INDEX.md", tuple(sorted(missing)),
            "Indexed filesystem claims resolve to tracked repository artifacts.",
            f"{len(missing)} indexed path claims do not resolve to tracked files.",
            tuple(sorted(missing)[:50]), "MEDIUM",
            "Verify rename/removal history, then reconcile the index without guessing.", True, rev,
        ))

    if backups:
        findings.append(Finding(
            "HY-001", "DISCOVERED", "hygiene", ".patch_backup_*", tuple(sorted(backups)),
            "Repository state contains intentional canonical artifacts rather than unmanaged backup trees.",
            f"{len(backups)} tracked files live under .patch_backup_* trees.",
            tuple(sorted(backups)[:50]), "LOW",
            "Review backup retention and remove only through an explicit governed change.", True, rev,
        ))

    if not findings:
        findings.append(Finding(
            "AUD-000", "CANONICAL", "canonical-index", index_name, (),
            "Repository state and canonical index are synchronized for the implemented checks.",
            "No unresolved repository/index divergence was detected.", (index_name, rev), "INFO",
            "No action required; repeat the audit after repository mutation.", False, rev,
        ))
    return findings


def audit(repo: Path, index_name: str = DEFAULT_INDEX) -> dict:
    findings = build_findings(repo, index_name)
    states = {f.state for f in findings}
    if "MISSING" in states or "CONFLICT" in states:
        final_state = "REQUIRES_OPERATOR"
    elif "DISCOVERED" in states or "STALE" in states:
        final_state = "DIVERGENT"
    else:
        final_state = "SYNCHRONIZED"

    return {
        "audit_version": VERSION,
        "repository_revision": revision(repo),
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "repository": str(repo.resolve()),
        "index": index_name,
        "final_state": final_state,
        "finding_count": len(findings),
        "findings": [asdict(f) for f in findings],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Path to the repository")
    parser.add_argument("--index", default=DEFAULT_INDEX, help="Canonical index filename")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    result = audit(Path(args.repo), args.index)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Canonical Self-Audit v{VERSION}")
        print(f"Revision: {result['repository_revision']}")
        print(f"State: {result['final_state']}")
        for finding in result["findings"]:
            print(f"[{finding['severity']}] {finding['finding_id']} {finding['state']}: {finding['observation']}")
            print(f"  Action: {finding['recommended_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

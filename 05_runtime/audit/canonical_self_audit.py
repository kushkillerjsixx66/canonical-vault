#!/usr/bin/env python3
"""Canonical Vault repository/index self-audit.

Version 0.2 observes and reports. It never mutates canonical state.
Directory entries in VAULT_INDEX.md provide coverage for tracked files beneath
that directory; backup trees remain separately classified as hygiene findings.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.2"
DEFAULT_INDEX = "VAULT_INDEX.md"
PATH_RE = re.compile(r"`([^`]+)`")
IGNORED_DECLARATION_PREFIXES = ("http://", "https://")
BACKUP_PREFIX = ".patch_backup_"


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


def declared_paths(index_text: str) -> set[str]:
    paths: set[str] = set()
    for match in PATH_RE.findall(index_text):
        candidate = match.strip()
        if candidate and not candidate.startswith(IGNORED_DECLARATION_PREFIXES):
            paths.add(candidate)
    return paths


def indexed_paths(index_text: str, files: set[str]) -> set[str]:
    """Return tracked files covered by exact file or directory declarations."""
    declarations = declared_paths(index_text)
    indexed: set[str] = set()
    for candidate in declarations:
        if candidate.endswith("/"):
            prefix = candidate
            indexed.update(p for p in files if p.startswith(prefix))
        elif candidate in files:
            indexed.add(candidate)
    return indexed


def declared_missing_paths(index_text: str, files: set[str]) -> set[str]:
    """Return declarations that look like missing file paths, not directory claims."""
    missing: set[str] = set()
    for candidate in declared_paths(index_text):
        if candidate.endswith("/") or candidate.startswith(BACKUP_PREFIX):
            continue
        if candidate not in files and ("/" in candidate or "." in Path(candidate).name):
            missing.add(candidate)
    return missing


def backup_files(files: set[str]) -> set[str]:
    return {p for p in files if p.startswith(BACKUP_PREFIX)}


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
    undiscovered = [
        p for p in undiscovered
        if p != index_name and not p.startswith(BACKUP_PREFIX) and not p.startswith(".git/")
    ]

    if undiscovered:
        findings.append(Finding(
            "IDX-002", "DISCOVERED", "canonical-index", index_name, tuple(undiscovered),
            "Tracked repository artifacts are represented by the canonical index through exact or directory coverage.",
            f"{len(undiscovered)} tracked artifacts are not represented by an exact indexed path or indexed directory.",
            tuple(undiscovered[:50]), "MEDIUM",
            "Classify each artifact and update the index only after governed review.", True, rev,
        ))

    if missing:
        findings.append(Finding(
            "IDX-003", "MISSING", "canonical-index", index_name, tuple(sorted(missing)),
            "Indexed filesystem claims resolve to tracked repository artifacts.",
            f"{len(missing)} indexed path claims do not resolve to tracked files.",
            tuple(sorted(missing)[:50]), "MEDIUM",
            "Verify rename/removal history, then reconcile the index without guessing.", True, rev,
        ))

    if backups:
        findings.append(Finding(
            "HY-001", "DISCOVERED", "hygiene", BACKUP_PREFIX, tuple(sorted(backups)),
            "Repository state contains intentional canonical artifacts rather than unmanaged backup trees.",
            f"{len(backups)} tracked files live under {BACKUP_PREFIX}* trees.",
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

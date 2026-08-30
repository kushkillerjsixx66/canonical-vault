"""
LMES Smoke Test (v1.2)
Verifies structural presence of required protocol markers.
Does not evaluate reasoning quality.
"""

REQUIRED_MARKERS_COMPLIANT = [
    "[FRAME]",
    "[CONSTRAIN]",
    "[CP1]",
    "[REASONING]",
    "[CP2]",
    "[FINALIZATION]",
    "[CP3]",
    "AUDIT_LOG",  # or [AUDIT]
    "[EXIT]",
]

REQUIRED_MARKERS_FAILURE = [
    "FAILURE_LOG",
]


def check_compliant_run(transcript: str) -> list[str]:
    """Return list of missing required markers for a compliant-path run."""
    missing = [m for m in REQUIRED_MARKERS_COMPLIANT if m not in transcript]
    # AUDIT_LOG may appear as [AUDIT] in some transcripts
    if "AUDIT_LOG" in missing and "[AUDIT]" in transcript:
        missing = [m for m in missing if m != "AUDIT_LOG"]
    return missing


def check_failure_run(transcript: str) -> list[str]:
    """Return list of missing required markers for a hard-failure run."""
    return [m for m in REQUIRED_MARKERS_FAILURE if m not in transcript]


def test_compliant_markers_present():
    """Example structural check — feed a real transcript in CI or manual runs."""
    # Placeholder: real transcripts should be supplied by the test harness.
    sample = """
    [FRAME]
    [CONSTRAIN]
    [CP1]
    [REASONING]
    [CP2]
    [FINALIZATION]
    [CP3]
    AUDIT_LOG:
    [EXIT]
    """
    missing = check_compliant_run(sample)
    assert missing == [], f"Missing markers: {missing}"


def test_failure_markers_present():
    sample = "FAILURE_LOG: invariant violation"
    missing = check_failure_run(sample)
    assert missing == [], f"Missing markers: {missing}"


if __name__ == "__main__":
    test_compliant_markers_present()
    test_failure_markers_present()
    print("LMES smoke protocol structural checks passed.")

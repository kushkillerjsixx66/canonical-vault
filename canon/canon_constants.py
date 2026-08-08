"""
canon_constants.py
Canonical operator-grade constants for CDS-Ω1.

Source: cds_omega1.py  Operator: JRM-01 @liminaljermo
Absorbed verbatim from the operator file; these values are the
single source of truth across all Canon subsystems.

System Invariants (inherited):
    I·SRC  — full provenance on every construct
    II·SCR — scores derived from signal data; no inflation
    V·SIL  — null result valid; logged, not suppressed
    VI·BND — CDS surfaces constructs only; no directives
"""

from __future__ import annotations
import datetime
import hashlib

# ─────────────────────────────────────────────────────────────────────────────
# Domain Registry
# ─────────────────────────────────────────────────────────────────────────────

DOMAINS = ["econ", "crypto", "geopolitics", "world_pol", "industrial"]

# Canonical domain ID → CDS DomainID enum value mapping
DOMAIN_ID_MAP = {
    "econ":        "ECON",
    "crypto":      "CRYPTO",
    "geopolitics": "GEOPOL",
    "world_pol":   "WORLDPOL",
    "industrial":  "INDUSTRIAL",
}

# ─────────────────────────────────────────────────────────────────────────────
# Operational Thresholds  (from cds_omega1.py §CONSTANTS)
# ─────────────────────────────────────────────────────────────────────────────

ANOMALY_THRESHOLD       = 0.70   # single-signal anomaly gate
CONTRADICTION_THRESHOLD = 0.55   # CMX divergence gate  (was 0.70 in Phase-1 stub)
REINFORCEMENT_THRESHOLD = 0.60   # CDCE reinforcement gate
DRIFT_SURGE_THRESHOLD   = 0.45   # DCA surge gate        (was 0.60 in Phase-1 stub)

# Contradiction severity → Paradox Engine escalation gate
CONTRADICTION_HIGH_THRESHOLD = 0.70   # retained from spec §5; CMX cell threshold
CONFIDENCE_GATE              = 0.40   # CSP minimum confidence to escalate

# Mode trigger counts
ACTIVE_MODE_TRIGGER    = 3   # number of domain anomalies to enter ACTIVE mode
RECURSIVE_MODE_TRIGGER = 2   # number of contradictions to enter RECURSIVE mode

# ─────────────────────────────────────────────────────────────────────────────
# Domain Weights  (canonical, from cds_omega1.py §DOMAIN_WEIGHT)
# ─────────────────────────────────────────────────────────────────────────────

DOMAIN_WEIGHT: dict[str, float] = {
    "econ":        0.90,
    "crypto":      0.75,
    "geopolitics": 0.85,
    "world_pol":   0.80,
    "industrial":  0.70,
}

# ─────────────────────────────────────────────────────────────────────────────
# Domain Relationship Map  (structural priors, from cds_omega1.py)
# +1 = domains expected to move together
# -1 = domains expected to move inversely
# ─────────────────────────────────────────────────────────────────────────────

DOMAIN_RELATIONSHIP_MAP: dict[tuple[str, str], int] = {
    ("econ",        "crypto"):      +1,
    ("econ",        "geopolitics"): -1,
    ("econ",        "world_pol"):   -1,
    ("econ",        "industrial"):  +1,
    ("crypto",      "geopolitics"): +1,
    ("crypto",      "world_pol"):   +1,
    ("crypto",      "industrial"):  -1,
    ("geopolitics", "world_pol"):   +1,
    ("geopolitics", "industrial"):  +1,
    ("world_pol",   "industrial"):  -1,
}

# ─────────────────────────────────────────────────────────────────────────────
# Contradiction Templates  (from cds_omega1.py §CONTRADICTION_TEMPLATES)
# Human-readable paradox descriptions keyed by domain pair + direction.
# "positive" = domain_a signal > domain_b signal
# "negative" = domain_a signal < domain_b signal
# ─────────────────────────────────────────────────────────────────────────────

CONTRADICTION_TEMPLATES: dict[tuple[str, str], dict[str, str]] = {
    ("econ", "geopolitics"): {
        "positive": (
            "Economic signals trending positive while geopolitical tension signals are elevated — "
            "market optimism is decoupled from deteriorating foreign-policy conditions."
        ),
        "negative": (
            "Economic contraction signals co-occurring with geopolitical stability — "
            "structural economic weakness not explained by external pressure."
        ),
    },
    ("econ", "world_pol"): {
        "positive": (
            "Strong economic composite contradicted by elevated political instability signals — "
            "political fracture risk is not priced into macro indicators."
        ),
        "negative": (
            "Economic stress signals contradicted by stable political signal environment — "
            "economic weakness is domestically sourced, not politically driven."
        ),
    },
    ("econ", "crypto"): {
        "positive": (
            "Macro economic strength signals contradict elevated crypto volatility — "
            "crypto is diverging from macro fundamentals, suggesting speculative decoupling."
        ),
        "negative": (
            "Economic weakness signals contradict crypto rally indicators — "
            "crypto may be functioning as an alternative store of value under macro stress."
        ),
    },
    ("econ", "industrial"): {
        "positive": (
            "Macro indicators positive while industrial signals show contraction — "
            "economic headline strength is not translating into real-sector output."
        ),
        "negative": (
            "Industrial expansion signals co-occurring with macro weakness — "
            "sectoral strength is not reflected in aggregate economic indicators."
        ),
    },
    ("crypto", "geopolitics"): {
        "positive": (
            "Crypto signals subdued despite elevated geopolitical instability — "
            "expected crypto volatility response to geopolitical risk is absent."
        ),
        "negative": (
            "Crypto volatility elevated despite stable geopolitical signals — "
            "crypto is generating internal instability not driven by foreign-policy risk."
        ),
    },
    ("crypto", "world_pol"): {
        "positive": (
            "Crypto signals quiet despite rising political instability — "
            "political risk has not transmitted into crypto markets."
        ),
        "negative": (
            "Crypto volatility elevated in stable political environment — "
            "crypto instability is structurally internal, not geopolitically driven."
        ),
    },
    ("geopolitics", "world_pol"): {
        "positive": (
            "US foreign relations signals elevated while global political environment shows stability — "
            "US-specific foreign policy stress is not reflected in broader political signals."
        ),
        "negative": (
            "Global political instability signals high while US foreign relations signals are stable — "
            "systemic political risk is not originating from or affecting US foreign posture."
        ),
    },
    ("geopolitics", "industrial"): {
        "positive": (
            "Geopolitical tension signals elevated without corresponding industrial disruption — "
            "supply chain and industrial sector have not yet absorbed foreign-policy shocks."
        ),
        "negative": (
            "Industrial disruption signals elevated in stable geopolitical environment — "
            "industrial stress is structurally or domestically driven, not geopolitically caused."
        ),
    },
    ("world_pol", "industrial"): {
        "positive": (
            "Political instability signals elevated while industrial output signals remain strong — "
            "political risk has not transmitted into real-sector productive capacity."
        ),
        "negative": (
            "Industrial contraction signals alongside stable political environment — "
            "industrial weakness is structural, not politically induced."
        ),
    },
    ("crypto", "industrial"): {
        "positive": (
            "Crypto strength signals alongside industrial weakness — "
            "speculative capital is flowing into crypto rather than productive industrial investment."
        ),
        "negative": (
            "Industrial strength alongside crypto weakness — "
            "capital is rotating from speculative assets into real-sector investment."
        ),
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# I·SRC  Provenance utility  (from cds_omega1.py §_uid)
# ─────────────────────────────────────────────────────────────────────────────

def canon_uid(label: str) -> str:
    """
    I·SRC — short deterministic UID for construct provenance.
    Mirrors cds_omega1._uid() exactly.
    """
    ts = datetime.datetime.utcnow().isoformat()
    return hashlib.md5(f"{label}:{ts}".encode()).hexdigest()[:12]


# ─────────────────────────────────────────────────────────────────────────────
# Relationship lookup helpers
# ─────────────────────────────────────────────────────────────────────────────

def expected_direction(da: str, db: str) -> int | None:
    """
    Return the structural prior (+1 / -1) for a domain pair.
    Checks both orderings. Returns None if pair is undefined.
    """
    return (
        DOMAIN_RELATIONSHIP_MAP.get((da, db)) or
        DOMAIN_RELATIONSHIP_MAP.get((db, da))
    )


def contradiction_template(da: str, db: str, positive: bool) -> str | None:
    """
    Return the operator-authored contradiction description for a domain pair.
    Checks both orderings. Returns None if no template exists.
    """
    tmpl = (
        CONTRADICTION_TEMPLATES.get((da, db)) or
        CONTRADICTION_TEMPLATES.get((db, da))
    )
    if tmpl is None:
        return None
    return tmpl.get("positive" if positive else "negative")

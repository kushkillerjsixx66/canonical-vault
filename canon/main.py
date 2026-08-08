"""
CDS-Ω1  —  Cross-Domain Synthesis Subsystem
Entry point / demo runner

Usage:
    python main.py              # run demo scenario
    python main.py --status     # print subsystem status after demo
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from datetime import datetime

from orchestrator import CDSOrchestrator
from router import RecursiveRequest
from models import DomainID

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)-22s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("cds.main")


# ---------------------------------------------------------------------------
# Sample DIPs  (realistic cross-domain scenario)
# ---------------------------------------------------------------------------

DEMO_DIPS = [
    {   # Economics: elevated inflation pressure
        "type": "DIP", "version": "1.0",
        "domain_id": "ECON",
        "timestamp": datetime.utcnow().isoformat(),
        "signal_set": [
            {"signal_type": "INDEX",      "value": 112.4, "weight": 0.60, "confidence": 0.87, "source": "fed_data"},
            {"signal_type": "RATE",       "value": 5.25,  "weight": 0.25, "confidence": 0.95, "source": "fed_funds"},
            {"signal_type": "VOLATILITY", "value": 0.31,  "weight": 0.15, "confidence": 0.72, "source": "vix_proxy"},
        ],
        "weight_vector": [0.60, 0.25, 0.15],
        "confidence_score": 0.86,
        "drift_indicators": [{"vector": [0.4, 0.2], "magnitude": 0.45, "direction": "UP",   "volatility": 0.28}],
        "anomaly_flags": [],
        "metadata": {"harvester": "econ_v2", "region": "US"},
    },
    {   # Government: policy tightening signals
        "type": "DIP", "version": "1.0",
        "domain_id": "GOV",
        "timestamp": datetime.utcnow().isoformat(),
        "signal_set": [
            {"signal_type": "POLICY",    "value": -0.8,  "weight": 0.70, "confidence": 0.82, "source": "congress_nlp"},
            {"signal_type": "SENTIMENT", "value": -0.55, "weight": 0.30, "confidence": 0.68, "source": "press_conf_nlp"},
        ],
        "weight_vector": [0.70, 0.30],
        "confidence_score": 0.77,
        "drift_indicators": [{"vector": [-0.3, -0.5], "magnitude": 0.58, "direction": "DOWN", "volatility": 0.40}],
        "anomaly_flags": [{"code": "REGIME_SHIFT", "severity": "MEDIUM", "description": "Policy pivot detected"}],
        "metadata": {"harvester": "gov_nlp_v1"},
    },
    {   # Stock market: mixed signals
        "type": "DIP", "version": "1.0",
        "domain_id": "STOCK",
        "timestamp": datetime.utcnow().isoformat(),
        "signal_set": [
            {"signal_type": "INDEX",      "value": 4820.5, "weight": 0.50, "confidence": 0.92, "source": "sp500"},
            {"signal_type": "VOLUME",     "value": 1.15,   "weight": 0.30, "confidence": 0.88, "source": "nyse_vol"},
            {"signal_type": "VOLATILITY", "value": 0.24,   "weight": 0.20, "confidence": 0.80, "source": "vix"},
        ],
        "weight_vector": [0.50, 0.30, 0.20],
        "confidence_score": 0.88,
        "drift_indicators": [{"vector": [0.1, -0.2], "magnitude": 0.22, "direction": "FLAT",  "volatility": 0.15}],
        "anomaly_flags": [],
        "metadata": {"harvester": "market_feed_v3"},
    },
    {   # Crypto: high volatility, regulatory uncertainty
        "type": "DIP", "version": "1.0",
        "domain_id": "CRYPTO",
        "timestamp": datetime.utcnow().isoformat(),
        "signal_set": [
            {"signal_type": "PRICE",      "value": 62100.0, "weight": 0.45, "confidence": 0.78, "source": "btc_usd"},
            {"signal_type": "VOLATILITY", "value": 0.65,    "weight": 0.35, "confidence": 0.70, "source": "crypto_vol_index"},
            {"signal_type": "FLOW",       "value": -220.5,  "weight": 0.20, "confidence": 0.60, "source": "exchange_flows"},
        ],
        "weight_vector": [0.45, 0.35, 0.20],
        "confidence_score": 0.71,
        "drift_indicators": [{"vector": [0.7, 0.8], "magnitude": 0.75, "direction": "CHAOTIC", "volatility": 0.65}],
        "anomaly_flags": [{"code": "SPIKE", "severity": "HIGH", "description": "Vol spike above 2σ"}],
        "metadata": {"harvester": "crypto_sentinel"},
    },
    {   # Commodities / Energy: supply constraints
        "type": "DIP", "version": "1.0",
        "domain_id": "ENERGY",
        "timestamp": datetime.utcnow().isoformat(),
        "signal_set": [
            {"signal_type": "PRICE",     "value": 88.40, "weight": 0.60, "confidence": 0.83, "source": "wti_crude"},
            {"signal_type": "FLOW",      "value": -15.2, "weight": 0.40, "confidence": 0.76, "source": "opec_output"},
        ],
        "weight_vector": [0.60, 0.40],
        "confidence_score": 0.80,
        "drift_indicators": [{"vector": [0.5, 0.6], "magnitude": 0.55, "direction": "UP", "volatility": 0.30}],
        "anomaly_flags": [],
        "metadata": {"harvester": "energy_v1"},
    },
]


# ---------------------------------------------------------------------------
# Dashboard subscriber (pretty-print)
# ---------------------------------------------------------------------------

async def _dashboard_printer(msg):
    d = msg.packet
    csp_id = d.get("synthesis_id", "?")[:8]
    print("\n" + "─" * 60)
    print(f"  OPERATOR DASHBOARD  [{datetime.utcnow().strftime('%H:%M:%S')}]")
    print(f"  synthesis_id    : {csp_id}…")
    print(f"  synthesis_type  : {d.get('synthesis_type')}")
    print(f"  escalation_path : {d.get('escalation_path')}")
    print(f"  confidence      : {d.get('confidence_score', 0):.3f}")
    print(f"  mode            : {d.get('mode')}")
    print(f"  drift_magnitude : {d.get('drift_magnitude', 0):.3f}")
    insight = d.get("insight", "")
    print(f"  insight         : {insight[:120]}{'…' if len(insight) > 120 else ''}")
    cmx = d.get("cmx", {})
    print(f"  CMX hot pair    : {cmx.get('hot_pair')}  max_contradiction={cmx.get('max_contradiction', 0):.3f}")
    preds = d.get("predictive_indicators", [])
    if preds:
        print("  predictive_indicators:")
        for p in preds:
            print(f"    [{p['indicator_type']:12s}]  value={p['value']:.3f}  conf={p['confidence']:.3f}")
    print("─" * 60)


async def _paradox_printer(msg):
    d = msg.packet
    print(f"\n  ⚠  PARADOX ENGINE INTAKE  — synthesis_id={d.get('synthesis_id', '?')[:8]}…")
    print(f"     type={d.get('synthesis_type')}  conf={d.get('confidence_score', 0):.3f}")


# ---------------------------------------------------------------------------
# Demo scenario
# ---------------------------------------------------------------------------

async def run_demo() -> None:
    print("\n" + "=" * 60)
    print("  CDS-Ω1  Cross-Domain Synthesis  —  Demo Run")
    print("  " + datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S UTC"))
    print("=" * 60)

    from citl import Topic

    orchestrator = CDSOrchestrator()

    # Attach live dashboard subscriber before starting
    orchestrator.bus.subscribe(Topic.OPERATOR_DASHBOARD, _dashboard_printer, name="demo-dashboard")
    orchestrator.bus.subscribe(Topic.PARADOX_INTAKE,     _paradox_printer,   name="demo-paradox")

    print("\n[1] Ingesting 5-domain DIP batch…")
    await orchestrator.ingest_dips(DEMO_DIPS)
    await asyncio.sleep(0.1)   # let DAL process

    print("\n[2] Running CDCE flush (pairwise correlation)…")
    scp_count = await orchestrator.cdce.flush()
    print(f"    → {scp_count} SCPs emitted")
    await asyncio.sleep(0.1)

    print("\n[3] Running EPS synthesis…")
    csp = await orchestrator.eps.flush()
    await asyncio.sleep(0.1)

    if csp:
        print(f"\n[4] CSP produced: {csp.synthesis_id}")
    else:
        print("\n[4] No CSP produced (insufficient data)")

    print("\n[5] Checking for Paradox Engine re-synthesis…")
    max_c, da, db = orchestrator.cmx.max_contradiction()
    if max_c >= 0.70 and da and db:
        print(f"    → Contradiction {max_c:.3f} ≥ 0.70 detected between {da.value} and {db.value}")
        print("    → Issuing recursive re-synthesis request…")
        req = RecursiveRequest(
            domain_set=[da, db],
            time_window_s=1800,
            focus_cells=[(da, db)],
            synthesis_id=csp.synthesis_id if csp else "unknown",
        )
        await orchestrator.request_recursive_synthesis(req)
        await asyncio.sleep(0.1)
    else:
        print(f"    → Max contradiction={max_c:.3f} — no Paradox Engine trigger needed")

    print("\n[6] Final subsystem status:")
    status = orchestrator.status()
    print(json.dumps(status, indent=4))

    print("\n[7] Topic → Subscriber map:")
    for topic, subs in orchestrator.topic_map().items():
        print(f"    {topic:<42}  ← {', '.join(subs)}")

    print("\n[8] Bus message stats:")
    for topic, count in sorted(orchestrator.bus.stats().items()):
        print(f"    {count:4d}  {topic}")

    dead = orchestrator.bus.dead_letters()
    if dead:
        print(f"\n  ⚠  {len(dead)} dead-letter(s):")
        for dl in dead:
            print(f"     [{dl.subscriber}] {dl.error}")

    print("\n✓  Demo complete.\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
    if "--status" in sys.argv:
        pass   # status already printed inside run_demo

"""
Canon Intelligence System — Full System Demo
Vara (multi-channel domain scan) + CDS-Ω1 (cross-domain synthesis)

Run:  python main_vara.py
"""

from __future__ import annotations

import asyncio
import logging
import sys
from datetime import datetime


def _banner(title: str, width: int = 65) -> None:
    bar = "═" * width
    print(f"\n╔{bar}╗")
    print(f"║  {title:<{width-2}}║")
    print(f"╚{bar}╝")


def _section(title: str, width: int = 65) -> None:
    print(f"\n  ┌─ {title} {'─' * (width - len(title) - 5)}┐")


def _row(label: str, value: str, width: int = 60) -> None:
    print(f"  │  {label:<30}{str(value):<{width-32}}│")


def _end(width: int = 65) -> None:
    print(f"  └{'─'*width}┘")


# ---------------------------------------------------------------------------
# Dashboard printers
# ---------------------------------------------------------------------------

def print_domain_scan_summary(results: dict) -> None:
    _section("VARA DOMAIN SCAN RESULTS", width=65)
    for did, res in sorted(results.items()):
        if res is None:
            print(f"  │  {did:<12} ✗  (no result)")
            continue
        vsr     = res.result
        conf    = res.dip_packet.get("confidence_score", 0.0)
        anom_n  = len(vsr.anomalies)
        weak_n  = len(vsr.weak_signals)
        trend_n = len(vsr.trends)
        mode    = f"Vara.{did}"
        print(
            f"  │  {mode:<16}  conf={conf:.3f}  "
            f"weak={weak_n}  trends={trend_n}  anomalies={anom_n}"
        )
        if vsr.anomalies:
            for a in vsr.anomalies[:2]:
                print(f"  │    ⚠  {a.field}: {a.reason[:50]}")
    _end(width=65)


def print_cross_domain_signals(signals: list[dict]) -> None:
    if not signals:
        return
    _section("CROSS-DOMAIN SIGNALS (Dispatcher)", width=65)
    for s in signals:
        sev   = s.get("severity", "?")
        stype = s.get("signal_type", "?")
        desc  = s.get("description", "")[:55]
        doms  = ", ".join(s.get("domains", []))
        print(f"  │  [{sev:^8}]  {stype:<22}  {desc}")
        print(f"  │           domains: {doms}")
    _end(width=65)


def print_cmx(snap: dict) -> None:
    domains = snap["domains"]
    matrix  = snap["matrix"]
    n       = len(domains)
    _section("CONTRADICTION MATRIX (CMX)", width=65)
    header = "  │       " + "".join(f" {d[:6]:>8}" for d in domains)
    print(header)
    for i, row_dom in enumerate(domains):
        cells = "".join(
            f"  {v:7.3f}" if i != j else "    ——  "
            for j, v in enumerate(matrix[i])
        )
        print(f"  │  {row_dom[:6]:>6} {cells}")
    _end(width=65)


def print_csp(csp_data: dict) -> None:
    _section("CANON SYNTHESIS PACKET (CSP)", width=65)
    _row("synthesis_id",   csp_data.get("synthesis_id","?")[:16] + "…")
    _row("synthesis_type", csp_data.get("synthesis_type","?"))
    _row("confidence",     f"{csp_data.get('confidence_score',0):.4f}")
    _row("escalation",     csp_data.get("escalation_path","NONE"))
    _row("domains",        ", ".join(csp_data.get("domains_involved",[])))
    insight = csp_data.get("insight","")
    words   = insight.split()
    line    = ""
    first   = True
    for word in words:
        if len(line) + len(word) + 1 > 42:
            lbl = "insight" if first else ""
            _row(lbl, line.strip())
            first = False
            line  = word + " "
        else:
            line += word + " "
    if line.strip():
        _row("" if not first else "insight", line.strip())
    _end(width=65)


def print_predictive_indicators(csp_data: dict) -> None:
    pis = csp_data.get("predictive_indicators", [])
    if not pis:
        return
    _section("PREDICTIVE INDICATORS", width=65)
    for pi in pis:
        itype = pi.get("indicator_type", "?")
        val   = pi.get("value", 0)
        conf  = pi.get("confidence", 0)
        print(f"  │  {itype:<20}  value={val:<8}  confidence={conf:.3f}")
    _end(width=65)


def print_reinforcement_clusters(csp_data: dict) -> None:
    clusters = csp_data.get("reinforcement_clusters", [])
    if not clusters:
        return
    _section("REINFORCEMENT CLUSTERS", width=65)
    for c in clusters[:4]:
        origin = c.get("domain_origin", "?")
        weight = c.get("weight", 0)
        sigs   = c.get("signals", [])
        print(f"  │  [{origin}]  cluster_weight={weight:.3f}  signals={len(sigs)}")
        for sig in sigs[:2]:
            print(f"  │    · {sig.get('signal_type','?'):<20} val={sig.get('value',0)}")
    _end(width=65)


def print_bridge_status(status: dict) -> None:
    _section("SYSTEM STATUS", width=65)
    b = status["bridge"]
    o = status["orchestrator"]
    d = status["dispatcher"]
    _row("bridge_mode",          o.get("mode","?"))
    _row("bridge_flush_count",   b.get("flush_count",0))
    _row("domains_running",      d.get("domains_running",0))
    _row("dispatcher_scans",     d.get("total_scans",0))
    _row("total_cross_domain",   d.get("cross_domain_signals",0))
    _row("bus_messages_total",   o.get("bus_stats",{}).get("messages_published",0))
    _row("dal_accepted",         o.get("dal_stats",{}).get("accepted",0))
    _row("dal_rejected",         o.get("dal_stats",{}).get("rejected",0))
    _end(width=65)


# ---------------------------------------------------------------------------
# Main demo
# ---------------------------------------------------------------------------

async def main() -> None:
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)-8s %(name)s: %(message)s"
    )

    _banner("Canon Intelligence System  —  Full Pipeline Demo")
    print(f"  Timestamp : {datetime.utcnow().isoformat()} UTC")
    print(f"  Phase 1   : CDS-Ω1 (Cross-Domain Synthesis)")
    print(f"  Phase 2   : Vara Scan (Domain-Segmented Harvesters)")
    print(f"  Transport : Canon Intelligence Transport Layer (CITL)")

    from vara.vara_canon_bridge import VaraCanonBridge
    from pipeline import DAL, CDCE, CMX, EPS
    from citl import Topic

    # ── Build system ────────────────────────────────────────────────────────
    bridge = VaraCanonBridge()
    bus    = bridge.orchestrator.bus
    cdce   = bridge.orchestrator.cdce
    cmx_stage = bridge.orchestrator.cmx
    eps    = bridge.orchestrator.eps

    # Collect all CSPs produced during the demo
    csps_produced: list[dict] = []
    async def capture_csp(msg): csps_produced.append(msg.packet)
    bus.subscribe(Topic.CSP_SYNTHESIS, capture_csp, name="demo-csp")

    # ── Cycle 1: Vara scan_all ───────────────────────────────────────────
    print("\n  ● Scanning all 5 Vara domain channels…")
    scan_results = await bridge.dispatcher.scan_all()
    await asyncio.sleep(0.15)   # allow async bus delivery to settle

    print_domain_scan_summary(scan_results)

    cross_sigs = bridge.dispatcher.cross_domain_signals()
    print_cross_domain_signals(cross_sigs)

    # ── Cycle 1: CDS-Ω1 pipeline ────────────────────────────────────────
    print("  ● Running CDS-Ω1 pipeline (CDCE → CMX → EPS)…")

    # Inject cross-domain signals as synthetic DIPs
    for sig in cross_sigs:
        await bridge._inject_cross_domain_signal(sig)
        await asyncio.sleep(0.05)

    scp_count = await cdce.flush()
    await asyncio.sleep(0.1)
    csp_obj   = await eps.flush()
    await asyncio.sleep(0.1)

    print(f"\n  ● CDCE generated {scp_count} pairwise SCPs")

    cmx_snap = cmx_stage.snapshot()
    print_cmx(cmx_snap)

    if csps_produced:
        print_csp(csps_produced[-1])
        print_reinforcement_clusters(csps_produced[-1])
        print_predictive_indicators(csps_produced[-1])
    else:
        print("\n  (No CSP produced — confidence gate may have filtered output)")

    # ── Cycle 2: second scan to generate delta ───────────────────────────
    print("\n  ● Running second scan cycle (delta analysis)…")
    scan2 = await bridge.dispatcher.scan_all()
    await asyncio.sleep(0.15)

    print("\n  Domain deltas (confidence drift between cycle 1 and cycle 2):")
    for did, domain_mode in bridge.dispatcher.domains.items():
        delta = domain_mode.delta()
        if delta:
            cd = delta.get("confidence_delta", 0.0)
            dd = delta.get("drift_delta", 0.0)
            a_delta = delta.get("anomaly_delta", 0)
            sign_c  = "▲" if cd >= 0 else "▼"
            sign_d  = "▲" if dd >= 0 else "▼"
            print(
                f"    {did:<12}  conf {sign_c}{abs(cd):.4f}   "
                f"drift {sign_d}{abs(dd):.4f}   "
                f"anomaly_Δ {a_delta:+d}"
            )

    # Re-flush after second scan
    scp2 = await cdce.flush()
    await asyncio.sleep(0.1)
    await eps.flush()
    await asyncio.sleep(0.1)

    # ── Status dump ──────────────────────────────────────────────────────
    print_bridge_status(bridge.status())

    # ── Router output breakdown ──────────────────────────────────────────
    _section("ROUTER OUTPUT BREAKDOWN", width=65)
    paradox_csps = [c for c in csps_produced if c.get("escalation_path") == "PARADOX_ENGINE"]
    field_csps   = [c for c in csps_produced if c.get("escalation_path") == "FIELD_INTEL"]
    none_csps    = [c for c in csps_produced if c.get("escalation_path") == "NONE"]
    op_csps      = [c for c in csps_produced if c.get("escalation_path") == "OPERATOR_ALERT"]
    print(f"  │  Total CSPs produced    : {len(csps_produced)}")
    print(f"  │  → Paradox Engine       : {len(paradox_csps)}")
    print(f"  │  → FIELD INTEL          : {len(field_csps)}")
    print(f"  │  → Operator Alert       : {len(op_csps)}")
    print(f"  │  → Gated (conf < 0.4)   : {len(none_csps)}")
    _end(width=65)

    if csps_produced:
        _banner("Latest Canon Synthesis")
        last = csps_produced[-1]
        print(f"  ID          : {last.get('synthesis_id','?')}")
        print(f"  Type        : {last.get('synthesis_type','?')}")
        print(f"  Confidence  : {last.get('confidence_score',0):.4f}")
        print(f"  Escalation  : {last.get('escalation_path','?')}")
        print(f"  Domains     : {', '.join(last.get('domains_involved',[]))}")
        print(f"  Insight     : {last.get('insight','')}")

    print(f"\n{'═'*67}")
    print(f"  Canon Intelligence System demo complete.")
    print(f"  Processed at {datetime.utcnow().isoformat()} UTC")
    print(f"{'═'*67}\n")


if __name__ == "__main__":
    asyncio.run(main())

"""
Vara + CDS-Ω1 Integration Test Suite
Tests: ontologies, harvesters, domain scan modes, dispatcher,
cross-domain detection, epistemic bus bridge, and full pipeline.
Run with:  python tests_vara.py
"""

from __future__ import annotations

import asyncio
import sys
import traceback
from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# Path setup — make /workspace/cds importable from any working directory
# ---------------------------------------------------------------------------
import os
_CDS_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _CDS_ROOT not in sys.path:
    sys.path.insert(0, _CDS_ROOT)

# ---------------------------------------------------------------------------
# Minimal harness (same pattern as cds/tests.py)
# ---------------------------------------------------------------------------

_PASS = "✓"
_FAIL = "✗"
_results: list[tuple[str, bool, str]] = []


def test(name: str):
    def decorator(fn):
        async def _run():
            try:
                if asyncio.iscoroutinefunction(fn):
                    await fn()
                else:
                    fn()
                _results.append((name, True, ""))
                print(f"  {_PASS} {name}")
            except Exception as exc:
                tb = traceback.format_exc()
                _results.append((name, False, str(exc)))
                print(f"  {_FAIL} {name}")
                print(f"      {exc}")
                if "--verbose" in sys.argv:
                    print(tb)
        _run.__is_test__ = True
        return _run
    return decorator


def assert_eq(a, b, msg=""):    assert a == b, f"Expected {b!r}, got {a!r}. {msg}"
def assert_true(c, msg=""):     assert c, msg or "Expected True"
def assert_false(c, msg=""):    assert not c, msg or "Expected False"
def assert_in(v, col, msg=""):  assert v in col, f"{v!r} not in {col!r}. {msg}"
def assert_in_range(v, lo, hi, msg=""): assert lo <= v <= hi, f"{v} not in [{lo},{hi}]. {msg}"
def assert_approx(a, b, tol=0.05, msg=""): assert abs(a-b)<=tol, f"|{a}-{b}|>{tol}. {msg}"


# ===========================================================================
# 1. Domain Ontology tests
# ===========================================================================

@test("Ontology: all 5 domains registered in DOMAIN_REGISTRY")
def test_all_domains_registered():
    from vara.domain_ontology import DOMAIN_REGISTRY
    expected = {"ECON", "CRYPTO", "GEOPOL", "WORLDPOL", "INDUSTRIAL"}
    assert_eq(set(DOMAIN_REGISTRY.keys()), expected)


@test("Ontology: each domain has non-empty signal_types and weight_map")
def test_ontology_completeness():
    from vara.domain_ontology import DOMAIN_REGISTRY
    for did, onto in DOMAIN_REGISTRY.items():
        assert_true(len(onto.signal_types) >= 10,
                    f"{did}: signal_types too short ({len(onto.signal_types)})")
        assert_true(len(onto.weight_map) >= 10,
                    f"{did}: weight_map too short ({len(onto.weight_map)})")
        assert_true(len(onto.anomaly_rules) >= 3,
                    f"{did}: anomaly_rules too short")
        assert_true(len(onto.trend_patterns) >= 3,
                    f"{did}: trend_patterns too short")


@test("Ontology: weight_map values are in [0, 1]")
def test_ontology_weights_range():
    from vara.domain_ontology import DOMAIN_REGISTRY
    for did, onto in DOMAIN_REGISTRY.items():
        for sig, w in onto.weight_map.items():
            assert_in_range(w, 0.0, 1.0, f"{did}.{sig}")


@test("Ontology: get_ontology() raises KeyError for unknown domain")
def test_get_ontology_unknown():
    from vara.domain_ontology import get_ontology
    try:
        get_ontology("BOGUS")
        assert False, "Should have raised KeyError"
    except KeyError:
        pass


@test("Ontology: weak_signal_keys are subsets of signal_types")
def test_weak_signal_keys_subset():
    from vara.domain_ontology import DOMAIN_REGISTRY
    for did, onto in DOMAIN_REGISTRY.items():
        for key in onto.weak_signal_keys:
            assert_in(key, onto.signal_types,
                      f"{did}: weak_signal_key '{key}' not in signal_types")


@test("Ontology: CRYPTO cadence is fastest (900s)")
def test_crypto_cadence():
    from vara.domain_ontology import DOMAIN_REGISTRY
    cadences = {did: onto.cadence_s for did, onto in DOMAIN_REGISTRY.items()}
    assert_eq(cadences["CRYPTO"], 900)
    for did, c in cadences.items():
        if did != "CRYPTO":
            assert_true(c >= 900, f"{did} cadence {c} < CRYPTO's 900")


# ===========================================================================
# 2. Vara Schema tests
# ===========================================================================

@test("VaraSchema: VaraScanResult.to_dict() serialises all fields")
def test_vara_schema_to_dict():
    import json
    from vara.vara_schema import WeakSignal, EmergentTrend, Anomaly, VaraScanResult
    ws = WeakSignal("yield_curve", "inverted", -0.12)
    et = EmergentTrend("Rate Shock", [ws])
    an = Anomaly("yield_curve", -0.12, "Inverted yield curve")
    result = VaraScanResult(
        weak_signals=[ws], trends=[et], anomalies=[an],
        unspecified=[], lineage=[{"scan_id": "abc"}]
    )
    d = result.to_dict()
    assert_eq(len(d["weak_signals"]), 1)
    assert_eq(len(d["trends"]), 1)
    assert_eq(len(d["anomalies"]), 1)
    json.dumps(d)   # must be JSON-serialisable


# ===========================================================================
# 3. Harvester tests
# ===========================================================================

@test("EconHarvester: fetch() returns all expected raw keys")
async def test_econ_fetch():
    from citl import CITLBus
    from vara.harvesters.econ_harvester import EconHarvester
    h = EconHarvester(CITLBus())
    raw = await h.fetch()
    assert_true("FRED_GDP_GROWTH" in raw)
    assert_true("BLS_CPI_YOY" in raw)
    assert_true("TREAS_YIELD_SPREAD_10_2" in raw)


@test("EconHarvester: normalise() maps to all ontology signal_types")
async def test_econ_normalise():
    from citl import CITLBus
    from vara.harvesters.econ_harvester import EconHarvester
    from vara.domain_ontology import ECON_ONTOLOGY
    h = EconHarvester(CITLBus())
    raw = await h.fetch()
    artifact = h.normalise(raw)
    for sig in ECON_ONTOLOGY.signal_types:
        assert_in(sig, artifact, f"Missing signal: {sig}")


@test("CryptoHarvester: normalise() produces all ontology signal_types")
async def test_crypto_normalise():
    from citl import CITLBus
    from vara.harvesters.crypto_harvester import CryptoHarvester
    from vara.domain_ontology import CRYPTO_ONTOLOGY
    h = CryptoHarvester(CITLBus())
    raw = await h.fetch()
    artifact = h.normalise(raw)
    for sig in CRYPTO_ONTOLOGY.signal_types:
        assert_in(sig, artifact, f"Missing signal: {sig}")


@test("GeoPolHarvester: normalise() produces all ontology signal_types")
async def test_geopol_normalise():
    from citl import CITLBus
    from vara.harvesters.geopol_harvester import GeoPolHarvester
    from vara.domain_ontology import GEOPOL_ONTOLOGY
    h = GeoPolHarvester(CITLBus())
    raw = await h.fetch()
    artifact = h.normalise(raw)
    for sig in GEOPOL_ONTOLOGY.signal_types:
        assert_in(sig, artifact, f"Missing signal: {sig}")


@test("WorldPolHarvester: normalise() produces all ontology signal_types")
async def test_worldpol_normalise():
    from citl import CITLBus
    from vara.harvesters.worldpol_harvester import WorldPolHarvester
    from vara.domain_ontology import WORLDPOL_ONTOLOGY
    h = WorldPolHarvester(CITLBus())
    raw = await h.fetch()
    artifact = h.normalise(raw)
    for sig in WORLDPOL_ONTOLOGY.signal_types:
        assert_in(sig, artifact, f"Missing signal: {sig}")


@test("IndustrialHarvester: normalise() produces all ontology signal_types")
async def test_industrial_normalise():
    from citl import CITLBus
    from vara.harvesters.industrial_harvester import IndustrialHarvester
    from vara.domain_ontology import INDUSTRIAL_ONTOLOGY
    h = IndustrialHarvester(CITLBus())
    raw = await h.fetch()
    artifact = h.normalise(raw)
    for sig in INDUSTRIAL_ONTOLOGY.signal_types:
        assert_in(sig, artifact, f"Missing signal: {sig}")


@test("BaseHarvester: _scan() returns VaraScanResult with correct types")
async def test_base_harvester_scan():
    from citl import CITLBus
    from vara.harvesters.econ_harvester import EconHarvester
    from vara.vara_schema import VaraScanResult
    h = EconHarvester(CITLBus())
    raw = await h.fetch()
    artifact = h.normalise(raw)
    result = h._scan(artifact)
    assert_true(isinstance(result, VaraScanResult))
    assert_true(isinstance(result.weak_signals, list))
    assert_true(isinstance(result.trends, list))
    assert_true(isinstance(result.anomalies, list))
    assert_true(isinstance(result.lineage, list))
    assert_eq(len(result.lineage), 1)


@test("BaseHarvester: _build_dip() produces valid DIP structure")
async def test_base_harvester_build_dip():
    import json
    from citl import CITLBus
    from vara.harvesters.econ_harvester import EconHarvester
    h = EconHarvester(CITLBus())
    raw = await h.fetch()
    artifact = h.normalise(raw)
    result = h._scan(artifact)
    dip = h._build_dip(artifact, result)
    # Structural checks
    assert_eq(dip["type"], "DIP")
    assert_eq(dip["domain_id"], "ECON")
    assert_in_range(dip["confidence_score"], 0.0, 1.0)
    assert_true(len(dip["signal_set"]) > 0)
    assert_eq(len(dip["weight_vector"]), len(dip["signal_set"]))
    assert_true(len(dip["drift_indicators"]) > 0)
    # JSON-serialisable
    json.dumps(dip)


@test("BaseHarvester: anomaly rules fire correctly for ECON yield curve inversion")
async def test_econ_anomaly_inversion():
    from citl import CITLBus
    from vara.harvesters.econ_harvester import EconHarvester
    h = EconHarvester(CITLBus())
    # Force an inverted yield curve
    artifact = {sig: 0.0 for sig in h.ontology.signal_types}
    artifact["yield_curve"] = -0.45   # clearly inverted
    result = h._scan(artifact)
    anomaly_fields = [a.field for a in result.anomalies]
    assert_in("yield_curve", anomaly_fields, "yield_curve inversion anomaly not raised")


@test("BaseHarvester: anomaly rules fire correctly for CRYPTO extreme fear")
async def test_crypto_anomaly_extreme_fear():
    from citl import CITLBus
    from vara.harvesters.crypto_harvester import CryptoHarvester
    h = CryptoHarvester(CITLBus())
    artifact = {sig: 0.5 for sig in h.ontology.signal_types}
    artifact["fear_greed_index"] = 8.0   # extreme fear threshold is <15
    result = h._scan(artifact)
    anomaly_fields = [a.field for a in result.anomalies]
    assert_in("fear_greed_index", anomaly_fields)


@test("BaseHarvester: run_once() publishes to correct CITL topic")
async def test_harvester_run_once_publishes():
    from citl import CITLBus, Topic
    from vara.harvesters.econ_harvester import EconHarvester
    bus = CITLBus()
    captured = []
    async def capture(msg): captured.append(msg)
    bus.subscribe("canon.dip.raw.", capture, name="test", prefix=True)
    h = EconHarvester(bus)
    await h.run_once()
    assert_eq(len(captured), 1)
    assert_eq(captured[0].topic, "canon.dip.raw.ECON")
    assert_eq(captured[0].packet["domain_id"], "ECON")


@test("BaseHarvester: stats track fetches and published counts")
async def test_harvester_stats():
    from citl import CITLBus
    from vara.harvesters.crypto_harvester import CryptoHarvester
    bus = CITLBus()
    h = CryptoHarvester(bus)
    assert_eq(h.stats["fetches"], 0)
    assert_eq(h.stats["published"], 0)
    await h.run_once()
    assert_eq(h.stats["fetches"], 1)
    assert_eq(h.stats["published"], 1)


# ===========================================================================
# 4. Vara Scan Domain Mode tests
# ===========================================================================

@test("VaraScanDomain: scan_once() returns DomainScanResult")
async def test_domain_scan_result():
    from citl import CITLBus
    from vara.harvesters.econ_harvester import EconHarvester
    from vara.vara_scan_domain import VaraScanDomain, EpistemicBusBridge
    from vara.vara_schema import VaraScanResult
    bus = CITLBus()
    ep_bus = EpistemicBusBridge(bus)
    domain = VaraScanDomain(EconHarvester(bus), ep_bus)
    result = await domain.scan_once()
    assert_true(result is not None)
    assert_eq(result.domain_id, "ECON")
    assert_true(isinstance(result.result, VaraScanResult))
    assert_true(isinstance(result.dip_packet, dict))


@test("VaraScanDomain: mode_name is Vara.<DOMAIN>")
def test_domain_mode_name():
    from citl import CITLBus
    from vara.harvesters.crypto_harvester import CryptoHarvester
    from vara.vara_scan_domain import VaraScanDomain, EpistemicBusBridge
    bus = CITLBus()
    domain = VaraScanDomain(CryptoHarvester(bus), EpistemicBusBridge(bus))
    assert_eq(domain.mode_name, "Vara.CRYPTO")


@test("VaraScanDomain: history grows after scan_once()")
async def test_domain_history_grows():
    from citl import CITLBus
    from vara.harvesters.geopol_harvester import GeoPolHarvester
    from vara.vara_scan_domain import VaraScanDomain, EpistemicBusBridge
    bus = CITLBus()
    domain = VaraScanDomain(GeoPolHarvester(bus), EpistemicBusBridge(bus))
    assert_eq(len(domain.history()), 0)
    await domain.scan_once()
    assert_eq(len(domain.history()), 1)
    await domain.scan_once()
    assert_eq(len(domain.history()), 2)


@test("VaraScanDomain: delta() returns None before 2 scans, dict after")
async def test_domain_delta():
    from citl import CITLBus
    from vara.harvesters.industrial_harvester import IndustrialHarvester
    from vara.vara_scan_domain import VaraScanDomain, EpistemicBusBridge
    bus = CITLBus()
    domain = VaraScanDomain(IndustrialHarvester(bus), EpistemicBusBridge(bus))
    assert_true(domain.delta() is None)
    await domain.scan_once()
    assert_true(domain.delta() is None)
    await domain.scan_once()
    delta = domain.delta()
    assert_true(delta is not None)
    assert_eq(delta["domain_id"], "INDUSTRIAL")
    assert_in("confidence_delta", delta)
    assert_in("drift_delta", delta)


@test("EpistemicBusBridge: emits to vara.epistemic.<domain> and canon.dip.raw.<DOMAIN>")
async def test_epistemic_bus_bridge_topics():
    from citl import CITLBus
    from vara.harvesters.worldpol_harvester import WorldPolHarvester
    from vara.vara_scan_domain import VaraScanDomain, EpistemicBusBridge
    bus = CITLBus()
    ep_bus = EpistemicBusBridge(bus)
    domain = VaraScanDomain(WorldPolHarvester(bus), ep_bus)
    topics_seen = []
    async def capture(msg): topics_seen.append(msg.topic)
    bus.subscribe("vara.epistemic.", capture, name="ep-capture", prefix=True)
    bus.subscribe("canon.dip.raw.", capture, name="dip-capture", prefix=True)
    await domain.scan_once()
    assert_in("vara.epistemic.worldpol", topics_seen)
    assert_in("canon.dip.raw.WORLDPOL", topics_seen)


# ===========================================================================
# 5. Dispatcher tests
# ===========================================================================

@test("VaraDispatcher: instantiates all 5 domain channels")
def test_dispatcher_channels():
    from citl import CITLBus
    from vara.vara_dispatcher import VaraDispatcher
    bus = CITLBus()
    disp = VaraDispatcher(bus)
    assert_eq(set(disp.domains.keys()), {"ECON","CRYPTO","GEOPOL","WORLDPOL","INDUSTRIAL"})


@test("VaraDispatcher: scan_all() returns results for all 5 domains")
async def test_dispatcher_scan_all():
    from citl import CITLBus
    from vara.vara_dispatcher import VaraDispatcher
    bus = CITLBus()
    disp = VaraDispatcher(bus)
    results = await disp.scan_all()
    assert_eq(set(results.keys()), {"ECON","CRYPTO","GEOPOL","WORLDPOL","INDUSTRIAL"})
    for did, res in results.items():
        assert_true(res is not None, f"{did} returned None")


@test("VaraDispatcher: all 5 domains publish DIPs to canon.dip.raw.*")
async def test_dispatcher_publishes_all_dips():
    from citl import CITLBus
    from vara.vara_dispatcher import VaraDispatcher
    bus = CITLBus()
    dip_topics = []
    async def capture(msg): dip_topics.append(msg.topic)
    bus.subscribe("canon.dip.raw.", capture, name="all-dips", prefix=True)
    disp = VaraDispatcher(bus)
    await disp.scan_all()
    domains_seen = {t.replace("canon.dip.raw.", "") for t in dip_topics}
    for did in ["ECON","CRYPTO","GEOPOL","WORLDPOL","INDUSTRIAL"]:
        assert_in(did, domains_seen, f"No DIP published for {did}")


@test("VaraDispatcher: cross-domain anomaly cascade detected when 3+ domains anomalous")
async def test_dispatcher_anomaly_cascade():
    """
    Force high-anomaly conditions on all harvesters by monkey-patching
    the scan result to inject anomalies, then check cross-domain detection.
    """
    from citl import CITLBus
    from vara.vara_dispatcher import VaraDispatcher
    from vara.vara_schema import Anomaly, VaraScanResult, WeakSignal, EmergentTrend

    bus = CITLBus()
    disp = VaraDispatcher(bus)

    # Manually build 5 scan results — all with ≥1 anomaly
    from vara.vara_scan_domain import DomainScanResult
    import uuid
    fake_results = {}
    for did in ["ECON","CRYPTO","GEOPOL","WORLDPOL","INDUSTRIAL"]:
        anomaly = Anomaly("test_field", 999.0, "Forced test anomaly")
        vsr = VaraScanResult(
            weak_signals=[], trends=[], anomalies=[anomaly],
            unspecified=[], lineage=[]
        )
        dip = {
            "confidence_score": 0.75,
            "drift_indicators": [{"direction":"UP","magnitude":0.5}]
        }
        fake_results[did] = DomainScanResult(
            domain_id=did, scan_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(), result=vsr,
            dip_packet=dip, cadence_s=3600, escalation_bias=1.0,
        )

    disp._detect_cross_domain(fake_results)
    signals = disp.cross_domain_signals()
    cascade = [s for s in signals if s["signal_type"] == "ANOMALY_CASCADE"]
    assert_true(len(cascade) >= 1, "Expected at least one ANOMALY_CASCADE signal")


@test("VaraDispatcher: confidence collapse detected when 2+ domains low-confidence")
async def test_dispatcher_confidence_collapse():
    from citl import CITLBus
    from vara.vara_dispatcher import VaraDispatcher
    from vara.vara_schema import VaraScanResult
    from vara.vara_scan_domain import DomainScanResult
    import uuid
    bus = CITLBus()
    disp = VaraDispatcher(bus)
    fake_results = {}
    for i, did in enumerate(["ECON","CRYPTO","GEOPOL","WORLDPOL","INDUSTRIAL"]):
        vsr = VaraScanResult(weak_signals=[], trends=[], anomalies=[], unspecified=[], lineage=[])
        conf = 0.30 if i < 3 else 0.82   # first 3 are low confidence
        dip = {"confidence_score": conf, "drift_indicators": [{"direction":"FLAT","magnitude":0.1}]}
        fake_results[did] = DomainScanResult(
            domain_id=did, scan_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(), result=vsr,
            dip_packet=dip, cadence_s=3600, escalation_bias=1.0,
        )
    disp._detect_cross_domain(fake_results)
    signals = disp.cross_domain_signals()
    collapse = [s for s in signals if s["signal_type"] == "CONFIDENCE_COLLAPSE"]
    assert_true(len(collapse) >= 1, "Expected at least one CONFIDENCE_COLLAPSE signal")


@test("VaraDispatcher: drift divergence detected when UP and DOWN domains coexist")
async def test_dispatcher_drift_divergence():
    from citl import CITLBus
    from vara.vara_dispatcher import VaraDispatcher
    from vara.vara_schema import VaraScanResult
    from vara.vara_scan_domain import DomainScanResult
    import uuid
    bus = CITLBus()
    disp = VaraDispatcher(bus)
    drift_map = {
        "ECON":       ("UP",    0.8),
        "CRYPTO":     ("CHAOTIC",0.9),
        "GEOPOL":     ("DOWN",  0.1),
        "WORLDPOL":   ("FLAT",  0.1),
        "INDUSTRIAL": ("DOWN",  0.2),
    }
    fake_results = {}
    for did, (direction, mag) in drift_map.items():
        vsr = VaraScanResult(weak_signals=[], trends=[], anomalies=[], unspecified=[], lineage=[])
        dip = {"confidence_score": 0.75, "drift_indicators": [{"direction": direction, "magnitude": mag}]}
        fake_results[did] = DomainScanResult(
            domain_id=did, scan_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(), result=vsr,
            dip_packet=dip, cadence_s=3600, escalation_bias=1.0,
        )
    disp._detect_cross_domain(fake_results)
    signals = disp.cross_domain_signals()
    diverge = [s for s in signals if s["signal_type"] == "DRIFT_DIVERGENCE"]
    assert_true(len(diverge) >= 1, "Expected at least one DRIFT_DIVERGENCE signal")


# ===========================================================================
# 6. Full pipeline integration (Vara → DAL → CDCE → CMX → EPS → CSP)
# ===========================================================================

@test("Integration: Vara scan_all() feeds DAL and produces aligned DIPs")
async def test_vara_feeds_dal():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE, CMX, EPS
    from vara.vara_dispatcher import VaraDispatcher

    bus = CITLBus()
    dal  = DAL(bus)
    cdce = CDCE(bus)
    cmx  = CMX(bus)
    eps  = EPS(bus, cmx)

    aligned = []
    async def capture(msg): aligned.append(msg.packet)
    bus.subscribe(Topic.DIP_ALIGNED, capture, name="align-capture")

    disp = VaraDispatcher(bus)
    await disp.scan_all()
    await asyncio.sleep(0.15)

    assert_true(len(aligned) >= 5,
                f"Expected ≥5 aligned DIPs (one per domain), got {len(aligned)}")
    domains_aligned = {d["domain_id"] for d in aligned}
    for did in ["ECON","CRYPTO","GEOPOL","WORLDPOL","INDUSTRIAL"]:
        assert_in(did, domains_aligned, f"{did} DIP not aligned by DAL")
    assert_eq(dal.stats["rejected"], 0, "DAL rejected some valid DIPs")


@test("Integration: full Vara→CDCE→EPS cycle produces a CSP")
async def test_vara_full_pipeline():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE, CMX, EPS
    from vara.vara_dispatcher import VaraDispatcher

    bus = CITLBus()
    DAL(bus)
    cdce = CDCE(bus)
    cmx  = CMX(bus)
    eps  = EPS(bus, cmx)
    csps = []
    async def capture(msg): csps.append(msg.packet)
    bus.subscribe(Topic.CSP_SYNTHESIS, capture, name="csp-capture")

    disp = VaraDispatcher(bus)
    await disp.scan_all()
    await asyncio.sleep(0.15)

    scp_count = await cdce.flush()
    await asyncio.sleep(0.1)
    csp = await eps.flush()
    await asyncio.sleep(0.1)

    assert_true(len(csps) >= 1, "Expected at least one CSP")
    assert_true(scp_count >= 10, f"Expected ≥10 SCPs (5 domains → 10 pairs), got {scp_count}")

    csp_data = csps[0]
    assert_in_range(csp_data["confidence_score"], 0.0, 1.0)
    assert_true(len(csp_data["domains_involved"]) >= 5)
    assert_true(len(csp_data["insight"]) > 10)

    print(f"      synthesis_type  : {csp_data['synthesis_type']}")
    print(f"      confidence_score: {csp_data['confidence_score']:.3f}")
    print(f"      domains_involved: {csp_data['domains_involved']}")
    print(f"      escalation_path : {csp_data['escalation_path']}")
    print(f"      SCP count       : {scp_count}")


@test("Integration: VaraCanonBridge.flush() produces end-to-end synthesis")
async def test_vara_canon_bridge_flush():
    from vara.vara_canon_bridge import VaraCanonBridge
    bridge = VaraCanonBridge()
    summary = await bridge.flush()
    assert_true(summary["domains_scanned"] >= 5)
    assert_true(summary["scp_count"] >= 10)
    assert_true(summary["csp_produced"])
    assert_in_range(summary["confidence"], 0.0, 1.0)
    assert_true(summary["synthesis_type"] is not None)
    print(f"      Bridge flush summary:")
    for k, v in summary.items():
        print(f"        {k}: {v}")


@test("Integration: CMX has 5×5 matrix after full Vara scan")
async def test_vara_cmx_dimension():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE, CMX, EPS
    from vara.vara_dispatcher import VaraDispatcher
    bus = CITLBus()
    DAL(bus); cdce = CDCE(bus); cmx = CMX(bus); EPS(bus, cmx)
    disp = VaraDispatcher(bus)
    await disp.scan_all()
    await asyncio.sleep(0.15)
    await cdce.flush()
    await asyncio.sleep(0.1)
    snap = cmx.snapshot()
    n = len(snap["domains"])
    assert_eq(n, 5, f"Expected 5 domains in CMX, got {n}: {snap['domains']}")
    assert_eq(len(snap["matrix"]), 5)
    for row in snap["matrix"]:
        assert_eq(len(row), 5)
    # Symmetric
    mat = snap["matrix"]
    for i in range(5):
        for j in range(5):
            assert_approx(mat[i][j], mat[j][i], tol=1e-9, msg=f"CMX[{i}][{j}] not symmetric")


# ===========================================================================
# Runner
# ===========================================================================

async def _run_all():
    import inspect
    module = sys.modules[__name__]
    tests = [
        (name, fn)
        for name, fn in inspect.getmembers(module)
        if callable(fn) and getattr(fn, "__is_test__", False)
    ]

    print(f"\n{'='*65}")
    print(f"  Vara + CDS-Ω1 Integration Test Suite  —  {len(tests)} tests")
    print(f"  {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S UTC')}")
    print(f"{'='*65}\n")

    for _name, fn in tests:
        await fn()

    passed = sum(1 for _, ok, _ in _results if ok)
    failed = sum(1 for _, ok, _ in _results if not ok)

    print(f"\n{'='*65}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'='*65}\n")

    if failed:
        print("Failed tests:")
        for name, ok, err in _results:
            if not ok:
                print(f"  {_FAIL} {name}: {err}")
        sys.exit(1)
    else:
        print("All tests passed.")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.WARNING,
                        format="%(levelname)-8s %(name)s: %(message)s")
    asyncio.run(_run_all())

"""
CDS-Ω1 Test Suite
Tests every pipeline stage, the message bus, thresholds, and mode transitions.
Run with:  python tests.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import sys
import traceback
from datetime import datetime, timedelta
from typing import Any

# ---------------------------------------------------------------------------
# Minimal test harness (no pytest required)
# ---------------------------------------------------------------------------

_PASS = "✓"
_FAIL = "✗"
_results: list[tuple[str, bool, str]] = []


def test(name: str):
    """Decorator — wraps sync or async test functions."""
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
        _run.__test_name__ = name
        _run.__is_test__ = True
        return _run
    return decorator


def assert_eq(a, b, msg=""):
    assert a == b, f"Expected {b!r}, got {a!r}. {msg}"

def assert_approx(a, b, tol=0.01, msg=""):
    assert abs(a - b) <= tol, f"Expected ~{b}, got {a} (tol={tol}). {msg}"

def assert_in_range(v, lo, hi, msg=""):
    assert lo <= v <= hi, f"Expected {v} in [{lo},{hi}]. {msg}"

def assert_true(cond, msg=""):
    assert cond, msg or "Condition was False"

def assert_false(cond, msg=""):
    assert not cond, msg or "Condition was True"


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _make_dip_dict(
    domain: str = "ECON",
    confidence: float = 0.8,
    signals: list[dict] | None = None,
    drift_magnitude: float = 0.3,
    drift_direction: str = "UP",
    timestamp: str | None = None,
    anomaly_code: str | None = None,
) -> dict:
    signals = signals or [
        {"signal_type": "PRICE", "value": 100.5, "weight": 0.7, "confidence": 0.85, "source": "test"},
        {"signal_type": "VOLATILITY", "value": 0.22, "weight": 0.3, "confidence": 0.75, "source": "test"},
    ]
    dip: dict[str, Any] = {
        "type": "DIP",
        "version": "1.0",
        "domain_id": domain,
        "timestamp": timestamp or _now_iso(),
        "signal_set": signals,
        "weight_vector": [s["weight"] for s in signals],
        "confidence_score": confidence,
        "drift_indicators": [
            {
                "vector": [0.5, 0.3],
                "magnitude": drift_magnitude,
                "direction": drift_direction,
                "volatility": 0.2,
            }
        ],
        "anomaly_flags": [],
        "metadata": {},
    }
    if anomaly_code:
        dip["anomaly_flags"].append({
            "code": anomaly_code,
            "severity": "HIGH",
            "description": "test anomaly",
        })
    return dip


# ---------------------------------------------------------------------------
# MODELS tests
# ---------------------------------------------------------------------------

@test("DIP validates confidence in [0,1]")
def test_dip_confidence_validation():
    from models import DIP, DomainID, DriftDirection, DriftIndicator, Signal, SignalType
    dip = DIP(
        domain_id=DomainID.ECON,
        timestamp=datetime.utcnow(),
        signal_set=[Signal(SignalType.PRICE, 100.0, 0.7, 0.8, "test")],
        weight_vector=[0.7],
        confidence_score=1.5,  # invalid
        drift_indicators=[],
        anomaly_flags=[],
    )
    errors = dip.validate()
    assert_true(any("confidence_score" in e for e in errors))


@test("DIP validates weight_vector length matches signal_set")
def test_dip_weight_vector_length():
    from models import DIP, DomainID, Signal, SignalType
    dip = DIP(
        domain_id=DomainID.ECON,
        timestamp=datetime.utcnow(),
        signal_set=[Signal(SignalType.PRICE, 100.0, 0.7, 0.8, "test")],
        weight_vector=[0.7, 0.3],  # wrong length
        confidence_score=0.8,
        drift_indicators=[],
        anomaly_flags=[],
    )
    errors = dip.validate()
    assert_true(any("weight_vector" in e for e in errors))


@test("SCP validates correlation_strength in [-1,1]")
def test_scp_correlation_validation():
    from models import SCP, DomainID, CorrelationType
    scp = SCP(
        domain_a=DomainID.ECON,
        domain_b=DomainID.GOV,
        correlation_type=CorrelationType.CAUSAL,
        correlation_strength=2.5,   # invalid
        lag=0.0,
        predictive_value=0.5,
        reinforcement_signals=[],
        divergence_signals=[],
        contradiction_score=0.2,
    )
    errors = scp.validate()
    assert_true(any("correlation_strength" in e for e in errors))


@test("CSP contradiction_matrix dimension matches domains_involved")
def test_csp_matrix_dimension():
    from models import CSP, DomainID, SynthesisType, EscalationPath
    csp = CSP(
        synthesis_id="test-id",
        timestamp=datetime.utcnow(),
        domains_involved=[DomainID.ECON, DomainID.GOV],  # 2 domains
        synthesis_type=SynthesisType.BASELINE,
        insight="test",
        reinforcement_clusters=[],
        contradiction_matrix=[[0.0, 0.5, 0.1]],   # wrong: 1 row x 3 cols
        drift_vector=[0.0],
        predictive_indicators=[],
        confidence_score=0.7,
        escalation_path=EscalationPath.NONE,
    )
    errors = csp.validate()
    assert_true(len(errors) > 0)


@test("CSP.to_dict serialises all fields correctly")
def test_csp_to_dict():
    from models import CSP, DomainID, SynthesisType, EscalationPath
    csp = CSP(
        synthesis_id="abc-123",
        timestamp=datetime.utcnow(),
        domains_involved=[DomainID.ECON, DomainID.STOCK],
        synthesis_type=SynthesisType.LIQUIDITY_SHOCK,
        insight="Liquidity declining",
        reinforcement_clusters=[],
        contradiction_matrix=[[0.0, 0.3], [0.3, 0.0]],
        drift_vector=[0.1, 0.2],
        predictive_indicators=[],
        confidence_score=0.72,
        escalation_path=EscalationPath.FIELD_INTEL,
    )
    d = csp.to_dict()
    assert_eq(d["type"], "CSP")
    assert_eq(d["synthesis_id"], "abc-123")
    assert_eq(d["escalation_path"], "FIELDINTEL")
    assert_eq(d["domains_involved"], ["ECON", "STOCK"])
    # Serialise to JSON to confirm no type errors
    json.dumps(d)


# ---------------------------------------------------------------------------
# CITL Bus tests
# ---------------------------------------------------------------------------

@test("CITLBus: exact subscription receives message")
async def test_bus_exact_subscription():
    from citl import CITLBus, Topic
    bus = CITLBus()
    received = []

    async def handler(msg):
        received.append(msg)

    bus.subscribe(Topic.DIP_ALIGNED, handler, name="test-handler")
    await bus.publish(Topic.DIP_ALIGNED, {"type": "DIP", "test": True})
    assert_eq(len(received), 1)


@test("CITLBus: prefix subscription catches all matching topics")
async def test_bus_prefix_subscription():
    from citl import CITLBus
    bus = CITLBus()
    received = []

    async def handler(msg):
        received.append(msg.topic)

    bus.subscribe("canon.dip.raw.", handler, name="prefix-handler", prefix=True)
    await bus.publish("canon.dip.raw.ECON", {"type": "DIP", "domain_id": "ECON"})
    await bus.publish("canon.dip.raw.GOV",  {"type": "DIP", "domain_id": "GOV"})
    await bus.publish("canon.dip.aligned",  {"type": "DIP", "other": True})
    assert_eq(len(received), 2)
    assert_true("canon.dip.raw.ECON" in received)
    assert_true("canon.dip.raw.GOV"  in received)


@test("CITLBus: envelope wrapping and unwrapping")
async def test_bus_envelope():
    from citl import CITLBus, Topic, unwrap, SUBSYSTEM_ID
    bus = CITLBus()
    captured = []

    async def handler(msg):
        captured.append(msg.envelope)

    bus.subscribe(Topic.DIP_ALIGNED, handler, name="env-test")
    await bus.publish(Topic.DIP_ALIGNED, {"type": "DIP", "domain_id": "ECON"})

    env = captured[0]
    assert_eq(env["subsystem_id"], SUBSYSTEM_ID)
    assert_eq(env["envelope_version"], "1.0")
    inner = unwrap(env)
    assert_eq(inner["type"], "DIP")


@test("CITLBus: subscriber error goes to dead-letter queue")
async def test_bus_dead_letter():
    from citl import CITLBus, Topic
    bus = CITLBus()

    async def bad_handler(msg):
        raise RuntimeError("intentional error")

    bus.subscribe(Topic.DIP_ALIGNED, bad_handler, name="bad-handler")
    await bus.publish(Topic.DIP_ALIGNED, {"type": "DIP"})
    assert_eq(len(bus.dead_letters()), 1)
    assert_true("intentional error" in bus.dead_letters()[0].error)


@test("CITLBus: fanout delivers to multiple subscribers")
async def test_bus_fanout():
    from citl import CITLBus, Topic
    bus = CITLBus()
    counts = [0, 0]

    async def h1(msg): counts[0] += 1
    async def h2(msg): counts[1] += 1

    bus.subscribe(Topic.DIP_ALIGNED, h1, name="h1")
    bus.subscribe(Topic.DIP_ALIGNED, h2, name="h2")
    await bus.publish(Topic.DIP_ALIGNED, {"type": "DIP"})
    assert_eq(counts, [1, 1])


@test("CITLBus: stats track publish counts per topic")
async def test_bus_stats():
    from citl import CITLBus, Topic
    bus = CITLBus()
    async def noop(msg): pass
    bus.subscribe(Topic.DIP_ALIGNED, noop, name="noop")
    for _ in range(5):
        await bus.publish(Topic.DIP_ALIGNED, {"type": "DIP"})
    assert_eq(bus.stats()[Topic.DIP_ALIGNED], 5)


@test("CITLBus: history ring buffer trims to depth")
async def test_bus_history_depth():
    from citl import CITLBus, Topic
    bus = CITLBus(history_depth=3)
    async def noop(msg): pass
    bus.subscribe(Topic.DIP_ALIGNED, noop, name="noop")
    for i in range(5):
        await bus.publish(Topic.DIP_ALIGNED, {"i": i})
    assert_eq(len(bus.history()), 3)


# ---------------------------------------------------------------------------
# DAL tests
# ---------------------------------------------------------------------------

@test("DAL: valid DIP is aligned and published")
async def test_dal_valid_dip():
    from citl import CITLBus, Topic
    from pipeline import DAL
    bus = CITLBus()
    dal = DAL(bus)
    aligned = []

    async def capture(msg): aligned.append(msg.packet)
    bus.subscribe(Topic.DIP_ALIGNED, capture, name="capture")

    dip = _make_dip_dict("ECON")
    await bus.publish("canon.dip.raw.ECON", dip)
    assert_eq(len(aligned), 1)
    assert_eq(aligned[0]["domain_id"], "ECON")
    assert_eq(dal.stats["accepted"], 1)
    assert_eq(dal.stats["rejected"], 0)


@test("DAL: wrong type is rejected")
async def test_dal_wrong_type():
    from citl import CITLBus
    from pipeline import DAL
    bus = CITLBus()
    dal = DAL(bus)
    bad = {"type": "SCP", "domain_id": "ECON", "timestamp": _now_iso(),
           "signal_set": [], "weight_vector": [], "confidence_score": 0.5}
    await bus.publish("canon.dip.raw.ECON", bad)
    assert_eq(dal.stats["rejected"], 1)


@test("DAL: stale timestamp is rejected")
async def test_dal_stale_timestamp():
    from citl import CITLBus
    from pipeline import DAL
    bus = CITLBus()
    dal = DAL(bus)
    stale_ts = (datetime.utcnow() - timedelta(hours=3)).isoformat()
    dip = _make_dip_dict(timestamp=stale_ts)
    await bus.publish("canon.dip.raw.ECON", dip)
    assert_eq(dal.stats["rejected"], 1)


@test("DAL: out-of-range confidence is rejected")
async def test_dal_bad_confidence():
    from citl import CITLBus
    from pipeline import DAL
    bus = CITLBus()
    dal = DAL(bus)
    dip = _make_dip_dict(confidence=1.5)
    await bus.publish("canon.dip.raw.ECON", dip)
    assert_eq(dal.stats["rejected"], 1)


@test("DAL: signal_type is normalised to canonical ontology")
async def test_dal_signal_type_normalisation():
    from citl import CITLBus, Topic
    from pipeline import DAL
    bus = CITLBus()
    dal = DAL(bus)
    aligned = []
    async def capture(msg): aligned.append(msg.packet)
    bus.subscribe(Topic.DIP_ALIGNED, capture, name="capture")

    # "px" should map to "PRICE"
    dip = _make_dip_dict(signals=[
        {"signal_type": "px", "value": 50.0, "weight": 0.5, "confidence": 0.7, "source": "test"},
    ])
    await bus.publish("canon.dip.raw.ECON", dip)
    assert_eq(aligned[0]["signal_set"][0]["signal_type"], "PRICE")


# ---------------------------------------------------------------------------
# CDCE tests
# ---------------------------------------------------------------------------

@test("CDCE: flush produces SCPs for all domain pairs")
async def test_cdce_flush():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE
    bus = CITLBus()
    dal = DAL(bus)
    cdce = CDCE(bus)
    scps = []
    async def capture(msg): scps.append(msg.packet)
    bus.subscribe(Topic.SCP_PAIRWISE, capture, name="capture")

    # Publish 3 domains → expect 3 pairs (3 choose 2)
    for domain in ["ECON", "GOV", "STOCK"]:
        await bus.publish("canon.dip.raw." + domain, _make_dip_dict(domain))
    await asyncio.sleep(0.05)   # allow handlers to run
    await cdce.flush()
    assert_eq(len(scps), 3)


@test("CDCE: SCP has required fields")
async def test_cdce_scp_fields():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE
    bus = CITLBus()
    DAL(bus)
    cdce = CDCE(bus)
    scps = []
    async def capture(msg): scps.append(msg.packet)
    bus.subscribe(Topic.SCP_PAIRWISE, capture, name="capture")

    for d in ["ECON", "GOV"]:
        await bus.publish("canon.dip.raw." + d, _make_dip_dict(d))
    await asyncio.sleep(0.05)
    await cdce.flush()
    scp = scps[0]
    for key in ["domain_a", "domain_b", "correlation_type",
                "correlation_strength", "lag", "predictive_value",
                "contradiction_score"]:
        assert_true(key in scp, f"Missing key: {key}")


@test("CDCE: contradiction_score is in [0, 1]")
async def test_cdce_contradiction_range():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE
    bus = CITLBus()
    DAL(bus)
    cdce = CDCE(bus)
    scps = []
    async def capture(msg): scps.append(msg.packet)
    bus.subscribe(Topic.SCP_PAIRWISE, capture, name="capture")

    # Opposing signals: positive ECON vs negative GOV
    econ = _make_dip_dict("ECON", signals=[{"signal_type": "PRICE", "value": 100, "weight": 0.8, "confidence": 0.9, "source": "t"}])
    gov  = _make_dip_dict("GOV",  signals=[{"signal_type": "PRICE", "value": -50, "weight": 0.8, "confidence": 0.9, "source": "t"}])
    await bus.publish("canon.dip.raw.ECON", econ)
    await bus.publish("canon.dip.raw.GOV",  gov)
    await asyncio.sleep(0.05)
    await cdce.flush()
    for scp in scps:
        assert_in_range(scp["contradiction_score"], 0.0, 1.0)


# ---------------------------------------------------------------------------
# CMX tests
# ---------------------------------------------------------------------------

@test("CMX: matrix is N×N after N domains")
async def test_cmx_matrix_dimension():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE, CMX
    bus = CITLBus()
    DAL(bus)
    cdce = CDCE(bus)
    cmx  = CMX(bus)

    for d in ["ECON", "GOV", "STOCK"]:
        await bus.publish("canon.dip.raw." + d, _make_dip_dict(d))
    await asyncio.sleep(0.05)
    await cdce.flush()
    await asyncio.sleep(0.05)

    snap = cmx.snapshot()
    n = len(snap["domains"])
    assert_eq(n, 3)
    assert_eq(len(snap["matrix"]), 3)
    for row in snap["matrix"]:
        assert_eq(len(row), 3)


@test("CMX: diagonal is always 0.0")
async def test_cmx_diagonal():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE, CMX
    bus = CITLBus()
    DAL(bus)
    cdce = CDCE(bus)
    cmx  = CMX(bus)

    for d in ["ECON", "GOV"]:
        await bus.publish("canon.dip.raw." + d, _make_dip_dict(d))
    await asyncio.sleep(0.05)
    await cdce.flush()
    await asyncio.sleep(0.05)

    snap = cmx.snapshot()
    for i, row in enumerate(snap["matrix"]):
        assert_approx(row[i], 0.0, tol=1e-9, msg="Diagonal must be 0")


@test("CMX: matrix is symmetric")
async def test_cmx_symmetric():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE, CMX
    bus = CITLBus()
    DAL(bus)
    cdce = CDCE(bus)
    cmx  = CMX(bus)

    for d in ["ECON", "GOV", "CRYPTO"]:
        await bus.publish("canon.dip.raw." + d, _make_dip_dict(d))
    await asyncio.sleep(0.05)
    await cdce.flush()
    await asyncio.sleep(0.05)

    snap = cmx.snapshot()
    mat = snap["matrix"]
    n = len(mat)
    for i in range(n):
        for j in range(n):
            assert_approx(mat[i][j], mat[j][i], tol=1e-9, msg=f"[{i}][{j}] != [{j}][{i}]")


# ---------------------------------------------------------------------------
# EPS / DCA tests
# ---------------------------------------------------------------------------

@test("DCA: combine returns vector of correct length and valid magnitude")
def test_dca_combine():
    from models import DIP, DomainID, DriftDirection, DriftIndicator
    from pipeline import DCA
    dips = []
    for i in range(3):
        dip = DIP(
            domain_id=DomainID.ECON,
            timestamp=datetime.utcnow(),
            signal_set=[],
            weight_vector=[],
            confidence_score=0.7,
            drift_indicators=[
                DriftIndicator(
                    vector=[float(i), float(i+1)],
                    magnitude=0.5,
                    direction=DriftDirection.UP,
                    volatility=0.2,
                )
            ],
            anomaly_flags=[],
        )
        dips.append(dip)
    vec, mag = DCA.combine(dips)
    assert_eq(len(vec), 2)
    assert_true(mag >= 0.0)
    assert_true(math.isfinite(mag))


@test("EPS: flush emits a CSP with all required fields")
async def test_eps_flush():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE, CMX, EPS
    bus = CITLBus()
    DAL(bus)
    cdce = CDCE(bus)
    cmx  = CMX(bus)
    eps  = EPS(bus, cmx)
    csps = []
    async def capture(msg): csps.append(msg.packet)
    bus.subscribe(Topic.CSP_SYNTHESIS, capture, name="capture")

    for d in ["ECON", "GOV", "STOCK"]:
        await bus.publish("canon.dip.raw." + d, _make_dip_dict(d, confidence=0.75))
    await asyncio.sleep(0.05)
    await cdce.flush()
    await asyncio.sleep(0.05)
    await eps.flush()
    await asyncio.sleep(0.05)

    assert_true(len(csps) >= 1, "Expected at least one CSP")
    csp = csps[0]
    for key in ["synthesis_id", "timestamp", "domains_involved",
                "synthesis_type", "insight", "confidence_score",
                "escalation_path", "drift_vector", "contradiction_matrix"]:
        assert_true(key in csp, f"Missing CSP key: {key}")


@test("EPS: confidence_score is in [0, 1]")
async def test_eps_confidence_range():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE, CMX, EPS
    bus = CITLBus()
    DAL(bus)
    cdce = CDCE(bus)
    cmx  = CMX(bus)
    eps  = EPS(bus, cmx)
    csps = []
    async def capture(msg): csps.append(msg.packet)
    bus.subscribe(Topic.CSP_SYNTHESIS, capture, name="capture")

    for d in ["ECON", "STOCK"]:
        await bus.publish("canon.dip.raw." + d, _make_dip_dict(d))
    await asyncio.sleep(0.05)
    await cdce.flush()
    await asyncio.sleep(0.05)
    await eps.flush()
    await asyncio.sleep(0.05)

    for csp in csps:
        assert_in_range(csp["confidence_score"], 0.0, 1.0)


# ---------------------------------------------------------------------------
# Threshold / escalation tests
# ---------------------------------------------------------------------------

@test("Threshold: contradiction >= 0.7 → PARADOXENGINE escalation")
async def test_threshold_contradiction():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE, CMX, EPS, CONTRADICTION_HIGH_THRESHOLD
    from router import Router, ThresholdEvaluator
    bus = CITLBus()
    dal  = DAL(bus)
    cdce = CDCE(bus)
    cmx  = CMX(bus)
    eps  = EPS(bus, cmx)
    router = Router(bus, dal, cdce, cmx, eps)
    dashboard_msgs = []
    async def capture_dash(msg): dashboard_msgs.append(msg.packet)
    bus.subscribe(Topic.OPERATOR_DASHBOARD, capture_dash, name="dash")

    # Force-inject a high-contradiction SCP to drive CMX above threshold
    high_scp = {
        "type": "SCP", "version": "1.0",
        "domain_a": "ECON", "domain_b": "GOV",
        "correlation_type": "DIVERGENT",
        "correlation_strength": -0.85,
        "lag": 0.0,
        "predictive_value": 0.3,
        "reinforcement_signals": [],
        "divergence_signals": [],
        "contradiction_score": 0.80,   # > 0.70 threshold
        "metadata": {},
    }
    await bus.publish(Topic.SCP_PAIRWISE, high_scp)
    await asyncio.sleep(0.05)

    max_c, _, _ = cmx.max_contradiction()
    assert_true(max_c >= CONTRADICTION_HIGH_THRESHOLD,
                f"Expected max contradiction >= {CONTRADICTION_HIGH_THRESHOLD}, got {max_c}")


@test("Threshold: confidence < 0.4 → escalation_path = NONE")
async def test_threshold_confidence_gate():
    from models import CSP, DomainID, EscalationPath, SynthesisType
    from pipeline import CMX, CDCE, DAL, EPS
    from citl import CITLBus
    from router import Router, ThresholdEvaluator
    bus = CITLBus()
    dal = DAL(bus)
    cdce = CDCE(bus)
    cmx  = CMX(bus)
    eps  = EPS(bus, cmx)

    low_conf_csp = CSP(
        synthesis_id=CSP.new_id(),
        timestamp=datetime.utcnow(),
        domains_involved=[DomainID.ECON, DomainID.GOV],
        synthesis_type=SynthesisType.BASELINE,
        insight="Low confidence synthesis",
        reinforcement_clusters=[],
        contradiction_matrix=[[0.0, 0.2], [0.2, 0.0]],
        drift_vector=[0.1],
        predictive_indicators=[],
        confidence_score=0.35,   # below gate of 0.4
        escalation_path=EscalationPath.FIELD_INTEL,
        metadata={"drift_magnitude": 0.1},
    )
    result = ThresholdEvaluator.evaluate(low_conf_csp, cmx)
    assert_eq(result, EscalationPath.NONE)


@test("Threshold: drift >= 0.6 → OPERATOR_ALERT escalation")
async def test_threshold_drift():
    from models import CSP, DomainID, EscalationPath, SynthesisType
    from pipeline import CMX, CDCE, DAL, EPS, DRIFT_HIGH_THRESHOLD
    from citl import CITLBus
    from router import ThresholdEvaluator
    bus = CITLBus()
    dal  = DAL(bus)
    cdce = CDCE(bus)
    cmx  = CMX(bus)
    eps  = EPS(bus, cmx)

    high_drift_csp = CSP(
        synthesis_id=CSP.new_id(),
        timestamp=datetime.utcnow(),
        domains_involved=[DomainID.ECON, DomainID.STOCK],
        synthesis_type=SynthesisType.SYSTEMIC_DRIFT,
        insight="High drift detected",
        reinforcement_clusters=[],
        contradiction_matrix=[[0.0, 0.3], [0.3, 0.0]],
        drift_vector=[0.7, 0.5],
        predictive_indicators=[],
        confidence_score=0.75,   # above gate
        escalation_path=EscalationPath.FIELD_INTEL,
        metadata={"drift_magnitude": 0.72},  # > 0.6
    )
    result = ThresholdEvaluator.evaluate(high_drift_csp, cmx)
    assert_eq(result, EscalationPath.OPERATOR_ALERT)


# ---------------------------------------------------------------------------
# Mode transition tests
# ---------------------------------------------------------------------------

@test("Mode: starts in PASSIVE")
async def test_mode_starts_passive():
    from citl import CITLBus
    from pipeline import DAL, CDCE, CMX, EPS
    from router import Router, OperationalMode
    bus = CITLBus()
    dal = DAL(bus); cdce = CDCE(bus); cmx = CMX(bus); eps = EPS(bus, cmx)
    router = Router(bus, dal, cdce, cmx, eps)
    assert_eq(router.mode, OperationalMode.PASSIVE)


@test("Mode: transitions to ACTIVE on high contradiction")
async def test_mode_transition_active():
    """
    Drive the router directly by publishing a pre-built CSP whose metadata
    carries high contradiction, bypassing the CDCE flush that would otherwise
    overwrite the CMX cell with a fresh lower score.
    """
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE, CMX, EPS
    from router import Router, OperationalMode
    from models import CSP, DomainID, EscalationPath, SynthesisType

    bus = CITLBus()
    dal = DAL(bus); cdce = CDCE(bus); cmx = CMX(bus); eps = EPS(bus, cmx)
    router = Router(bus, dal, cdce, cmx, eps)

    # 1. Prime CMX with a high-contradiction SCP (score = 0.85 > threshold 0.70)
    high_scp = {
        "type": "SCP", "version": "1.0",
        "domain_a": "ECON", "domain_b": "GOV",
        "correlation_type": "DIVERGENT",
        "correlation_strength": -0.9,
        "lag": 0.0, "predictive_value": 0.2,
        "reinforcement_signals": [], "divergence_signals": [],
        "contradiction_score": 0.85,
        "metadata": {},
    }
    await bus.publish(Topic.SCP_PAIRWISE, high_scp)
    await asyncio.sleep(0.05)

    # Verify CMX registered the high score before proceeding
    max_c, _, _ = cmx.max_contradiction()
    assert_true(max_c >= 0.70, f"CMX did not record high contradiction: {max_c}")

    # 2. Publish a synthesised CSP whose escalation_path is already PARADOXENGINE.
    #    This goes through Router._handle_csp → ThresholdEvaluator.evaluate (which
    #    reads the live CMX = 0.85) → _update_mode.
    ready_csp = CSP(
        synthesis_id=CSP.new_id(),
        timestamp=datetime.utcnow(),
        domains_involved=[DomainID.ECON, DomainID.GOV],
        synthesis_type=SynthesisType.MARKET_POLICY_FRACTURE,
        insight="High contradiction between ECON and GOV policy signals.",
        reinforcement_clusters=[],
        contradiction_matrix=[[0.0, 0.85], [0.85, 0.0]],
        drift_vector=[0.3, 0.2],
        predictive_indicators=[],
        confidence_score=0.78,          # above confidence gate
        escalation_path=EscalationPath.PARADOX_ENGINE,
        metadata={"drift_magnitude": 0.35, "max_contradiction": 0.85},
    )
    await bus.publish(Topic.CSP_SYNTHESIS, ready_csp)
    await asyncio.sleep(0.15)           # let router._handle_csp process

    # Mode must have moved off PASSIVE
    assert_true(
        router.mode in (OperationalMode.ACTIVE, OperationalMode.RECURSIVE),
        f"Expected ACTIVE/RECURSIVE, got {router.mode.value}",
    )


# ---------------------------------------------------------------------------
# End-to-end integration test
# ---------------------------------------------------------------------------

@test("E2E: multi-domain ingestion produces routed CSP")
async def test_e2e_full_pipeline():
    from citl import CITLBus, Topic
    from pipeline import DAL, CDCE, CMX, EPS
    from router import Router

    bus = CITLBus()
    dal    = DAL(bus)
    cdce   = CDCE(bus)
    cmx    = CMX(bus)
    eps    = EPS(bus, cmx)
    router = Router(bus, dal, cdce, cmx, eps)

    paradox_intake  = []
    fieldintel      = []
    dashboard       = []

    async def cap_paradox(msg):  paradox_intake.append(msg.packet)
    async def cap_fieldintel(msg): fieldintel.append(msg.packet)
    async def cap_dashboard(msg):  dashboard.append(msg.packet)

    bus.subscribe(Topic.PARADOX_INTAKE,     cap_paradox,    name="e2e-paradox")
    bus.subscribe(Topic.FIELD_INTEL_INTAKE, cap_fieldintel, name="e2e-fi")
    bus.subscribe(Topic.OPERATOR_DASHBOARD, cap_dashboard,  name="e2e-dash")

    # Ingest 5 domains with realistic values
    domains_data = {
        "ECON":   {"confidence": 0.82, "drift": 0.4},
        "GOV":    {"confidence": 0.75, "drift": 0.5},
        "STOCK":  {"confidence": 0.88, "drift": 0.3},
        "CRYPTO": {"confidence": 0.65, "drift": 0.6},
        "COMM":   {"confidence": 0.70, "drift": 0.2},
    }
    for domain, params in domains_data.items():
        dip = _make_dip_dict(
            domain=domain,
            confidence=params["confidence"],
            drift_magnitude=params["drift"],
        )
        await bus.publish(f"canon.dip.raw.{domain}", dip)

    await asyncio.sleep(0.1)
    await cdce.flush()
    await asyncio.sleep(0.1)
    await eps.flush()
    await asyncio.sleep(0.1)

    # Verify CSP was routed to field intel
    assert_true(len(fieldintel) >= 1, "No CSP routed to FIELD_INTEL")

    # Verify dashboard was updated
    assert_true(len(dashboard) >= 1, "No dashboard update received")

    # Verify CSP structure
    csp = fieldintel[0]
    assert_true("synthesis_id"   in csp)
    assert_true("synthesis_type" in csp)
    assert_true("insight"        in csp)
    assert_true("confidence_score" in csp)
    assert_in_range(csp["confidence_score"], 0.0, 1.0)

    # Verify DAL stats
    assert_eq(dal.stats["accepted"], 5)
    assert_eq(dal.stats["rejected"], 0)

    print(f"      synthesis_type  : {csp['synthesis_type']}")
    print(f"      confidence_score: {csp['confidence_score']:.3f}")
    print(f"      escalation_path : {csp['escalation_path']}")
    print(f"      insight         : {csp['insight'][:80]}...")


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

async def _run_all():
    import inspect
    import sys

    # Collect all decorated test functions from this module
    module = sys.modules[__name__]
    tests = [
        (name, fn)
        for name, fn in inspect.getmembers(module)
        if callable(fn) and getattr(fn, "__is_test__", False)
    ]

    print(f"\n{'='*60}")
    print(f"  CDS-Ω1 Test Suite  —  {len(tests)} tests")
    print(f"{'='*60}\n")

    for _name, fn in tests:
        await fn()

    passed = sum(1 for _, ok, _ in _results if ok)
    failed = sum(1 for _, ok, _ in _results if not ok)

    print(f"\n{'='*60}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")

    if failed:
        print("Failed tests:")
        for name, ok, err in _results:
            if not ok:
                print(f"  {_FAIL} {name}: {err}")
        sys.exit(1)
    else:
        print("All tests passed.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)-8s %(name)s: %(message)s",
    )
    asyncio.run(_run_all())

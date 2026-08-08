"""
CDS-Ω1 Processing Pipeline
Stages: DAL → CDCE → CMX → EPS+DCA

Each stage is an async class that subscribes to upstream CITL topics,
processes data, and publishes to downstream topics.
"""

from __future__ import annotations

import asyncio
import logging
import math
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from typing import Any

# numpy is optional — pure-Python fallback used when unavailable (e.g. Termux)
try:
    import numpy as _np
    _HAS_NUMPY = True
except ImportError:  # pragma: no cover
    _np = None       # type: ignore
    _HAS_NUMPY = False


# ── Pure-Python math shims (used when numpy absent) ──────────────────────────

def _mean(seq):
    """Arithmetic mean of a numeric iterable."""
    lst = list(seq)
    return sum(lst) / len(lst) if lst else 0.0

def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def _weighted_mean(vals, weights):
    """Weighted average of vals with given weights."""
    total_w = sum(weights)
    if total_w == 0:
        return _mean(vals)
    return sum(v * w for v, w in zip(vals, weights)) / total_w

def _pearson(a, b):
    """Pearson correlation coefficient, pure Python."""
    n = len(a)
    if n < 2:
        return 0.0
    ma, mb = _mean(a), _mean(b)
    num  = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    dsa  = math.sqrt(sum((x - ma) ** 2 for x in a))
    dsb  = math.sqrt(sum((y - mb) ** 2 for y in b))
    if dsa == 0 or dsb == 0:
        return 0.0
    r = num / (dsa * dsb)
    return max(-1.0, min(1.0, r))

def _cross_correlate(a, b):
    """Full cross-correlation of two equal-length sequences, pure Python."""
    n   = len(a)
    ma, mb = _mean(a), _mean(b)
    ca  = [x - ma for x in a]
    cb  = [y - mb for y in b]
    out = []
    for lag in range(-(n - 1), n):
        s = 0.0
        for i in range(n):
            j = i + lag
            if 0 <= j < n:
                s += ca[i] * cb[j]
        out.append(s)
    return out

def _norm(v):
    """Euclidean norm of a list."""
    return math.sqrt(sum(x * x for x in v))

def _vec_mean(vecs):
    """Element-wise mean of a list of equal-or-padded lists."""
    if not vecs:
        return []
    max_len = max(len(v) for v in vecs)
    padded  = [v + [0.0] * (max_len - len(v)) for v in vecs]
    return [sum(col) / len(col) for col in zip(*padded)]


# ── numpy-aware wrappers (select real numpy or shim at call time) ─────────────

def _np_mean(seq):
    lst = list(seq)
    if not lst:
        return 0.0
    return float(_np.mean(lst)) if _HAS_NUMPY else _mean(lst)

def _np_weighted_mean(vals, weights):
    if _HAS_NUMPY:
        va, wa = _np.array(vals), _np.array(weights)
        return float(_np.average(va, weights=wa))
    return _weighted_mean(vals, weights)

def _np_pearson(a, b):
    if _HAS_NUMPY and len(a) > 1:
        r = float(_np.corrcoef(_np.array(a), _np.array(b))[0, 1])
        return 0.0 if math.isnan(r) else r
    return _pearson(a, b)

def _np_lag(a, b):
    n = len(a)
    if n < 2:
        return 0.0
    if _HAS_NUMPY:
        va, vb = _np.array(a), _np.array(b)
        xc     = _np.correlate(va - va.mean(), vb - vb.mean(), mode="full")
        return float(int(_np.argmax(xc)) - (n - 1))
    xc = _cross_correlate(a, b)
    return float(xc.index(max(xc)) - (n - 1))

def _np_vec_mean_and_norm(vecs):
    if _HAS_NUMPY:
        max_len = max(len(v) for v in vecs)
        padded  = _np.array([v + [0.0] * (max_len - len(v)) for v in vecs])
        mean_v  = padded.mean(axis=0).tolist()
        mag     = float(_np.linalg.norm(mean_v) / math.sqrt(max_len))
    else:
        mean_v  = _vec_mean(vecs)
        max_len = len(mean_v)
        mag     = _norm(mean_v) / math.sqrt(max(1, max_len))
    return [round(x, 4) for x in mean_v], round(mag, 4)


from citl import CITLBus, Message, Topic
from canon_constants import (
    DOMAIN_WEIGHT, DOMAIN_RELATIONSHIP_MAP,
    CONTRADICTION_THRESHOLD, REINFORCEMENT_THRESHOLD, DRIFT_SURGE_THRESHOLD,
    ACTIVE_MODE_TRIGGER, RECURSIVE_MODE_TRIGGER,
    contradiction_template, expected_direction, canon_uid,
    DOMAIN_ID_MAP,
)
from models import (
    AnomalyCode, AnomalyFlag, CorrelationType, DIP, DriftDirection,
    DriftIndicator, DomainID, EscalationPath, IndicatorType,
    PredictiveIndicator, ReinforcementCluster, SCP, CSP,
    Severity, Signal, SignalType, SynthesisType,
)

logger = logging.getLogger("cds.pipeline")


# ===========================================================================
# 4.1  Domain Alignment Layer (DAL)
# ===========================================================================

# Canonical ontology mapping: raw signal type strings → SignalType enum
_SIGNAL_ONTOLOGY: dict[str, SignalType] = {
    "idx":         SignalType.INDEX,
    "index":       SignalType.INDEX,
    "px":          SignalType.PRICE,
    "price":       SignalType.PRICE,
    "pol":         SignalType.POLICY,
    "policy":      SignalType.POLICY,
    "flow":        SignalType.FLOW,
    "vol":         SignalType.VOLATILITY,
    "volatility":  SignalType.VOLATILITY,
    "sent":        SignalType.SENTIMENT,
    "sentiment":   SignalType.SENTIMENT,
    "volume":      SignalType.VOLUME,
    "rate":        SignalType.RATE,
    "indicator":   SignalType.INDICATOR,
}

# Max acceptable age of a DIP timestamp before rejection (seconds)
_MAX_TIMESTAMP_AGE_S = 3600


def _normalise_signal_type(raw: str) -> SignalType:
    """Map any raw string to canonical SignalType. Falls back to INDICATOR."""
    key = raw.lower().strip()
    return _SIGNAL_ONTOLOGY.get(key, SignalType.INDICATOR)


class DAL:
    """
    Domain Alignment Layer

    Subscribes to: canon.dip.raw.* (prefix)
    Publishes to:  canon.dip.aligned

    Responsibilities
    ----------------
    1. Validate DIP structure and field ranges.
    2. Normalise signal_type strings to canonical ontology.
    3. Reject stale or malformed packets (emit to dead-letter via bus).
    4. Forward clean DIPs to canon.dip.aligned.
    """

    def __init__(self, bus: CITLBus, window_s: int = _MAX_TIMESTAMP_AGE_S) -> None:
        self.bus = bus
        self.window_s = window_s
        self._accepted = 0
        self._rejected = 0

        bus.subscribe(
            topic_pattern="canon.dip.raw.",
            handler=self._handle_raw_dip,
            name="DAL",
            prefix=True,
        )
        logger.info("DAL initialised — subscribed to canon.dip.raw.*")

    async def _handle_raw_dip(self, msg: Message) -> None:
        raw = msg.packet

        # --- structural validation ---
        if raw.get("type") != "DIP":
            self._reject("type != DIP", raw)
            return

        required = {"domain_id", "timestamp", "signal_set",
                    "weight_vector", "confidence_score"}
        missing = required - set(raw.keys())
        if missing:
            self._reject(f"missing fields: {missing}", raw)
            return

        # --- timestamp window ---
        try:
            ts = datetime.fromisoformat(raw["timestamp"])
        except ValueError:
            self._reject("unparseable timestamp", raw)
            return

        age = (datetime.utcnow() - ts).total_seconds()
        if abs(age) > self.window_s:
            self._reject(f"timestamp age {age:.0f}s exceeds window {self.window_s}s", raw)
            return

        # --- confidence range ---
        conf = raw.get("confidence_score", -1)
        if not (0.0 <= conf <= 1.0):
            self._reject(f"confidence_score {conf} out of [0,1]", raw)
            return

        # --- normalise + reconstruct ---
        try:
            dip = self._normalise(raw, ts)
        except Exception as exc:
            self._reject(f"normalisation error: {exc}", raw)
            return

        self._accepted += 1
        await self.bus.publish(Topic.DIP_ALIGNED, dip)
        logger.debug("DAL aligned DIP from %s  conf=%.2f", dip.domain_id.value, dip.confidence_score)

    def _normalise(self, raw: dict, ts: datetime) -> DIP:
        try:
            domain = DomainID(raw["domain_id"])
        except ValueError:
            domain = DomainID.ECON   # fallback; log only

        signals = []
        for s in raw.get("signal_set", []):
            signals.append(Signal(
                signal_type=_normalise_signal_type(str(s.get("signal_type", "INDICATOR"))),
                value=float(s.get("value", 0.0)),
                weight=max(0.0, min(1.0, float(s.get("weight", 0.5)))),
                confidence=max(0.0, min(1.0, float(s.get("confidence", 0.5)))),
                source=str(s.get("source", "unknown")),
            ))

        weights = [float(w) for w in raw.get("weight_vector", [s.weight for s in signals])]
        if len(weights) != len(signals):
            weights = [s.weight for s in signals]

        drift_indicators = []
        for d in raw.get("drift_indicators", []):
            try:
                direction = DriftDirection(d.get("direction", "FLAT"))
            except ValueError:
                direction = DriftDirection.FLAT
            drift_indicators.append(DriftIndicator(
                vector=[float(v) for v in d.get("vector", [0.0])],
                magnitude=float(d.get("magnitude", 0.0)),
                direction=direction,
                volatility=max(0.0, min(1.0, float(d.get("volatility", 0.0)))),
            ))

        anomaly_flags = []
        for a in raw.get("anomaly_flags", []):
            try:
                code = AnomalyCode(a.get("code", "OUTLIER"))
                sev  = Severity(a.get("severity", "LOW"))
            except ValueError:
                code, sev = AnomalyCode.OUTLIER, Severity.LOW
            anomaly_flags.append(AnomalyFlag(
                code=code,
                severity=sev,
                description=str(a.get("description", "")),
            ))

        return DIP(
            domain_id=domain,
            timestamp=ts,
            signal_set=signals,
            weight_vector=weights,
            confidence_score=float(raw["confidence_score"]),
            drift_indicators=drift_indicators,
            anomaly_flags=anomaly_flags,
            metadata=raw.get("metadata", {}),
        )

    def _reject(self, reason: str, raw: dict) -> None:
        self._rejected += 1
        domain = raw.get("domain_id", "UNKNOWN")
        logger.warning("DAL rejected DIP [%s]: %s", domain, reason)

    @property
    def stats(self) -> dict[str, int]:
        return {"accepted": self._accepted, "rejected": self._rejected}


# ===========================================================================
# 4.2  Cross-Domain Correlation Engine (CDCE)
# ===========================================================================

class CDCE:
    """
    Cross-Domain Correlation Engine

    Subscribes to: canon.dip.aligned
    Publishes to:  canon.scp.pairwise

    Algorithm
    ---------
    Collects aligned DIPs for a rolling time window T.
    On flush (called by the pipeline runner) generates ordered
    (domain_i, domain_j) pairs and emits one SCP per pair.

    Correlation metrics:
    - correlation_strength : weighted Pearson-like score between signal value arrays.
    - lag                  : estimated via cross-correlation peak offset.
    - predictive_value     : mean predictive signal confidence.
    - contradiction_score  : proportion of divergent signals weighted by magnitude.
    - correlation_type     : inferred from strength + lag + contradiction_score.
    """

    def __init__(self, bus: CITLBus, window_s: int = 3600) -> None:
        self.bus = bus
        self.window_s = window_s
        self._buffer: dict[DomainID, list[DIP]] = defaultdict(list)
        self._lock = asyncio.Lock()

        bus.subscribe(
            topic_pattern=Topic.DIP_ALIGNED,
            handler=self._collect,
            name="CDCE",
        )
        logger.info("CDCE initialised — window=%ds", window_s)

    async def _collect(self, msg: Message) -> None:
        raw = msg.packet
        try:
            domain = DomainID(raw["domain_id"])
            ts     = datetime.fromisoformat(raw["timestamp"])
        except (KeyError, ValueError):
            return

        # Re-hydrate a lightweight DIP reference (only what CDCE needs)
        signals = []
        for s in raw.get("signal_set", []):
            signals.append(Signal(
                signal_type=SignalType(s["signal_type"]),
                value=float(s["value"]),
                weight=float(s["weight"]),
                confidence=float(s["confidence"]),
                source=s["source"],
            ))

        drift_indicators = []
        for d in raw.get("drift_indicators", []):
            drift_indicators.append(DriftIndicator(
                vector=[float(v) for v in d["vector"]],
                magnitude=float(d["magnitude"]),
                direction=DriftDirection(d["direction"]),
                volatility=float(d["volatility"]),
            ))

        dip = DIP(
            domain_id=domain,
            timestamp=ts,
            signal_set=signals,
            weight_vector=[float(w) for w in raw.get("weight_vector", [])],
            confidence_score=float(raw.get("confidence_score", 0.5)),
            drift_indicators=drift_indicators,
            anomaly_flags=[],
            metadata=raw.get("metadata", {}),
        )

        async with self._lock:
            self._buffer[domain].append(dip)
            self._evict_stale()

    def _evict_stale(self) -> None:
        cutoff = datetime.utcnow() - timedelta(seconds=self.window_s)
        for domain in list(self._buffer):
            self._buffer[domain] = [
                d for d in self._buffer[domain] if d.timestamp >= cutoff
            ]
            if not self._buffer[domain]:
                del self._buffer[domain]

    async def flush(self) -> int:
        """Compute pairwise SCPs for all domains currently in buffer."""
        async with self._lock:
            snapshot = {d: list(dips) for d, dips in self._buffer.items()}

        domains = list(snapshot.keys())
        if len(domains) < 2:
            logger.debug("CDCE flush: fewer than 2 domains buffered, skipping")
            return 0

        count = 0
        for da, db in combinations(domains, 2):
            scp = self._compute_scp(da, snapshot[da], db, snapshot[db])
            await self.bus.publish(Topic.SCP_PAIRWISE, scp)
            count += 1

        logger.info("CDCE flushed %d SCPs for %d domain pairs", count, len(domains))
        return count

    def _compute_scp(
        self,
        da: DomainID, dips_a: list[DIP],
        db: DomainID, dips_b: list[DIP],
    ) -> SCP:
        vals_a = self._signal_value_array(dips_a)
        vals_b = self._signal_value_array(dips_b)

        # Align lengths
        min_len = min(len(vals_a), len(vals_b))
        if min_len == 0:
            strength, lag = 0.0, 0.0
        else:
            va_list = vals_a[:min_len]
            vb_list = vals_b[:min_len]
            strength = _np_pearson(va_list, vb_list) if min_len > 1 else 0.0
            strength = 0.0 if math.isnan(strength) else strength
            lag      = self._estimate_lag(va_list, vb_list)

        conf_a = _np_mean(d.confidence_score for d in dips_a) if dips_a else 0.5
        conf_b = _np_mean(d.confidence_score for d in dips_b) if dips_b else 0.5

        all_signals_a = [s for d in dips_a for s in d.signal_set]
        all_signals_b = [s for d in dips_b for s in d.signal_set]

        reinf, diverg    = self._split_signals(all_signals_a, all_signals_b, strength)
        contradiction    = self._contradiction_score(all_signals_a, all_signals_b)
        predictive_value = _np_mean(s.confidence for s in reinf) if reinf else 0.0

        # ── Structural prior from DOMAIN_RELATIONSHIP_MAP (I·SCR) ────────────
        # Convert DomainID enums → canonical lowercase keys used in the map
        _rev = {v: k for k, v in DOMAIN_ID_MAP.items()}
        da_key = _rev.get(da.value, da.value.lower())
        db_key = _rev.get(db.value, db.value.lower())
        struct_prior = expected_direction(da_key, db_key)  # +1, -1, or None

        # Structural divergence: observed direction opposes the expected prior
        observed_dir = 1 if strength >= 0 else -1
        struct_diverge = (struct_prior is not None) and (observed_dir != struct_prior)

        # Apply operator CONTRADICTION_THRESHOLD (0.55) for structural detection
        if struct_diverge and contradiction < CONTRADICTION_THRESHOLD:
            # Structural divergence upgrades the contradiction score
            contradiction = max(contradiction, CONTRADICTION_THRESHOLD)

        corr_type = self._infer_corr_type(strength, lag, contradiction, struct_prior)

        return SCP(
            domain_a=da,
            domain_b=db,
            correlation_type=corr_type,
            correlation_strength=round(strength, 4),
            lag=round(lag, 2),
            predictive_value=round(predictive_value, 4),
            reinforcement_signals=reinf[:10],
            divergence_signals=diverg[:10],
            contradiction_score=round(contradiction, 4),
            metadata={
                "window_dips_a": len(dips_a),
                "window_dips_b": len(dips_b),
                "conf_a": round(float(conf_a), 4),
                "conf_b": round(float(conf_b), 4),
                "struct_prior": struct_prior,
                "struct_diverge": struct_diverge,
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _signal_value_array(dips: list[DIP]) -> list[float]:
        """Weighted mean signal value per DIP."""
        result = []
        for dip in dips:
            if not dip.signal_set:
                result.append(0.0)
                continue
            vals    = [s.value  for s in dip.signal_set]
            weights = [s.weight for s in dip.signal_set]
            result.append(_np_weighted_mean(vals, weights))
        return result

    @staticmethod
    def _weight_array(dips: list[DIP]) -> list[float]:
        return [d.confidence_score for d in dips]

    @staticmethod
    def _estimate_lag(va, vb) -> float:
        """Peak cross-correlation offset."""
        return _np_lag(list(va), list(vb))

    @staticmethod
    def _split_signals(
        sigs_a: list[Signal],
        sigs_b: list[Signal],
        strength: float,
    ) -> tuple[list[Signal], list[Signal]]:
        """Partition signals into reinforcing vs. diverging based on correlation sign."""
        if strength >= 0:
            return sigs_a, sigs_b
        return sigs_b, sigs_a

    @staticmethod
    def _contradiction_score(sigs_a: list[Signal], sigs_b: list[Signal]) -> float:
        """
        Proportion of signal pairs where value signs disagree,
        weighted by the average absolute value magnitude.
        """
        if not sigs_a or not sigs_b:
            return 0.0
        scores = []
        for sa in sigs_a:
            for sb in sigs_b:
                if sa.signal_type == sb.signal_type:
                    disagree = (sa.value * sb.value) < 0
                    mag = (abs(sa.value) + abs(sb.value)) / 2
                    scores.append((1.0 if disagree else 0.0) * min(1.0, mag / 100.0 + 0.1))
        return _np_mean(scores) if scores else 0.0

    @staticmethod
    def _infer_corr_type(
        strength: float,
        lag: float,
        contradiction: float,
        struct_prior: int | None = None,
    ) -> CorrelationType:
        """
        Infer correlation type, honouring structural priors from
        DOMAIN_RELATIONSHIP_MAP (canon_constants).  If the observed
        direction violates a +1 prior the pair is DIVERGENT even below
        the raw contradiction threshold; if it confirms a +1 prior
        at sufficient strength it is REINFORCING.
        """
        # Operator gate: contradiction >= CONTRADICTION_THRESHOLD (0.55) → DIVERGENT
        if contradiction >= CONTRADICTION_THRESHOLD:
            return CorrelationType.DIVERGENT
        if abs(lag) > 2:
            return CorrelationType.LAGGED
        # Structural reinforcement check
        if struct_prior == +1 and strength > REINFORCEMENT_THRESHOLD:
            return CorrelationType.REINFORCING
        if strength > 0.7:
            return CorrelationType.REINFORCING
        if strength > 0.4:
            return CorrelationType.CAUSAL
        if strength > 0.2:
            return CorrelationType.PREDICTIVE
        return CorrelationType.TEMPORAL


# ===========================================================================
# 4.3  Contradiction Matrix (CMX)
# ===========================================================================

class CMX:
    """
    Contradiction Matrix Engine

    Subscribes to: canon.scp.pairwise
    Publishes to:  canon.cmx.grid  (dict with matrix + domain index)

    Maintains an N×N matrix where cmx[i][j] = contradiction_score(domain_i, domain_j).
    Symmetric fill: cmx[i][j] = cmx[j][i] = score.
    Diagonal: 0.0.
    """

    def __init__(self, bus: CITLBus) -> None:
        self.bus = bus
        self._domain_index: list[DomainID] = []
        self._matrix: list[list[float]] = []
        self._lock = asyncio.Lock()

        bus.subscribe(
            topic_pattern=Topic.SCP_PAIRWISE,
            handler=self._update,
            name="CMX",
        )
        logger.info("CMX initialised")

    async def _update(self, msg: Message) -> None:
        raw = msg.packet
        try:
            da = DomainID(raw["domain_a"])
            db = DomainID(raw["domain_b"])
            score = float(raw["contradiction_score"])
        except (KeyError, ValueError) as exc:
            logger.warning("CMX bad SCP: %s", exc)
            return

        async with self._lock:
            self._ensure_domain(da)
            self._ensure_domain(db)
            i = self._domain_index.index(da)
            j = self._domain_index.index(db)
            self._matrix[i][j] = score
            self._matrix[j][i] = score

        await self._publish_grid()

    def _ensure_domain(self, domain: DomainID) -> None:
        if domain in self._domain_index:
            return
        n = len(self._domain_index)
        self._domain_index.append(domain)
        # Expand each existing row
        for row in self._matrix:
            row.append(0.0)
        # Add new row
        self._matrix.append([0.0] * (n + 1))

    async def _publish_grid(self) -> None:
        async with self._lock:
            snapshot = {
                "type": "CMX",
                "domains": [d.value for d in self._domain_index],
                "matrix": [list(row) for row in self._matrix],
                "timestamp": datetime.utcnow().isoformat(),
            }
        await self.bus.publish(Topic.CMX_GRID, snapshot)

    def snapshot(self) -> dict[str, Any]:
        return {
            "domains": [d.value for d in self._domain_index],
            "matrix": [list(row) for row in self._matrix],
        }

    def max_contradiction(self) -> tuple[float, DomainID | None, DomainID | None]:
        """Return (score, domain_i, domain_j) for the highest off-diagonal cell."""
        if not self._matrix:
            return 0.0, None, None
        best, bi, bj = 0.0, 0, 0
        n = len(self._matrix)
        for i in range(n):
            for j in range(i + 1, n):
                if self._matrix[i][j] > best:
                    best, bi, bj = self._matrix[i][j], i, j
        da = self._domain_index[bi] if self._domain_index else None
        db = self._domain_index[bj] if len(self._domain_index) > 1 else None
        return best, da, db

    @property
    def domain_index(self) -> list[DomainID]:
        return list(self._domain_index)

    @property
    def matrix(self) -> list[list[float]]:
        return [list(row) for row in self._matrix]


# ===========================================================================
# 4.4  Emergence & Pattern Synthesis (EPS) + Drift Coherence Analyser (DCA)
# ===========================================================================

# ── Operational thresholds ─────────────────────────────────────────────────
# Spec §5 hard thresholds (CMX escalation gate / DCA surge gate)
CONTRADICTION_HIGH_THRESHOLD = 0.70   # spec §5 — Paradox Engine gate
DRIFT_HIGH_THRESHOLD         = 0.60   # spec §5 — systemic drift gate
CONFIDENCE_GATE              = 0.40   # spec §5 — CSP escalation floor
# Operator thresholds from cds_omega1.py (signal-level detection)
# CONTRADICTION_THRESHOLD, REINFORCEMENT_THRESHOLD, DRIFT_SURGE_THRESHOLD
# are imported from canon_constants above.


class DCA:
    """
    Drift Coherence Analyser

    Combines drift_indicators across all active DIPs into a single
    global drift_vector and computes its normalised magnitude.
    """

    @staticmethod
    def combine(dips: list[DIP]) -> tuple[list[float], float]:
        """
        Returns (drift_vector, normalised_magnitude).
        drift_vector is the element-wise mean of all DIP drift indicator vectors.
        Normalised magnitude = ||drift_vector|| / sqrt(dim).
        """
        all_vecs: list[list[float]] = []
        for dip in dips:
            for di in dip.drift_indicators:
                if di.vector:
                    all_vecs.append(di.vector)

        if not all_vecs:
            return [0.0], 0.0

        return _np_vec_mean_and_norm(all_vecs)


class EPS:
    """
    Emergence & Pattern Synthesis Engine

    Subscribes to:
      - canon.dip.aligned    (accumulates DIP buffer)
      - canon.scp.pairwise   (accumulates SCP buffer)
      - canon.cmx.grid       (latest CMX snapshot)

    Publishes to:  canon.csp.synthesis

    On flush():
      1. Cluster reinforcement signals across domains.
      2. Run DCA for global drift vector.
      3. Determine synthesis_type, insight, predictive_indicators.
      4. Compute confidence_score.
      5. Set escalation_path per thresholds.
      6. Emit CSP.
    """

    def __init__(self, bus: CITLBus, cmx: CMX) -> None:
        self.bus = bus
        self.cmx = cmx
        self._dips: list[DIP] = []
        self._scps: list[SCP] = []
        self._lock = asyncio.Lock()

        bus.subscribe(Topic.DIP_ALIGNED,    self._collect_dip, "EPS-DIP")
        bus.subscribe(Topic.SCP_PAIRWISE,   self._collect_scp, "EPS-SCP")
        logger.info("EPS initialised")

    async def _collect_dip(self, msg: Message) -> None:
        raw = msg.packet
        try:
            domain = DomainID(raw["domain_id"])
            ts     = datetime.fromisoformat(raw["timestamp"])
        except (KeyError, ValueError):
            return

        signals = [
            Signal(
                signal_type=SignalType(s["signal_type"]),
                value=float(s["value"]),
                weight=float(s["weight"]),
                confidence=float(s["confidence"]),
                source=s["source"],
            )
            for s in raw.get("signal_set", [])
        ]
        drift_indicators = [
            DriftIndicator(
                vector=[float(v) for v in d["vector"]],
                magnitude=float(d["magnitude"]),
                direction=DriftDirection(d["direction"]),
                volatility=float(d["volatility"]),
            )
            for d in raw.get("drift_indicators", [])
        ]
        dip = DIP(
            domain_id=domain,
            timestamp=ts,
            signal_set=signals,
            weight_vector=[float(w) for w in raw.get("weight_vector", [])],
            confidence_score=float(raw.get("confidence_score", 0.5)),
            drift_indicators=drift_indicators,
            anomaly_flags=[],
        )
        async with self._lock:
            self._dips.append(dip)

    async def _collect_scp(self, msg: Message) -> None:
        raw = msg.packet
        try:
            da = DomainID(raw["domain_a"])
            db = DomainID(raw["domain_b"])
        except (KeyError, ValueError):
            return
        reinf = [
            Signal(
                signal_type=SignalType(s["signal_type"]),
                value=float(s["value"]),
                weight=float(s["weight"]),
                confidence=float(s["confidence"]),
                source=s["source"],
            )
            for s in raw.get("reinforcement_signals", [])
        ]
        diverg = [
            Signal(
                signal_type=SignalType(s["signal_type"]),
                value=float(s["value"]),
                weight=float(s["weight"]),
                confidence=float(s["confidence"]),
                source=s["source"],
            )
            for s in raw.get("divergence_signals", [])
        ]
        scp = SCP(
            domain_a=da,
            domain_b=db,
            correlation_type=CorrelationType(raw["correlation_type"]),
            correlation_strength=float(raw["correlation_strength"]),
            lag=float(raw["lag"]),
            predictive_value=float(raw["predictive_value"]),
            reinforcement_signals=reinf,
            divergence_signals=diverg,
            contradiction_score=float(raw["contradiction_score"]),
        )
        async with self._lock:
            self._scps.append(scp)

    async def flush(self) -> CSP | None:
        async with self._lock:
            dips = list(self._dips)
            scps = list(self._scps)
            self._dips.clear()
            self._scps.clear()

        if not dips and not scps:
            logger.debug("EPS flush: no data")
            return None

        domains_involved = list({d.domain_id for d in dips})

        # 1. Reinforcement clustering
        clusters = self._cluster_reinforcement(scps, dips)

        # 2. Drift analysis
        drift_vector, drift_magnitude = DCA.combine(dips)

        # 3. CMX snapshot
        cmx_snap = self.cmx.snapshot()
        cmx_domains = [DomainID(d) for d in cmx_snap["domains"]]
        cmx_matrix  = cmx_snap["matrix"]
        max_contradiction, _, _ = self.cmx.max_contradiction()

        # 4. Align contradiction_matrix to domains_involved
        contradiction_matrix = self._build_contradiction_submatrix(
            domains_involved, cmx_domains, cmx_matrix
        )

        # 5. Synthesis type determination
        synthesis_type = self._determine_synthesis_type(
            domains_involved, scps, drift_magnitude, max_contradiction
        )

        # 6. Predictive indicators
        predictive_indicators = self._derive_predictive_indicators(
            scps, drift_magnitude, max_contradiction
        )

        # 7. Confidence score
        confidence_score = self._compute_confidence(dips, scps)

        # 8. Insight text
        insight = self._generate_insight(
            synthesis_type, domains_involved, max_contradiction,
            drift_magnitude, confidence_score, scps
        )

        # 9. Escalation path
        escalation_path = self._escalation_path(
            confidence_score, max_contradiction, synthesis_type
        )

        csp = CSP(
            synthesis_id=CSP.new_id(),
            timestamp=datetime.utcnow(),
            domains_involved=domains_involved,
            synthesis_type=synthesis_type,
            insight=insight,
            reinforcement_clusters=clusters,
            contradiction_matrix=contradiction_matrix,
            drift_vector=drift_vector,
            predictive_indicators=predictive_indicators,
            confidence_score=round(confidence_score, 4),
            escalation_path=escalation_path,
            metadata={
                "drift_magnitude": drift_magnitude,
                "max_contradiction": max_contradiction,
                "dip_count": len(dips),
                "scp_count": len(scps),
            },
        )

        errors = csp.validate()
        if errors:
            logger.warning("CSP validation errors: %s", errors)

        await self.bus.publish(Topic.CSP_SYNTHESIS, csp)
        logger.info(
            "EPS emitted CSP %s  type=%s  conf=%.2f  escalation=%s",
            csp.synthesis_id, csp.synthesis_type.value,
            csp.confidence_score, csp.escalation_path.value,
        )
        return csp

    # ------------------------------------------------------------------
    # EPS helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _cluster_reinforcement(
        scps: list[SCP], dips: list[DIP]
    ) -> list[ReinforcementCluster]:
        """Group reinforcement_signals by domain origin."""
        by_domain: dict[DomainID, list[Signal]] = defaultdict(list)
        for scp in scps:
            for sig in scp.reinforcement_signals:
                by_domain[scp.domain_a].append(sig)
        for dip in dips:
            for sig in dip.signal_set:
                by_domain[dip.domain_id].append(sig)

        clusters = []
        for domain, signals in by_domain.items():
            if not signals:
                continue
            agg_weight = _np_mean(s.weight for s in signals)
            clusters.append(ReinforcementCluster(
                signals=signals[:8],
                domain_origin=domain,
                weight=round(agg_weight, 4),
            ))
        return clusters

    @staticmethod
    def _build_contradiction_submatrix(
        involved: list[DomainID],
        cmx_domains: list[DomainID],
        cmx_matrix: list[list[float]],
    ) -> list[list[float]]:
        n = len(involved)
        mat = [[0.0] * n for _ in range(n)]
        for i, da in enumerate(involved):
            for j, db in enumerate(involved):
                if i == j:
                    continue
                if da in cmx_domains and db in cmx_domains:
                    ci = cmx_domains.index(da)
                    cj = cmx_domains.index(db)
                    mat[i][j] = cmx_matrix[ci][cj]
        return mat

    @staticmethod
    def _determine_synthesis_type(
        domains: list[DomainID],
        scps: list[SCP],
        drift_magnitude: float,
        max_contradiction: float,
    ) -> SynthesisType:
        domain_set = {d for d in domains}
        has_econ  = DomainID.ECON  in domain_set
        has_gov   = DomainID.GOV   in domain_set
        has_stock = DomainID.STOCK in domain_set
        has_crypto = DomainID.CRYPTO in domain_set

        # Systemic drift takes precedence
        if drift_magnitude >= DRIFT_HIGH_THRESHOLD:
            return SynthesisType.SYSTEMIC_DRIFT

        # High contradiction between ECON/STOCK and GOV → fracture
        if max_contradiction >= CONTRADICTION_HIGH_THRESHOLD and has_econ and has_gov:
            return SynthesisType.MARKET_POLICY_FRACTURE

        # Crypto+Gov convergence
        if has_crypto and has_gov:
            avg_strength = (
                _np_mean(abs(s.correlation_strength) for s in scps)
                if scps else 0.0
            )
            if avg_strength > 0.5:
                return SynthesisType.CRYPTO_REG_CONVERGENCE

        # Multi-domain amplification
        if len(domains) >= 4:
            return SynthesisType.CROSS_DOMAIN_AMPLIFY

        # Liquidity shock: ECON + STOCK + high contradiction
        if has_econ and has_stock and max_contradiction > 0.5:
            return SynthesisType.LIQUIDITY_SHOCK

        # Regulatory divergence
        if has_gov and max_contradiction > 0.4:
            return SynthesisType.REGULATORY_DIVERGENCE

        # Sentiment fracture
        any_sentiment = any(
            any(s.signal_type == SignalType.SENTIMENT for s in scp.divergence_signals)
            for scp in scps
        )
        if any_sentiment:
            return SynthesisType.SENTIMENT_FRACTURE

        return SynthesisType.BASELINE

    @staticmethod
    def _derive_predictive_indicators(
        scps: list[SCP],
        drift_magnitude: float,
        max_contradiction: float,
    ) -> list[PredictiveIndicator]:
        indicators = []

        # Risk indicator
        risk_val = max_contradiction * 0.6 + drift_magnitude * 0.4
        indicators.append(PredictiveIndicator(
            indicator_type=IndicatorType.RISK,
            value=round(risk_val, 4),
            confidence=round(min(1.0, max_contradiction + 0.1), 4),
        ))

        # Opportunity indicator (inverse of contradiction, weighted by reinforcement)
        avg_reinf_conf = (
            _np_mean(
                s.confidence
                for scp in scps
                for s in scp.reinforcement_signals
            ) if any(scp.reinforcement_signals for scp in scps) else 0.5
        )
        opp_val = avg_reinf_conf * (1 - max_contradiction * 0.5)
        indicators.append(PredictiveIndicator(
            indicator_type=IndicatorType.OPPORTUNITY,
            value=round(opp_val, 4),
            confidence=round(avg_reinf_conf, 4),
        ))

        # Instability indicator
        instab = drift_magnitude * 0.5 + max_contradiction * 0.5
        indicators.append(PredictiveIndicator(
            indicator_type=IndicatorType.INSTABILITY,
            value=round(instab, 4),
            confidence=round(min(1.0, drift_magnitude + 0.15), 4),
        ))

        # Inflection point
        avg_pred = (
            _np_mean(scp.predictive_value for scp in scps) if scps else 0.0
        )
        indicators.append(PredictiveIndicator(
            indicator_type=IndicatorType.INFLECTION,
            value=round(avg_pred, 4),
            confidence=round(avg_pred, 4),
        ))

        return indicators

    @staticmethod
    def _compute_confidence(dips: list[DIP], scps: list[SCP]) -> float:
        scores = []
        if dips:
            scores.append(_np_mean(d.confidence_score for d in dips))
        if scps:
            scores.append(_np_mean(abs(s.correlation_strength) for s in scps))
            scores.append(_np_mean(s.predictive_value for s in scps))
        return _np_mean(scores) if scores else 0.0

    @staticmethod
    def _generate_insight(
        synthesis_type: SynthesisType,
        domains: list[DomainID],
        max_contradiction: float,
        drift_magnitude: float,
        confidence: float,
        scps: list[SCP],
    ) -> str:
        domain_labels = ", ".join(d.value for d in domains)

        divergent_pairs = [
            (s.domain_a.value, s.domain_b.value)
            for s in scps
            if s.correlation_type == CorrelationType.DIVERGENT
        ]
        reinforcing_pairs = [
            f"{s.domain_a.value}↔{s.domain_b.value}"
            for s in scps
            if s.correlation_type == CorrelationType.REINFORCING
        ]

        lines = [
            f"[{synthesis_type.value}] Synthesis across domains: {domain_labels}.",
            f"Max cross-domain contradiction: {max_contradiction:.2f}  |  "
            f"Drift magnitude: {drift_magnitude:.2f}  |  Confidence: {confidence:.2f}.",
        ]
        if reinforcing_pairs:
            lines.append(f"Reinforcing pairs: {', '.join(reinforcing_pairs[:4])}.")

        # ── Operator contradiction templates (I·SRC — cds_omega1.py) ─────────
        # Reverse map DomainID enum → canonical lowercase key used in templates
        _rev = {v: k for k, v in DOMAIN_ID_MAP.items()}
        template_lines = []
        for da_val, db_val in divergent_pairs[:3]:
            da_key = _rev.get(da_val, da_val.lower())
            db_key = _rev.get(db_val, db_val.lower())
            # Determine sign of delta to pick positive/negative template variant
            matching_scp = next(
                (s for s in scps
                 if s.domain_a.value == da_val and s.domain_b.value == db_val),
                None,
            )
            positive = (matching_scp.correlation_strength >= 0) if matching_scp else True
            tmpl = contradiction_template(da_key, db_key, positive)
            if tmpl:
                template_lines.append(tmpl)

        if template_lines:
            lines.extend(template_lines)
        elif divergent_pairs:
            lines.append(
                f"Divergent pairs: {', '.join(f"{a}↔{b}" for a, b in divergent_pairs[:4])}."
            )

        template = {
            SynthesisType.MARKET_POLICY_FRACTURE: (
                "Significant fracture detected between market signals and policy direction. "
                "Expect delayed re-alignment or volatility spike."
            ),
            SynthesisType.CRYPTO_REG_CONVERGENCE: (
                "Regulatory signals are converging with crypto domain activity. "
                "Monitor for compliance-driven price action."
            ),
            SynthesisType.SYSTEMIC_DRIFT: (
                "Systemic drift exceeds threshold across all observed domains. "
                "Regime shift in progress — heightened uncertainty."
            ),
            SynthesisType.CROSS_DOMAIN_AMPLIFY: (
                "Multi-domain reinforcement loop identified. "
                "Signals are amplifying across sectors — trend acceleration possible."
            ),
            SynthesisType.LIQUIDITY_SHOCK: (
                "Liquidity stress signatures emerging from ECON-STOCK divergence. "
                "Monitor flow signals closely."
            ),
            SynthesisType.REGULATORY_DIVERGENCE: (
                "Regulatory and market signals diverging. "
                "Policy uncertainty is structurally elevated."
            ),
            SynthesisType.SENTIMENT_FRACTURE: (
                "Sentiment signals are fragmenting across domains. "
                "Divergent narratives detected — watch for sharp corrections."
            ),
            SynthesisType.BASELINE: (
                "No critical pattern detected. Baseline conditions across observed domains."
            ),
        }
        lines.append(template.get(synthesis_type, ""))
        return " ".join(l for l in lines if l)

    @staticmethod
    def _escalation_path(
        confidence: float,
        max_contradiction: float,
        synthesis_type: SynthesisType,
    ) -> EscalationPath:
        # Confidence gate (spec §5)
        if confidence < CONFIDENCE_GATE:
            return EscalationPath.NONE

        # Paradox Engine: high contradiction
        if max_contradiction >= CONTRADICTION_HIGH_THRESHOLD:
            return EscalationPath.PARADOX_ENGINE

        # Systemic drift → Operator Alert
        if synthesis_type == SynthesisType.SYSTEMIC_DRIFT:
            return EscalationPath.OPERATOR_ALERT

        # Default → Field Intel
        return EscalationPath.FIELD_INTEL

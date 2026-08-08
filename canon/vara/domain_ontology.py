"""
Domain Ontologies — signal grammars, vocabularies, and pattern expectations
for each of the five Canon intelligence domains.

Each DomainOntology defines:
  - signal_types     : valid signal keys for this domain
  - weight_map       : default weights per signal type
  - anomaly_rules    : (field, predicate, reason) triples
  - weak_signal_keys : keys to probe for low-amplitude signals
  - trend_patterns   : named patterns and their constituent signal keys
  - cadence_s        : default harvesting interval in seconds
  - escalation_bias  : multiplier applied to contradiction/drift thresholds
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from canon_constants import DOMAIN_WEIGHT as _CANON_DOMAIN_WEIGHT


# ---------------------------------------------------------------------------
# Core structures
# ---------------------------------------------------------------------------

@dataclass
class AnomalyRule:
    field:     str
    predicate: Callable[[Any], bool]
    reason:    str


@dataclass
class TrendPattern:
    name:         str
    signal_keys:  list[str]   # ALL keys must appear for trend to fire
    min_signals:  int = 2     # minimum subset sufficient to confirm


@dataclass
class DomainOntology:
    domain_id:        str
    display_name:     str
    signal_types:     list[str]
    weight_map:       dict[str, float]
    anomaly_rules:    list[AnomalyRule]
    weak_signal_keys: list[str]
    trend_patterns:   list[TrendPattern]
    cadence_s:        int   = 3600
    escalation_bias:  float = 1.0

    def weight(self, signal_type: str) -> float:
        return self.weight_map.get(signal_type, 0.5)


# ===========================================================================
# ECON — Economics
# ===========================================================================

ECON_ONTOLOGY = DomainOntology(
    domain_id    = "ECON",
    display_name = "Economics",
    signal_types = [
        "gdp_growth", "inflation_rate", "unemployment_rate", "interest_rate",
        "trade_balance", "consumer_confidence", "ppi", "cpi", "m2_supply",
        "yield_curve", "debt_to_gdp", "budget_deficit", "fx_rate",
        "credit_spread", "ism_manufacturing", "retail_sales",
    ],
    weight_map = {
        "gdp_growth":          0.90,
        "inflation_rate":      0.85,
        "interest_rate":       0.88,
        "yield_curve":         0.82,
        "unemployment_rate":   0.75,
        "m2_supply":           0.70,
        "cpi":                 0.80,
        "ppi":                 0.72,
        "trade_balance":       0.65,
        "consumer_confidence": 0.60,
        "debt_to_gdp":         0.68,
        "budget_deficit":      0.65,
        "fx_rate":             0.60,
        "credit_spread":       0.78,
        "ism_manufacturing":   0.62,
        "retail_sales":        0.58,
    },
    anomaly_rules = [
        AnomalyRule("inflation_rate",    lambda v: float(v) > 8.0,
                    "Hyperinflationary pressure: CPI annualised >8%"),
        AnomalyRule("yield_curve",       lambda v: float(v) < 0.0,
                    "Inverted yield curve: recession signal active"),
        AnomalyRule("unemployment_rate", lambda v: float(v) > 10.0,
                    "Unemployment above 10%: structural distress"),
        AnomalyRule("credit_spread",     lambda v: float(v) > 5.0,
                    "Credit spread >500bps: systemic credit stress"),
        AnomalyRule("debt_to_gdp",       lambda v: float(v) > 130.0,
                    "Debt/GDP >130%: sovereign sustainability risk"),
    ],
    weak_signal_keys = [
        "yield_curve", "credit_spread", "m2_supply",
        "ism_manufacturing", "consumer_confidence",
    ],
    trend_patterns = [
        TrendPattern("Stagflation",          ["inflation_rate", "unemployment_rate", "gdp_growth"], min_signals=3),
        TrendPattern("Rate Shock",           ["interest_rate", "yield_curve", "credit_spread"],     min_signals=2),
        TrendPattern("Fiscal Deterioration", ["budget_deficit", "debt_to_gdp", "fx_rate"],          min_signals=2),
        TrendPattern("Consumer Contraction", ["consumer_confidence", "retail_sales", "cpi"],         min_signals=2),
        TrendPattern("Monetary Expansion",   ["m2_supply", "interest_rate", "inflation_rate"],       min_signals=2),
    ],
    cadence_s       = 1800,   # 30 min
    escalation_bias = 1.1,
)


# ===========================================================================
# CRYPTO — Cryptocurrency & Digital Assets
# ===========================================================================

CRYPTO_ONTOLOGY = DomainOntology(
    domain_id    = "CRYPTO",
    display_name = "Cryptocurrency & Digital Assets",
    signal_types = [
        "btc_price", "eth_price", "btc_dominance", "total_market_cap",
        "fear_greed_index", "exchange_inflow", "exchange_outflow",
        "stablecoin_supply", "funding_rate", "open_interest",
        "hash_rate", "miner_revenue", "defi_tvl", "nft_volume",
        "regulatory_sentiment", "on_chain_velocity",
    ],
    weight_map = {
        "btc_price":            0.85,
        "total_market_cap":     0.80,
        "fear_greed_index":     0.72,
        "funding_rate":         0.78,
        "open_interest":        0.75,
        "exchange_inflow":      0.70,
        "exchange_outflow":     0.70,
        "stablecoin_supply":    0.68,
        "regulatory_sentiment": 0.82,
        "hash_rate":            0.60,
        "miner_revenue":        0.58,
        "defi_tvl":             0.65,
        "on_chain_velocity":    0.62,
        "btc_dominance":        0.55,
        "eth_price":            0.75,
        "nft_volume":           0.40,
    },
    anomaly_rules = [
        AnomalyRule("fear_greed_index",  lambda v: float(v) < 15.0,
                    "Extreme Fear: capitulation-level sentiment"),
        AnomalyRule("fear_greed_index",  lambda v: float(v) > 90.0,
                    "Extreme Greed: bubble/blow-off top signal"),
        AnomalyRule("funding_rate",      lambda v: abs(float(v)) > 0.1,
                    "Funding rate >10%: extreme leverage imbalance"),
        AnomalyRule("exchange_inflow",   lambda v: float(v) > 50000.0,
                    "BTC exchange inflow >50k: potential sell pressure"),
        AnomalyRule("regulatory_sentiment", lambda v: float(v) < -0.6,
                    "Strongly negative regulatory sentiment: ban risk"),
    ],
    weak_signal_keys = [
        "funding_rate", "stablecoin_supply", "on_chain_velocity",
        "exchange_inflow", "regulatory_sentiment",
    ],
    trend_patterns = [
        TrendPattern("Crypto Winter",         ["btc_price", "fear_greed_index", "defi_tvl"],       min_signals=2),
        TrendPattern("Leverage Flush",        ["funding_rate", "open_interest", "btc_price"],       min_signals=3),
        TrendPattern("Regulatory Crackdown",  ["regulatory_sentiment", "exchange_outflow", "stablecoin_supply"], min_signals=2),
        TrendPattern("Accumulation Phase",    ["exchange_outflow", "on_chain_velocity", "fear_greed_index"], min_signals=2),
        TrendPattern("Miner Capitulation",    ["hash_rate", "miner_revenue", "btc_price"],          min_signals=3),
    ],
    cadence_s       = 900,    # 15 min — high frequency
    escalation_bias = 1.3,    # crypto moves fast
)


# ===========================================================================
# GEOPOL — US Foreign Relations & Geopolitics
# ===========================================================================

GEOPOL_ONTOLOGY = DomainOntology(
    domain_id    = "GEOPOL",
    display_name = "US Foreign Relations & Geopolitical Power",
    signal_types = [
        "diplomatic_incident_count", "sanction_intensity", "alliance_cohesion",
        "military_posture", "trade_tension_index", "treaty_compliance",
        "un_vote_alignment", "foreign_aid_flow", "arms_export_volume",
        "adversary_provocation_index", "intelligence_alert_level",
        "bilateral_stability", "proxy_conflict_intensity", "tariff_index",
        "soft_power_index", "cyber_incident_count",
    ],
    weight_map = {
        "diplomatic_incident_count":   0.80,
        "sanction_intensity":          0.85,
        "military_posture":            0.90,
        "alliance_cohesion":           0.82,
        "trade_tension_index":         0.78,
        "adversary_provocation_index": 0.88,
        "intelligence_alert_level":    0.92,
        "proxy_conflict_intensity":    0.85,
        "bilateral_stability":         0.75,
        "treaty_compliance":           0.70,
        "un_vote_alignment":           0.55,
        "foreign_aid_flow":            0.50,
        "arms_export_volume":          0.65,
        "tariff_index":                0.68,
        "soft_power_index":            0.45,
        "cyber_incident_count":        0.80,
    },
    anomaly_rules = [
        AnomalyRule("military_posture",            lambda v: float(v) > 8.0,
                    "Military posture at DEFCON-adjacent level"),
        AnomalyRule("adversary_provocation_index", lambda v: float(v) > 0.8,
                    "Adversary provocation at critical threshold"),
        AnomalyRule("sanction_intensity",          lambda v: float(v) > 9.0,
                    "Near-maximum sanction regime active"),
        AnomalyRule("cyber_incident_count",        lambda v: float(v) > 50,
                    "State-level cyber campaign in progress"),
        AnomalyRule("alliance_cohesion",           lambda v: float(v) < 0.3,
                    "Critical alliance fragmentation detected"),
    ],
    weak_signal_keys = [
        "intelligence_alert_level", "bilateral_stability",
        "proxy_conflict_intensity", "cyber_incident_count", "treaty_compliance",
    ],
    trend_patterns = [
        TrendPattern("Cold War Reactivation",  ["adversary_provocation_index", "military_posture", "alliance_cohesion"], min_signals=3),
        TrendPattern("Sanctions Escalation",   ["sanction_intensity", "trade_tension_index", "tariff_index"],            min_signals=2),
        TrendPattern("Alliance Drift",         ["alliance_cohesion", "un_vote_alignment", "treaty_compliance"],          min_signals=2),
        TrendPattern("Proxy Escalation",       ["proxy_conflict_intensity", "military_posture", "intelligence_alert_level"], min_signals=2),
        TrendPattern("Cyber Warfare Phase",    ["cyber_incident_count", "intelligence_alert_level", "bilateral_stability"], min_signals=2),
    ],
    cadence_s       = 3600,
    escalation_bias = 1.25,
)


# ===========================================================================
# WORLDPOL — World Politics
# ===========================================================================

WORLDPOL_ONTOLOGY = DomainOntology(
    domain_id    = "WORLDPOL",
    display_name = "World Politics & Governance",
    signal_types = [
        "global_democracy_index", "authoritarian_drift_index",
        "election_integrity_score", "populism_surge_index",
        "institutional_erosion_index", "press_freedom_index",
        "civil_unrest_index", "coup_risk_score", "regional_conflict_count",
        "multilateral_cooperation_index", "sovereignty_dispute_count",
        "refugee_flow_magnitude", "state_fragility_index",
        "corruption_perception_index", "social_stability_index",
        "nuclear_risk_index",
    ],
    weight_map = {
        "global_democracy_index":          0.70,
        "authoritarian_drift_index":       0.82,
        "institutional_erosion_index":     0.80,
        "civil_unrest_index":              0.85,
        "coup_risk_score":                 0.90,
        "regional_conflict_count":         0.88,
        "state_fragility_index":           0.85,
        "nuclear_risk_index":              0.95,
        "populism_surge_index":            0.72,
        "election_integrity_score":        0.68,
        "press_freedom_index":             0.60,
        "multilateral_cooperation_index":  0.65,
        "sovereignty_dispute_count":       0.75,
        "refugee_flow_magnitude":          0.70,
        "corruption_perception_index":     0.55,
        "social_stability_index":          0.78,
    },
    anomaly_rules = [
        AnomalyRule("coup_risk_score",          lambda v: float(v) > 0.8,
                    "Imminent coup risk: political rupture likely"),
        AnomalyRule("nuclear_risk_index",       lambda v: float(v) > 0.7,
                    "Nuclear escalation risk at high threshold"),
        AnomalyRule("civil_unrest_index",       lambda v: float(v) > 0.85,
                    "Systemic civil unrest: state control degrading"),
        AnomalyRule("authoritarian_drift_index",lambda v: float(v) > 0.75,
                    "Democratic backsliding at critical pace"),
        AnomalyRule("state_fragility_index",    lambda v: float(v) > 0.9,
                    "Failed-state threshold breached"),
    ],
    weak_signal_keys = [
        "institutional_erosion_index", "populism_surge_index",
        "sovereignty_dispute_count", "press_freedom_index",
        "corruption_perception_index",
    ],
    trend_patterns = [
        TrendPattern("Democratic Collapse",   ["authoritarian_drift_index", "election_integrity_score", "press_freedom_index"],      min_signals=2),
        TrendPattern("Regional War Onset",    ["regional_conflict_count", "sovereignty_dispute_count", "refugee_flow_magnitude"],    min_signals=2),
        TrendPattern("State Fragmentation",   ["state_fragility_index", "coup_risk_score", "civil_unrest_index"],                   min_signals=3),
        TrendPattern("Multilateral Breakdown",["multilateral_cooperation_index", "sovereignty_dispute_count", "nuclear_risk_index"], min_signals=2),
        TrendPattern("Populist Wave",         ["populism_surge_index", "institutional_erosion_index", "press_freedom_index"],       min_signals=2),
    ],
    cadence_s       = 3600,
    escalation_bias = 1.2,
)


# ===========================================================================
# INDUSTRIAL — Industrial, Supply Chain & Energy
# ===========================================================================

INDUSTRIAL_ONTOLOGY = DomainOntology(
    domain_id    = "INDUSTRIAL",
    display_name = "Industrial, Supply Chain & Energy",
    signal_types = [
        "manufacturing_pmi", "industrial_output_index", "supply_chain_stress",
        "freight_rate_index", "port_congestion_index", "energy_price_index",
        "oil_price", "natural_gas_price", "coal_price",
        "semiconductor_shortage_index", "rare_earth_supply_index",
        "capacity_utilization", "inventory_to_sales_ratio",
        "labor_productivity", "capex_investment_index",
        "grid_stability_index", "water_stress_index",
    ],
    weight_map = {
        "manufacturing_pmi":          0.82,
        "supply_chain_stress":        0.88,
        "energy_price_index":         0.85,
        "oil_price":                  0.80,
        "semiconductor_shortage_index": 0.90,
        "rare_earth_supply_index":    0.85,
        "freight_rate_index":         0.75,
        "port_congestion_index":      0.72,
        "capacity_utilization":       0.70,
        "industrial_output_index":    0.78,
        "natural_gas_price":          0.72,
        "coal_price":                 0.55,
        "inventory_to_sales_ratio":   0.68,
        "labor_productivity":         0.62,
        "capex_investment_index":     0.65,
        "grid_stability_index":       0.80,
        "water_stress_index":         0.70,
    },
    anomaly_rules = [
        AnomalyRule("supply_chain_stress",        lambda v: float(v) > 0.85,
                    "Critical supply chain stress: multi-sector disruption"),
        AnomalyRule("semiconductor_shortage_index",lambda v: float(v) > 0.80,
                    "Semiconductor shortage at systemic level"),
        AnomalyRule("energy_price_index",         lambda v: float(v) > 200.0,
                    "Energy price shock: 2× baseline breach"),
        AnomalyRule("port_congestion_index",       lambda v: float(v) > 0.90,
                    "Port system near-gridlock: supply delay cascade"),
        AnomalyRule("grid_stability_index",        lambda v: float(v) < 0.3,
                    "Grid instability: industrial output risk"),
    ],
    weak_signal_keys = [
        "inventory_to_sales_ratio", "rare_earth_supply_index",
        "capex_investment_index", "labor_productivity",
        "water_stress_index",
    ],
    trend_patterns = [
        TrendPattern("Supply Shock",          ["supply_chain_stress", "freight_rate_index", "port_congestion_index"],       min_signals=2),
        TrendPattern("Energy Crisis",         ["energy_price_index", "oil_price", "natural_gas_price"],                    min_signals=2),
        TrendPattern("Industrial Contraction",["manufacturing_pmi", "capacity_utilization", "industrial_output_index"],     min_signals=2),
        TrendPattern("Critical Input Squeeze",["semiconductor_shortage_index", "rare_earth_supply_index", "capex_investment_index"], min_signals=2),
        TrendPattern("Inventory Glut",        ["inventory_to_sales_ratio", "freight_rate_index", "manufacturing_pmi"],      min_signals=2),
    ],
    cadence_s       = 3600,
    escalation_bias = 1.0,
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

DOMAIN_REGISTRY: dict[str, DomainOntology] = {
    "ECON":       ECON_ONTOLOGY,
    "CRYPTO":     CRYPTO_ONTOLOGY,
    "GEOPOL":     GEOPOL_ONTOLOGY,
    "WORLDPOL":   WORLDPOL_ONTOLOGY,
    "INDUSTRIAL": INDUSTRIAL_ONTOLOGY,
}


def get_ontology(domain_id: str) -> DomainOntology:
    onto = DOMAIN_REGISTRY.get(domain_id.upper())
    if onto is None:
        raise KeyError(f"No ontology registered for domain '{domain_id}'. "
                       f"Available: {list(DOMAIN_REGISTRY)}")
    return onto

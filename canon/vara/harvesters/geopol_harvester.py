"""
Vara.GEOPOL — US Foreign Relations & Geopolitical Power Domain Harvester

Sources modelled (simulated; swap fetch() for live feeds):
  - State Dept. press releases / diplomatic cables (NLP)
  - OFAC sanctions database delta
  - Pentagon/DoD readiness indicators
  - USTR trade tension tracker
  - CISA cyber incident feed
  - UN General Assembly voting records
  - Arms Control Association treaty compliance tracker
"""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any

from vara.domain_ontology import GEOPOL_ONTOLOGY, DomainOntology
from vara.harvesters.base_harvester import BaseHarvester


class GeoPolHarvester(BaseHarvester):
    """
    Domain harvester for US Foreign Relations & Geopolitical Power (Vara.GEOPOL).

    Signal coverage
    ---------------
    diplomatic_incident_count    : # of formal diplomatic protests/recalls (30d)
    sanction_intensity           : 0–10 scale of active sanction regime severity
    alliance_cohesion            : 0–1 (1 = fully cohesive NATO/partner alignment)
    military_posture             : 0–10 DEFCON-proxy (10 = maximum alert)
    trade_tension_index          : 0–10 aggregate tariff/trade-war intensity
    treaty_compliance            : 0–1 (counterparty treaty adherence score)
    un_vote_alignment            : % of UNGA votes aligned with US position
    foreign_aid_flow             : US foreign assistance disbursed ($bn, annualised)
    arms_export_volume           : US arms export value ($bn, annualised)
    adversary_provocation_index  : 0–1 (aggregate China+Russia+NK provocation)
    intelligence_alert_level     : 0–1 (IC threat level proxy)
    bilateral_stability          : 0–1 (mean stability across top 20 bilateral relations)
    proxy_conflict_intensity     : 0–1 (active proxy/indirect conflict burden)
    tariff_index                 : effective average US tariff rate (%)
    soft_power_index             : 0–100 (Portland Soft Power 30 proxy)
    cyber_incident_count         : # of state-attributed cyber incidents (30d)
    """

    DOMAIN = "GEOPOL"

    @property
    def domain_id(self) -> str:
        return self.DOMAIN

    @property
    def ontology(self) -> DomainOntology:
        return GEOPOL_ONTOLOGY

    async def fetch(self) -> dict[str, Any]:
        return self._simulate_source()

    def _simulate_source(self) -> dict[str, Any]:
        rng = random.Random(int(datetime.utcnow().timestamp()) // 3600)
        # Simulate elevated geopolitical stress (South China Sea + Ukraine + sanctions)
        return {
            "STATE_DIPLOMATIC_INCIDENTS_30D": round(rng.gauss(14.0, 4.0), 0),
            "OFAC_SANCTION_INTENSITY":        round(rng.gauss(7.8, 0.6), 1),
            "NATO_COHESION_SCORE":            round(rng.gauss(0.68, 0.08), 3),
            "DOD_MILITARY_POSTURE":           round(rng.gauss(6.5, 0.9), 1),
            "USTR_TRADE_TENSION_INDEX":       round(rng.gauss(6.2, 0.8), 1),
            "ACA_TREATY_COMPLIANCE":          round(rng.gauss(0.54, 0.10), 3),
            "UN_VOTE_ALIGNMENT_PCT":          round(rng.gauss(0.41, 0.06), 3),
            "STATE_FOREIGN_AID_BN":           round(rng.gauss(52.0, 5.0), 1),
            "DSCA_ARMS_EXPORT_BN":            round(rng.gauss(78.5, 9.0), 1),
            "IC_ADVERSARY_PROVOCATION":       round(rng.gauss(0.62, 0.12), 3),
            "IC_INTELLIGENCE_ALERT":          round(rng.gauss(0.58, 0.10), 3),
            "STATE_BILATERAL_STABILITY":      round(rng.gauss(0.56, 0.09), 3),
            "DOD_PROXY_CONFLICT_INTENSITY":   round(rng.gauss(0.55, 0.12), 3),
            "USTR_EFFECTIVE_TARIFF_RATE":     round(rng.gauss(14.8, 2.5), 2),
            "PORTLAND_SOFT_POWER":            round(rng.gauss(74.5, 3.0), 1),
            "CISA_CYBER_INCIDENTS_30D":       round(rng.gauss(28.0, 9.0), 0),
        }

    def normalise(self, raw: dict[str, Any]) -> dict[str, Any]:
        return {
            "diplomatic_incident_count":    self._f(raw, "STATE_DIPLOMATIC_INCIDENTS_30D"),
            "sanction_intensity":           self._f(raw, "OFAC_SANCTION_INTENSITY"),
            "alliance_cohesion":            self._f(raw, "NATO_COHESION_SCORE"),
            "military_posture":             self._f(raw, "DOD_MILITARY_POSTURE"),
            "trade_tension_index":          self._f(raw, "USTR_TRADE_TENSION_INDEX"),
            "treaty_compliance":            self._f(raw, "ACA_TREATY_COMPLIANCE"),
            "un_vote_alignment":            self._f(raw, "UN_VOTE_ALIGNMENT_PCT"),
            "foreign_aid_flow":             self._f(raw, "STATE_FOREIGN_AID_BN"),
            "arms_export_volume":           self._f(raw, "DSCA_ARMS_EXPORT_BN"),
            "adversary_provocation_index":  self._f(raw, "IC_ADVERSARY_PROVOCATION"),
            "intelligence_alert_level":     self._f(raw, "IC_INTELLIGENCE_ALERT"),
            "bilateral_stability":          self._f(raw, "STATE_BILATERAL_STABILITY"),
            "proxy_conflict_intensity":     self._f(raw, "DOD_PROXY_CONFLICT_INTENSITY"),
            "tariff_index":                 self._f(raw, "USTR_EFFECTIVE_TARIFF_RATE"),
            "soft_power_index":             self._f(raw, "PORTLAND_SOFT_POWER"),
            "cyber_incident_count":         self._f(raw, "CISA_CYBER_INCIDENTS_30D"),
        }

    @staticmethod
    def _f(d: dict, key: str, default: float = 0.0) -> float:
        try:
            return float(d.get(key, default))
        except (TypeError, ValueError):
            return default

"""
Vara.WORLDPOL — World Politics & Governance Domain Harvester

Sources modelled (simulated; swap fetch() for live feeds):
  - V-Dem / Freedom House (democracy, press freedom indices)
  - ACLED (armed conflict & civil unrest event data)
  - Fund for Peace (Fragile States Index)
  - EIU / Eurasia Group (political risk scores)
  - IAEA / NTI (nuclear risk tracker)
  - UN OCHA (refugee flow data)
  - Transparency International (CPI)
  - Global Coalition trackers (multilateral cooperation)
"""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any

from vara.domain_ontology import WORLDPOL_ONTOLOGY, DomainOntology
from vara.harvesters.base_harvester import BaseHarvester


class WorldPolHarvester(BaseHarvester):
    """
    Domain harvester for World Politics & Governance (Vara.WORLDPOL).

    Signal coverage
    ---------------
    global_democracy_index         : V-Dem Liberal Democracy Index (0–1)
    authoritarian_drift_index      : pace of democratic backsliding (0–1)
    election_integrity_score       : Electoral Integrity Project (0–1)
    populism_surge_index           : Team Populism aggregate (0–1)
    institutional_erosion_index    : checks & balances degradation (0–1)
    press_freedom_index            : RSF Press Freedom (0–1, 1=most free)
    civil_unrest_index             : ACLED normalised event intensity (0–1)
    coup_risk_score                : EIU coup risk (0–1)
    regional_conflict_count        : active armed conflicts ≥25 deaths/year
    multilateral_cooperation_index : IGO engagement score (0–1)
    sovereignty_dispute_count      : active territorial disputes
    refugee_flow_magnitude         : UNHCR new displacement (millions)
    state_fragility_index          : FSI normalised (0–1, 1=most fragile)
    corruption_perception_index    : TI CPI (0–100, 100=cleanest)
    social_stability_index         : Economist Social Stability (0–1)
    nuclear_risk_index             : NTI nuclear security (0–1, 1=highest risk)
    """

    DOMAIN = "WORLDPOL"

    @property
    def domain_id(self) -> str:
        return self.DOMAIN

    @property
    def ontology(self) -> DomainOntology:
        return WORLDPOL_ONTOLOGY

    async def fetch(self) -> dict[str, Any]:
        return self._simulate_source()

    def _simulate_source(self) -> dict[str, Any]:
        rng = random.Random(int(datetime.utcnow().timestamp()) // 3600)
        # Simulate a world with elevated instability + democratic backsliding
        return {
            "VDEM_LDI":                   round(rng.gauss(0.44, 0.04), 3),
            "VDEM_BACKSLIDING_RATE":      round(rng.gauss(0.58, 0.08), 3),
            "EIP_ELECTION_INTEGRITY":     round(rng.gauss(0.52, 0.07), 3),
            "TEAM_POP_POPULISM_IDX":      round(rng.gauss(0.61, 0.09), 3),
            "EROSION_CHECKS_BALANCES":    round(rng.gauss(0.55, 0.08), 3),
            "RSF_PRESS_FREEDOM":          round(rng.gauss(0.48, 0.06), 3),
            "ACLED_CIVIL_UNREST_NORM":    round(rng.gauss(0.62, 0.10), 3),
            "EIU_COUP_RISK":              round(rng.gauss(0.32, 0.10), 3),
            "ACLED_ACTIVE_CONFLICTS":     round(rng.gauss(56.0, 7.0), 0),
            "IGO_MULTILATERAL_SCORE":     round(rng.gauss(0.52, 0.08), 3),
            "ICJ_TERRITORIAL_DISPUTES":   round(rng.gauss(22.0, 4.0), 0),
            "UNHCR_DISPLACEMENT_M":       round(rng.gauss(31.5, 4.0), 1),
            "FSI_FRAGILITY_NORM":         round(rng.gauss(0.58, 0.07), 3),
            "TI_CPI":                     round(rng.gauss(43.0, 3.5), 1),
            "EIU_SOCIAL_STABILITY":       round(rng.gauss(0.51, 0.08), 3),
            "NTI_NUCLEAR_RISK":           round(rng.gauss(0.48, 0.09), 3),
        }

    def normalise(self, raw: dict[str, Any]) -> dict[str, Any]:
        return {
            "global_democracy_index":         self._f(raw, "VDEM_LDI"),
            "authoritarian_drift_index":      self._f(raw, "VDEM_BACKSLIDING_RATE"),
            "election_integrity_score":       self._f(raw, "EIP_ELECTION_INTEGRITY"),
            "populism_surge_index":           self._f(raw, "TEAM_POP_POPULISM_IDX"),
            "institutional_erosion_index":    self._f(raw, "EROSION_CHECKS_BALANCES"),
            "press_freedom_index":            self._f(raw, "RSF_PRESS_FREEDOM"),
            "civil_unrest_index":             self._f(raw, "ACLED_CIVIL_UNREST_NORM"),
            "coup_risk_score":                self._f(raw, "EIU_COUP_RISK"),
            "regional_conflict_count":        self._f(raw, "ACLED_ACTIVE_CONFLICTS"),
            "multilateral_cooperation_index": self._f(raw, "IGO_MULTILATERAL_SCORE"),
            "sovereignty_dispute_count":      self._f(raw, "ICJ_TERRITORIAL_DISPUTES"),
            "refugee_flow_magnitude":         self._f(raw, "UNHCR_DISPLACEMENT_M"),
            "state_fragility_index":          self._f(raw, "FSI_FRAGILITY_NORM"),
            "corruption_perception_index":    self._f(raw, "TI_CPI"),
            "social_stability_index":         self._f(raw, "EIU_SOCIAL_STABILITY"),
            "nuclear_risk_index":             self._f(raw, "NTI_NUCLEAR_RISK"),
        }

    @staticmethod
    def _f(d: dict, key: str, default: float = 0.0) -> float:
        try:
            return float(d.get(key, default))
        except (TypeError, ValueError):
            return default

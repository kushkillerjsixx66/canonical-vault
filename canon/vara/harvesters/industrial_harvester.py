"""
Vara.INDUSTRIAL — Industrial, Supply Chain & Energy Domain Harvester

Sources modelled (simulated; swap fetch() for live feeds):
  - ISM Manufacturing / S&P Global PMI
  - Freightos Baltic Index (freight rates)
  - U.S. Energy Information Administration (EIA) — oil, gas, coal prices
  - World Semiconductor Trade Statistics (WSTS)
  - Federal Reserve — capacity utilization
  - Bureau of Labor Statistics — labor productivity
  - U.S. Census — inventory-to-sales ratio
  - NERC — grid stability index
  - World Resources Institute — water stress
  - Rare Earth Industry Association — supply index
"""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any

from vara.domain_ontology import INDUSTRIAL_ONTOLOGY, DomainOntology
from vara.harvesters.base_harvester import BaseHarvester


class IndustrialHarvester(BaseHarvester):
    """
    Domain harvester for Industrial, Supply Chain & Energy (Vara.INDUSTRIAL).

    Signal coverage
    ---------------
    manufacturing_pmi             : ISM/S&P Global Manufacturing PMI
    industrial_output_index       : Fed Industrial Production Index (YoY %)
    supply_chain_stress           : NY Fed GSCPI normalised (0–1)
    freight_rate_index            : Freightos Baltic Index (FBX, normalised)
    port_congestion_index         : UNCTAD port congestion score (0–1)
    energy_price_index            : EIA composite energy price index
    oil_price                     : WTI crude $/bbl
    natural_gas_price             : Henry Hub $/MMBtu
    coal_price                    : API2 Rotterdam $/tonne
    semiconductor_shortage_index  : WSTS demand-supply gap (0–1)
    rare_earth_supply_index       : REIA supply adequacy (0–1, 1=scarce)
    capacity_utilization          : Fed capacity utilization rate (%)
    inventory_to_sales_ratio      : Census I/S ratio
    labor_productivity            : BLS output-per-hour YoY (%)
    capex_investment_index        : S&P 500 capex growth YoY (%)
    grid_stability_index          : NERC composite (0–1, 1=stable)
    water_stress_index            : WRI Aqueduct (0–1, 1=extreme stress)
    """

    DOMAIN = "INDUSTRIAL"

    @property
    def domain_id(self) -> str:
        return self.DOMAIN

    @property
    def ontology(self) -> DomainOntology:
        return INDUSTRIAL_ONTOLOGY

    async def fetch(self) -> dict[str, Any]:
        return self._simulate_source()

    def _simulate_source(self) -> dict[str, Any]:
        rng = random.Random(int(datetime.utcnow().timestamp()) // 3600)
        # Simulate elevated supply-chain stress + energy price pressure
        return {
            "ISM_PMI":                    round(rng.gauss(48.4, 1.9), 1),   # sub-50 = contraction
            "FED_INDPRO_YOY":             round(rng.gauss(1.2, 0.8), 2),
            "NYFED_GSCPI_NORM":           round(rng.gauss(0.62, 0.12), 3),
            "FBX_FREIGHT_NORM":           round(rng.gauss(0.68, 0.10), 3),
            "UNCTAD_PORT_CONGESTION":     round(rng.gauss(0.58, 0.10), 3),
            "EIA_ENERGY_PRICE_INDEX":     round(rng.gauss(148.0, 14.0), 1),
            "EIA_WTI_CRUDE":              round(rng.gauss(89.5, 5.5), 2),
            "EIA_HENRY_HUB":              round(rng.gauss(3.18, 0.45), 3),
            "API2_COAL_ROTTERDAM":        round(rng.gauss(118.0, 12.0), 1),
            "WSTS_SEMI_SHORTAGE_NORM":    round(rng.gauss(0.58, 0.12), 3),
            "REIA_RARE_EARTH_SCARCITY":   round(rng.gauss(0.65, 0.10), 3),
            "FED_CAP_UTIL_PCT":           round(rng.gauss(77.8, 1.5), 1),
            "CENSUS_INV_SALES_RATIO":     round(rng.gauss(1.38, 0.06), 3),
            "BLS_LABOR_PRODUCTIVITY_YOY": round(rng.gauss(1.5, 0.8), 2),
            "SP500_CAPEX_GROWTH_YOY":     round(rng.gauss(4.2, 2.5), 2),
            "NERC_GRID_STABILITY":        round(rng.gauss(0.78, 0.07), 3),
            "WRI_WATER_STRESS":           round(rng.gauss(0.52, 0.08), 3),
        }

    def normalise(self, raw: dict[str, Any]) -> dict[str, Any]:
        return {
            "manufacturing_pmi":             self._f(raw, "ISM_PMI"),
            "industrial_output_index":       self._f(raw, "FED_INDPRO_YOY"),
            "supply_chain_stress":           self._f(raw, "NYFED_GSCPI_NORM"),
            "freight_rate_index":            self._f(raw, "FBX_FREIGHT_NORM"),
            "port_congestion_index":         self._f(raw, "UNCTAD_PORT_CONGESTION"),
            "energy_price_index":            self._f(raw, "EIA_ENERGY_PRICE_INDEX"),
            "oil_price":                     self._f(raw, "EIA_WTI_CRUDE"),
            "natural_gas_price":             self._f(raw, "EIA_HENRY_HUB"),
            "coal_price":                    self._f(raw, "API2_COAL_ROTTERDAM"),
            "semiconductor_shortage_index":  self._f(raw, "WSTS_SEMI_SHORTAGE_NORM"),
            "rare_earth_supply_index":       self._f(raw, "REIA_RARE_EARTH_SCARCITY"),
            "capacity_utilization":          self._f(raw, "FED_CAP_UTIL_PCT"),
            "inventory_to_sales_ratio":      self._f(raw, "CENSUS_INV_SALES_RATIO"),
            "labor_productivity":            self._f(raw, "BLS_LABOR_PRODUCTIVITY_YOY"),
            "capex_investment_index":        self._f(raw, "SP500_CAPEX_GROWTH_YOY"),
            "grid_stability_index":          self._f(raw, "NERC_GRID_STABILITY"),
            "water_stress_index":            self._f(raw, "WRI_WATER_STRESS"),
        }

    @staticmethod
    def _f(d: dict, key: str, default: float = 0.0) -> float:
        try:
            return float(d.get(key, default))
        except (TypeError, ValueError):
            return default

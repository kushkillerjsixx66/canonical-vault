"""
Vara.ECON — Economics Domain Harvester

Sources modelled (simulated adapters; swap fetch() for live API calls):
  - Federal Reserve Economic Data (FRED)
  - BLS (CPI, unemployment)
  - Treasury yield curve
  - ISM manufacturing PMI
  - Census Bureau (retail sales, trade balance)

In production: replace _simulate_source() with authenticated HTTP calls
to each data provider. The normalise() contract stays identical.
"""

from __future__ import annotations

import math
import random
from datetime import datetime
from typing import Any

from vara.domain_ontology import ECON_ONTOLOGY, DomainOntology
from vara.harvesters.base_harvester import BaseHarvester


class EconHarvester(BaseHarvester):
    """
    Domain harvester for Economics (Vara.ECON).

    Signal coverage
    ---------------
    gdp_growth             : annualised real GDP growth rate (%)
    inflation_rate         : YoY CPI change (%)
    unemployment_rate      : U-3 unemployment rate (%)
    interest_rate          : Federal Funds Rate target (%)
    trade_balance          : goods & services trade balance ($bn)
    consumer_confidence    : Conference Board CCI (index)
    ppi                    : Producer Price Index YoY (%)
    cpi                    : CPI all-items (index)
    m2_supply              : M2 money supply YoY growth (%)
    yield_curve            : 10Y minus 2Y Treasury spread (%)
    debt_to_gdp            : Federal debt as % of GDP
    budget_deficit         : Federal budget deficit ($bn, negative = deficit)
    fx_rate                : DXY US Dollar Index
    credit_spread          : ICE BofA HY spread (bps)
    ism_manufacturing      : ISM Manufacturing PMI
    retail_sales           : MoM retail sales change (%)
    """

    DOMAIN = "ECON"

    @property
    def domain_id(self) -> str:
        return self.DOMAIN

    @property
    def ontology(self) -> DomainOntology:
        return ECON_ONTOLOGY

    # ------------------------------------------------------------------
    # Data acquisition
    # ------------------------------------------------------------------

    async def fetch(self) -> dict[str, Any]:
        """
        Fetch economic indicators.
        Stub: returns simulated values representative of a mild-stress scenario.
        Replace with FRED API / BLS / Treasury calls in production.
        """
        return self._simulate_source()

    def _simulate_source(self) -> dict[str, Any]:
        """Simulate an ECON data pull with mild macro stress."""
        rng = random.Random(int(datetime.utcnow().timestamp()) // 1800)
        return {
            # Core macro
            "FRED_GDP_GROWTH":        round(rng.gauss(2.1, 0.6), 2),
            "BLS_CPI_YOY":            round(rng.gauss(4.8, 0.9), 2),
            "BLS_UNEMPLOYMENT":       round(rng.gauss(4.2, 0.4), 2),
            "FED_FUNDS_RATE":         round(rng.gauss(5.25, 0.12), 2),
            # Trade & fiscal
            "CENSUS_TRADE_BALANCE":   round(rng.gauss(-78.5, 8.0), 1),
            "FRB_CONSUMER_CONF":      round(rng.gauss(102.4, 6.0), 1),
            "BLS_PPI_YOY":            round(rng.gauss(3.9, 0.7), 2),
            "BLS_CPI_INDEX":          round(rng.gauss(312.4, 2.5), 1),
            # Monetary
            "FRB_M2_GROWTH":          round(rng.gauss(2.8, 1.2), 2),
            "TREAS_YIELD_SPREAD_10_2":round(rng.gauss(-0.12, 0.20), 3),  # slight inversion
            "CBO_DEBT_TO_GDP":        round(rng.gauss(122.5, 3.0), 1),
            "OMB_BUDGET_DEFICIT":     round(rng.gauss(-1850.0, 120.0), 0),
            # Markets
            "DXY_INDEX":              round(rng.gauss(103.8, 1.5), 2),
            "ICE_HY_SPREAD_BPS":      round(rng.gauss(340.0, 40.0), 0),
            "ISM_MANUFACTURING_PMI":  round(rng.gauss(48.6, 1.8), 1),
            "CENSUS_RETAIL_SALES_MOM":round(rng.gauss(0.3, 0.5), 2),
        }

    # ------------------------------------------------------------------
    # Normalisation
    # ------------------------------------------------------------------

    def normalise(self, raw: dict[str, Any]) -> dict[str, Any]:
        """
        Map raw source keys → canonical ECON ontology signal_types.
        All values are cast to float where possible.
        """
        return {
            "gdp_growth":          self._f(raw, "FRED_GDP_GROWTH"),
            "inflation_rate":      self._f(raw, "BLS_CPI_YOY"),
            "unemployment_rate":   self._f(raw, "BLS_UNEMPLOYMENT"),
            "interest_rate":       self._f(raw, "FED_FUNDS_RATE"),
            "trade_balance":       self._f(raw, "CENSUS_TRADE_BALANCE"),
            "consumer_confidence": self._f(raw, "FRB_CONSUMER_CONF"),
            "ppi":                 self._f(raw, "BLS_PPI_YOY"),
            "cpi":                 self._f(raw, "BLS_CPI_INDEX"),
            "m2_supply":           self._f(raw, "FRB_M2_GROWTH"),
            "yield_curve":         self._f(raw, "TREAS_YIELD_SPREAD_10_2"),
            "debt_to_gdp":         self._f(raw, "CBO_DEBT_TO_GDP"),
            "budget_deficit":      self._f(raw, "OMB_BUDGET_DEFICIT"),
            "fx_rate":             self._f(raw, "DXY_INDEX"),
            "credit_spread":       self._f(raw, "ICE_HY_SPREAD_BPS"),
            "ism_manufacturing":   self._f(raw, "ISM_MANUFACTURING_PMI"),
            "retail_sales":        self._f(raw, "CENSUS_RETAIL_SALES_MOM"),
        }

    @staticmethod
    def _f(d: dict, key: str, default: float = 0.0) -> float:
        try:
            return float(d.get(key, default))
        except (TypeError, ValueError):
            return default

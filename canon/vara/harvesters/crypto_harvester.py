"""
Vara.CRYPTO — Cryptocurrency & Digital Assets Domain Harvester

Sources modelled (simulated; swap fetch() for live calls):
  - CoinGecko / CoinMarketCap (prices, market cap, dominance)
  - CryptoQuant (exchange flows, on-chain velocity)
  - Alternative.me (Fear & Greed Index)
  - Glassnode (miner revenue, hash rate, stablecoin supply)
  - DeFiLlama (TVL)
  - Deribit / Coinglass (funding rate, open interest)
"""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any

from vara.domain_ontology import CRYPTO_ONTOLOGY, DomainOntology
from vara.harvesters.base_harvester import BaseHarvester


class CryptoHarvester(BaseHarvester):
    """
    Domain harvester for Crypto & Digital Assets (Vara.CRYPTO).

    High-frequency harvester (cadence = 15 min).
    Escalation bias = 1.3 — crypto signals escalate faster.

    Signal coverage
    ---------------
    btc_price              : BTC/USD spot price
    eth_price              : ETH/USD spot price
    btc_dominance          : BTC % of total crypto market cap
    total_market_cap       : total crypto market cap ($bn)
    fear_greed_index       : 0=Extreme Fear, 100=Extreme Greed
    exchange_inflow        : BTC daily inflow to exchanges (units)
    exchange_outflow       : BTC daily outflow from exchanges (units)
    stablecoin_supply      : USDT+USDC total supply ($bn)
    funding_rate           : 8h perpetual swap funding rate (%)
    open_interest          : BTC perp open interest ($bn)
    hash_rate              : BTC network hash rate (EH/s)
    miner_revenue          : daily miner revenue ($m)
    defi_tvl               : total DeFi TVL ($bn)
    nft_volume             : 24h NFT sales volume ($m)
    regulatory_sentiment   : -1 (hostile) to +1 (friendly)
    on_chain_velocity      : coin days destroyed / circulating supply
    """

    DOMAIN = "CRYPTO"

    @property
    def domain_id(self) -> str:
        return self.DOMAIN

    @property
    def ontology(self) -> DomainOntology:
        return CRYPTO_ONTOLOGY

    async def fetch(self) -> dict[str, Any]:
        return self._simulate_source()

    def _simulate_source(self) -> dict[str, Any]:
        rng = random.Random(int(datetime.utcnow().timestamp()) // 900)
        # Simulate a moderately stressed crypto environment
        return {
            "COINGECKO_BTC_USD":          round(rng.gauss(61500.0, 2800.0), 0),
            "COINGECKO_ETH_USD":          round(rng.gauss(3100.0, 180.0), 0),
            "CMC_BTC_DOMINANCE_PCT":      round(rng.gauss(52.4, 1.8), 2),
            "CMC_TOTAL_MCAP_BN":          round(rng.gauss(2280.0, 95.0), 0),
            "ALTME_FEAR_GREED":           round(rng.gauss(38.0, 12.0), 0),   # fear zone
            "CRYPTOQUANT_BTC_INFLOW":     round(rng.gauss(22400.0, 5000.0), 0),
            "CRYPTOQUANT_BTC_OUTFLOW":    round(rng.gauss(19800.0, 4500.0), 0),
            "GLASSNODE_STABLE_SUPPLY_BN": round(rng.gauss(145.0, 8.0), 1),
            "COINGLASS_FUNDING_RATE":     round(rng.gauss(0.015, 0.025), 4),
            "COINGLASS_OI_BN":            round(rng.gauss(18.5, 2.2), 2),
            "GLASSNODE_HASHRATE_EHS":     round(rng.gauss(620.0, 25.0), 1),
            "GLASSNODE_MINER_REV_M":      round(rng.gauss(42.0, 6.0), 1),
            "DEFILLAMA_TVL_BN":           round(rng.gauss(98.0, 9.0), 1),
            "NFT_24H_VOLUME_M":           round(rng.gauss(55.0, 18.0), 1),
            "NLP_REG_SENTIMENT":          round(rng.gauss(-0.18, 0.22), 3),
            "GLASSNODE_CDD_VELOCITY":     round(rng.gauss(0.042, 0.015), 4),
        }

    def normalise(self, raw: dict[str, Any]) -> dict[str, Any]:
        return {
            "btc_price":            self._f(raw, "COINGECKO_BTC_USD"),
            "eth_price":            self._f(raw, "COINGECKO_ETH_USD"),
            "btc_dominance":        self._f(raw, "CMC_BTC_DOMINANCE_PCT"),
            "total_market_cap":     self._f(raw, "CMC_TOTAL_MCAP_BN"),
            "fear_greed_index":     self._f(raw, "ALTME_FEAR_GREED"),
            "exchange_inflow":      self._f(raw, "CRYPTOQUANT_BTC_INFLOW"),
            "exchange_outflow":     self._f(raw, "CRYPTOQUANT_BTC_OUTFLOW"),
            "stablecoin_supply":    self._f(raw, "GLASSNODE_STABLE_SUPPLY_BN"),
            "funding_rate":         self._f(raw, "COINGLASS_FUNDING_RATE"),
            "open_interest":        self._f(raw, "COINGLASS_OI_BN"),
            "hash_rate":            self._f(raw, "GLASSNODE_HASHRATE_EHS"),
            "miner_revenue":        self._f(raw, "GLASSNODE_MINER_REV_M"),
            "defi_tvl":             self._f(raw, "DEFILLAMA_TVL_BN"),
            "nft_volume":           self._f(raw, "NFT_24H_VOLUME_M"),
            "regulatory_sentiment": self._f(raw, "NLP_REG_SENTIMENT"),
            "on_chain_velocity":    self._f(raw, "GLASSNODE_CDD_VELOCITY"),
        }

    @staticmethod
    def _f(d: dict, key: str, default: float = 0.0) -> float:
        try:
            return float(d.get(key, default))
        except (TypeError, ValueError):
            return default

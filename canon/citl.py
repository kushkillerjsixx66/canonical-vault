"""
CDS-Ω1 Canon Intelligence Transport Layer (CITL)
In-process async message bus with topic routing, envelope wrapping,
subscriber fanout, and dead-letter queue.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Awaitable, Callable

from models import DIP, SCP, CSP

logger = logging.getLogger("cds.citl")

# ---------------------------------------------------------------------------
# Topic registry  (mirrors spec §3.1)
# ---------------------------------------------------------------------------

class Topic:
    # Upstream
    DIP_RAW     = "canon.dip.raw.{domain}"   # parameterised — use topic_for()
    DIP_ALIGNED = "canon.dip.aligned"

    # Internal
    SCP_PAIRWISE = "canon.scp.pairwise"
    CMX_GRID     = "canon.cmx.grid"

    # Downstream
    CSP_SYNTHESIS       = "canon.csp.synthesis"
    PARADOX_INTAKE      = "canon.paradox.intake"
    FIELD_INTEL_INTAKE  = "canon.fieldintel.intake"
    OPERATOR_DASHBOARD  = "canon.operator.dashboard"

    @staticmethod
    def dip_raw(domain: str) -> str:
        return f"canon.dip.raw.{domain.upper()}"


# ---------------------------------------------------------------------------
# Envelope  (spec §3.2)
# ---------------------------------------------------------------------------

SUBSYSTEM_ID = "CDS-Ω1"


def wrap(packet: DIP | SCP | CSP | dict) -> dict:
    """Wrap any packet in the standard CITL envelope."""
    payload = packet.to_dict() if hasattr(packet, "to_dict") else packet
    return {
        "envelope_version": "1.0",
        "subsystem_id": SUBSYSTEM_ID,
        "sent_at": datetime.utcnow().isoformat(),
        "packet": payload,
    }


def unwrap(envelope: dict) -> dict:
    """Extract the inner packet from an envelope; validates envelope shape."""
    if "packet" not in envelope:
        raise ValueError(f"Missing 'packet' key in envelope: {list(envelope.keys())}")
    return envelope["packet"]


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------

@dataclass
class Message:
    topic: str
    envelope: dict
    publish_time: datetime = field(default_factory=datetime.utcnow)

    @property
    def packet(self) -> dict:
        return self.envelope["packet"]

    def to_json(self) -> str:
        return json.dumps({
            "topic": self.topic,
            "publish_time": self.publish_time.isoformat(),
            **self.envelope,
        }, indent=2)


# ---------------------------------------------------------------------------
# Dead-letter Queue entry
# ---------------------------------------------------------------------------

@dataclass
class DeadLetter:
    message: Message
    subscriber: str
    error: str
    failed_at: datetime = field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Subscriber handle
# ---------------------------------------------------------------------------

Handler = Callable[[Message], Awaitable[None]]


@dataclass
class Subscriber:
    name: str
    handler: Handler
    # optional topic prefix filter (None = exact match only)
    prefix: bool = False          # if True, match topic.startswith(pattern)


# ---------------------------------------------------------------------------
# CITL Message Bus
# ---------------------------------------------------------------------------

class CITLBus:
    """
    Async pub/sub message bus.

    Features
    --------
    - Exact topic subscriptions and wildcard-prefix subscriptions
      (subscribe("canon.dip.raw.", prefix=True) catches all domains).
    - Async fanout: all subscribers for a topic are invoked concurrently.
    - Per-subscriber error isolation with dead-letter capture.
    - Message history (ring buffer, configurable depth).
    - Stats counter per topic.
    """

    def __init__(self, history_depth: int = 500) -> None:
        # topic -> list[Subscriber]
        self._exact: dict[str, list[Subscriber]] = defaultdict(list)
        self._prefix: list[tuple[str, Subscriber]] = []   # (prefix, subscriber)

        self._history: list[Message] = []
        self._history_depth = history_depth

        self._dead_letters: list[DeadLetter] = []
        self._stats: dict[str, int] = defaultdict(int)

        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    def subscribe(
        self,
        topic_pattern: str,
        handler: Handler,
        name: str = "",
        prefix: bool = False,
    ) -> None:
        """
        Register a handler.

        Parameters
        ----------
        topic_pattern : exact topic string, or prefix if prefix=True.
        handler       : async callable(Message) -> None.
        name          : human-readable subscriber identifier.
        prefix        : if True, match any topic that starts with topic_pattern.
        """
        sub = Subscriber(name=name or handler.__name__, handler=handler, prefix=prefix)
        if prefix:
            self._prefix.append((topic_pattern, sub))
            logger.debug("Subscribed (prefix) %s → %s", topic_pattern, sub.name)
        else:
            self._exact[topic_pattern].append(sub)
            logger.debug("Subscribed (exact)  %s → %s", topic_pattern, sub.name)

    def unsubscribe(self, topic_pattern: str, name: str, prefix: bool = False) -> bool:
        """Remove a named subscriber. Returns True if found."""
        if prefix:
            before = len(self._prefix)
            self._prefix = [(p, s) for p, s in self._prefix
                            if not (p == topic_pattern and s.name == name)]
            return len(self._prefix) < before
        subs = self._exact.get(topic_pattern, [])
        filtered = [s for s in subs if s.name != name]
        self._exact[topic_pattern] = filtered
        return len(filtered) < len(subs)

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    async def publish(self, topic: str, packet: Any) -> int:
        """
        Wrap packet, emit to all matching subscribers, return delivery count.
        """
        envelope = wrap(packet)
        msg = Message(topic=topic, envelope=envelope)

        async with self._lock:
            self._history.append(msg)
            if len(self._history) > self._history_depth:
                self._history.pop(0)
            self._stats[topic] += 1

        # Collect subscribers
        recipients: list[Subscriber] = list(self._exact.get(topic, []))
        for prefix_pat, sub in self._prefix:
            if topic.startswith(prefix_pat):
                recipients.append(sub)

        if not recipients:
            logger.debug("No subscribers for topic: %s", topic)
            return 0

        # Fanout concurrently
        results = await asyncio.gather(
            *[self._deliver(sub, msg) for sub in recipients],
            return_exceptions=True,
        )

        delivered = sum(1 for r in results if r is True)
        logger.info(
            "Published → %s  |  delivered=%d/%d",
            topic, delivered, len(recipients),
        )
        return delivered

    async def _deliver(self, sub: Subscriber, msg: Message) -> bool:
        try:
            await sub.handler(msg)
            return True
        except Exception as exc:
            dl = DeadLetter(message=msg, subscriber=sub.name, error=str(exc))
            self._dead_letters.append(dl)
            logger.error(
                "Dead-letter from %s on topic %s: %s",
                sub.name, msg.topic, exc,
            )
            return False

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, int]:
        return dict(self._stats)

    def history(self, topic: str | None = None, last_n: int = 50) -> list[Message]:
        msgs = self._history if topic is None else [
            m for m in self._history if m.topic == topic
        ]
        return msgs[-last_n:]

    def dead_letters(self) -> list[DeadLetter]:
        return list(self._dead_letters)

    def clear_dead_letters(self) -> None:
        self._dead_letters.clear()

    def topic_subscriber_map(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for topic, subs in self._exact.items():
            out[topic] = [s.name for s in subs]
        for prefix_pat, sub in self._prefix:
            key = f"{prefix_pat}* (prefix)"
            out.setdefault(key, []).append(sub.name)
        return out

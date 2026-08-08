"""
PARADOX_ENGINE_1.0 — Core Paradox Representation
Canon Layer: CORE
Lineage Root: CANON:LATTICE:PARADOX_ENGINE

Defines the atomic units of the engine:
  Polarity       — truth-value in a paradox context
  Proposition    — a single logical claim, possibly self-referential
  ParadoxNode    — a node in the recursive exploration tree
  Paradox        — the root object passed into the engine
"""

from __future__ import annotations

import hashlib
import re
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Set


# ── Polarity ────────────────────────────────────────────────────────────────

class Polarity(Enum):
    """
    Truth-value assignment for a proposition inside a paradox simulation.
    PARADOXICAL is assigned when both TRUE and FALSE branches loop back
    to the same proposition — i.e., a stable self-negation cycle.
    """
    TRUE          = auto()
    FALSE         = auto()
    INDETERMINATE = auto()
    PARADOXICAL   = auto()


# ── Self-Reference Classification ───────────────────────────────────────────

class SelfRefClass(Enum):
    """
    Classifies the *kind* of self-reference present in a proposition.
    Used by the resolver to choose the correct expansion strategy.
    """
    NONE          = auto()   # No self-reference detected
    DIRECT        = auto()   # Proposition explicitly negates itself
    INDIRECT      = auto()   # Proposition references a chain that loops back
    STRUCTURAL    = auto()   # Paradox is in the set/membership structure
    MODAL         = auto()   # Paradox involves necessity/possibility operators


# ── Proposition ─────────────────────────────────────────────────────────────

@dataclass
class Proposition:
    """
    A single logical claim.

    Attributes
    ----------
    text        : Natural-language statement of the claim.
    tokens      : Normalised token set, used for drift and inflation metrics.
    self_ref    : Classification of any self-referential structure detected.
    polarity    : Initial assigned polarity (may be updated by resolver).
    origin_id   : UUID of the Paradox that spawned this proposition.
    depth       : Recursion depth at which this proposition was created.
    """
    text:      str
    origin_id: str                      = field(default_factory=lambda: str(uuid.uuid4()))
    depth:     int                      = 0
    polarity:  Polarity                 = Polarity.INDETERMINATE
    self_ref:  SelfRefClass             = SelfRefClass.NONE
    tokens:    Set[str]                 = field(default_factory=set)

    def __post_init__(self) -> None:
        if not self.tokens:
            self.tokens = _tokenise(self.text)
        if self.self_ref is SelfRefClass.NONE:
            self.self_ref = _classify_self_ref(self.text)

    @property
    def fingerprint(self) -> str:
        """Stable SHA-256 hex digest of the normalised text."""
        return hashlib.sha256(self.text.strip().lower().encode()).hexdigest()

    def negate(self) -> "Proposition":
        """Return a new Proposition that is the logical negation of this one."""
        negated_text = _negate_text(self.text)
        return Proposition(
            text=negated_text,
            origin_id=self.origin_id,
            depth=self.depth + 1,
            polarity=_flip(self.polarity),
        )

    def __hash__(self) -> int:
        return hash(self.fingerprint)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Proposition):
            return NotImplemented
        return self.fingerprint == other.fingerprint

    def __repr__(self) -> str:
        return (
            f"Proposition(depth={self.depth}, polarity={self.polarity.name}, "
            f"self_ref={self.self_ref.name}, text={self.text!r})"
        )


# ── ParadoxNode ──────────────────────────────────────────────────────────────

@dataclass
class ParadoxNode:
    """
    A single node in the recursive exploration tree.

    The resolver produces a tree of ParadoxNodes rooted at the seed
    Proposition. Each node holds its proposition, the polarity under
    which it was evaluated, and references to child nodes spawned by
    expansion.
    """
    proposition:  Proposition
    parent_id:    Optional[str]           = None
    node_id:      str                     = field(default_factory=lambda: str(uuid.uuid4()))
    children:     List["ParadoxNode"]     = field(default_factory=list)
    is_cycle:     bool                    = False    # True if this closes a cycle
    is_contained: bool                    = False    # True if enforcement bounded it
    created_at:   float                   = field(default_factory=time.monotonic)

    @property
    def depth(self) -> int:
        return self.proposition.depth

    @property
    def fingerprint(self) -> str:
        return self.proposition.fingerprint

    def add_child(self, child: "ParadoxNode") -> None:
        self.children.append(child)

    def __repr__(self) -> str:
        status = "CYCLE" if self.is_cycle else ("CONTAINED" if self.is_contained else "OPEN")
        return (
            f"ParadoxNode(id={self.node_id[:8]}, depth={self.depth}, "
            f"status={status}, prop={self.proposition.text!r})"
        )


# ── Paradox ──────────────────────────────────────────────────────────────────

@dataclass
class Paradox:
    """
    The root object submitted to the ParadoxEngine.

    A Paradox is a seed proposition that the engine will recursively
    explore, contain, and eventually archive or decay.

    Attributes
    ----------
    seed_text    : The original paradoxical statement.
    label        : Human-readable name for this paradox instance.
    paradox_id   : UUID, immutable after creation.
    created_at   : Unix timestamp of creation.
    metadata     : Arbitrary key-value context tags.
    """
    seed_text:   str
    label:       str                       = ""
    paradox_id:  str                       = field(default_factory=lambda: str(uuid.uuid4()))
    created_at:  float                     = field(default_factory=time.time)
    metadata:    dict                      = field(default_factory=dict)

    # Derived on first access
    _seed_proposition: Optional[Proposition] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.label:
            self.label = f"paradox-{self.paradox_id[:8]}"

    @property
    def seed_proposition(self) -> Proposition:
        if self._seed_proposition is None:
            self._seed_proposition = Proposition(
                text=self.seed_text,
                origin_id=self.paradox_id,
                depth=0,
            )
        return self._seed_proposition

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(
            f"{self.paradox_id}:{self.seed_text}".encode()
        ).hexdigest()

    def __repr__(self) -> str:
        return (
            f"Paradox(id={self.paradox_id[:8]}, label={self.label!r}, "
            f"seed={self.seed_text!r})"
        )


# ── Built-in Paradox Library ─────────────────────────────────────────────────

class ParadoxLibrary:
    """
    A curated collection of seed paradoxes for testing and demonstration.
    Each entry is a (label, seed_text) tuple.
    """
    LIAR = (
        "liar",
        "This statement is false.",
    )
    RUSSELL = (
        "russell",
        "The set of all sets that do not contain themselves contains itself.",
    )
    BOOTSTRAP = (
        "bootstrap",
        "A time traveller goes back in time and gives their younger self "
        "the book that inspired them to travel, but no one ever wrote the book.",
    )
    OMNIPOTENCE = (
        "omnipotence",
        "Can an omnipotent being create a stone so heavy that even it cannot lift it?",
    )
    SORITES = (
        "sorites",
        "One grain of sand is not a heap. Adding one grain to a non-heap never makes a heap. "
        "Therefore a million grains of sand is not a heap.",
    )
    SHIP_OF_THESEUS = (
        "theseus",
        "If every plank of a ship is replaced, is it still the same ship? "
        "If yes, is the ship rebuilt from the original planks also the same ship?",
    )

    @classmethod
    def all(cls) -> List[Paradox]:
        entries = [
            cls.LIAR, cls.RUSSELL, cls.BOOTSTRAP,
            cls.OMNIPOTENCE, cls.SORITES, cls.SHIP_OF_THESEUS,
        ]
        return [Paradox(seed_text=text, label=label) for label, text in entries]

    @classmethod
    def get(cls, label: str) -> Paradox:
        mapping = {
            "liar": cls.LIAR,
            "russell": cls.RUSSELL,
            "bootstrap": cls.BOOTSTRAP,
            "omnipotence": cls.OMNIPOTENCE,
            "sorites": cls.SORITES,
            "theseus": cls.SHIP_OF_THESEUS,
        }
        if label not in mapping:
            raise KeyError(f"Unknown paradox label: {label!r}. "
                           f"Available: {list(mapping)}")
        lbl, text = mapping[label]
        return Paradox(seed_text=text, label=lbl)


# ── Internal Helpers ──────────────────────────────────────────────────────────

_NEGATION_PREFIXES = ("It is not the case that ", "NOT: ")
_SELF_REF_PATTERNS = [
    (SelfRefClass.DIRECT,     re.compile(r"\bthis (statement|sentence|claim|proposition)\b", re.I)),
    (SelfRefClass.STRUCTURAL, re.compile(r"\bset of all sets\b",                            re.I)),
    (SelfRefClass.MODAL,      re.compile(r"\b(omnipotent|necessary|possible|cannot)\b",     re.I)),
    (SelfRefClass.INDIRECT,   re.compile(r"\b(itself|themselves|oneself)\b",                re.I)),
]


def _tokenise(text: str) -> Set[str]:
    """Lowercase, strip punctuation, return word tokens."""
    return set(re.sub(r"[^a-z0-9\s]", "", text.lower()).split())


def _classify_self_ref(text: str) -> SelfRefClass:
    for cls_value, pattern in _SELF_REF_PATTERNS:
        if pattern.search(text):
            return cls_value
    return SelfRefClass.NONE


def _negate_text(text: str) -> str:
    # If already negated, strip the negation (double-negation)
    for prefix in _NEGATION_PREFIXES:
        if text.startswith(prefix):
            return text[len(prefix):]
    return f"{_NEGATION_PREFIXES[0]}{text}"


def _flip(polarity: Polarity) -> Polarity:
    mapping = {
        Polarity.TRUE:          Polarity.FALSE,
        Polarity.FALSE:         Polarity.TRUE,
        Polarity.INDETERMINATE: Polarity.INDETERMINATE,
        Polarity.PARADOXICAL:   Polarity.PARADOXICAL,
    }
    return mapping[polarity]

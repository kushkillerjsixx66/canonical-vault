"""
PARADOX_ENGINE_1.0 — Recursive Resolver
Canon Layer: CORE
Lineage Root: CANON:LATTICE:PARADOX_ENGINE

The RecursiveResolver is the computational heart of the engine.
It expands a seed Proposition into a tree of ParadoxNodes by
alternately negating each branch, detecting cycles, measuring
semantic drift, and tracking narrative inflation — halting under
any hard constraint defined in EngineConfig.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Deque, Dict, List, Optional, Set, Tuple

from paradox_engine.config import EngineConfig, DEFAULT_CONFIG
from paradox_engine.core.paradox import (
    Paradox, Paradox, ParadoxNode, Polarity, Proposition, SelfRefClass, _tokenise
)


# ── Resolution Outcome ────────────────────────────────────────────────────────

class HaltReason:
    DEPTH_LIMIT          = "DEPTH_LIMIT"
    ITERATION_LIMIT      = "ITERATION_LIMIT"
    BRANCH_LIMIT         = "BRANCH_LIMIT"
    RUNTIME_LIMIT        = "RUNTIME_LIMIT"
    DRIFT_EXCEEDED       = "DRIFT_EXCEEDED"
    INFLATION_EXCEEDED   = "INFLATION_EXCEEDED"
    ALL_CYCLES_CLOSED    = "ALL_CYCLES_CLOSED"
    ENFORCEMENT_HALT     = "ENFORCEMENT_HALT"


@dataclass
class ResolutionResult:
    """
    The complete output of a single resolver run.

    Attributes
    ----------
    root            : Root ParadoxNode of the exploration tree.
    halt_reason     : Why the resolver stopped.
    total_nodes     : Total nodes created.
    cycle_count     : Number of cycle-closing nodes detected.
    max_depth_hit   : Deepest depth reached.
    unique_props    : All unique Proposition fingerprints seen.
    drift_score     : Final drift value (0.0 = no drift, 1.0 = fully diverged).
    inflation_ratio : Final narrative inflation ratio.
    elapsed_seconds : Wall-clock time consumed.
    iterations      : Total resolver loop iterations.
    branch_trace    : Ordered list of (depth, fingerprint, polarity) for audit.
    """
    root:             ParadoxNode
    halt_reason:      str
    total_nodes:      int
    cycle_count:      int
    max_depth_hit:    int
    unique_props:     Set[str]
    drift_score:      float
    inflation_ratio:  float
    elapsed_seconds:  float
    iterations:       int
    branch_trace:     List[Tuple[int, str, str]]  = field(default_factory=list)

    @property
    def contained(self) -> bool:
        """True when resolution ended due to a hard containment limit."""
        containment_reasons = {
            HaltReason.DEPTH_LIMIT, HaltReason.ITERATION_LIMIT,
            HaltReason.BRANCH_LIMIT, HaltReason.RUNTIME_LIMIT,
            HaltReason.DRIFT_EXCEEDED, HaltReason.INFLATION_EXCEEDED,
            HaltReason.ENFORCEMENT_HALT,
        }
        return self.halt_reason in containment_reasons

    def summary(self) -> dict:
        return {
            "halt_reason":      self.halt_reason,
            "contained":        self.contained,
            "total_nodes":      self.total_nodes,
            "cycle_count":      self.cycle_count,
            "max_depth":        self.max_depth_hit,
            "unique_props":     len(self.unique_props),
            "drift_score":      round(self.drift_score, 4),
            "inflation_ratio":  round(self.inflation_ratio, 4),
            "elapsed_seconds":  round(self.elapsed_seconds, 6),
            "iterations":       self.iterations,
        }


# ── Recursive Resolver ────────────────────────────────────────────────────────

class RecursiveResolver:
    """
    Iterative (stack-based) recursive paradox resolver.

    Uses a depth-first strategy with cycle detection via proposition
    fingerprint tracking. Expansion strategy is selected per-node based
    on the SelfRefClass of the proposition:

      DIRECT     → negate the proposition and recurse
      INDIRECT   → generate an indirect closure proposition and recurse
      STRUCTURAL → expand into membership and complement branches
      MODAL      → expand into possibility and necessity branches
      NONE       → treat as atomic: mark INDETERMINATE and close

    Halt conditions (checked every iteration):
      1. Max depth exceeded on current node
      2. Max iteration count reached
      3. Max branch (live node) count reached
      4. Wall-clock runtime exceeded
      5. Drift score exceeds threshold (sampled every N iterations)
      6. Inflation ratio exceeds limit
      7. All frontier nodes are cycle-closures

    An optional enforcement_hook callable can be passed by the
    EnforcementCluster to inject an immediate ENFORCEMENT_HALT.
    """

    def __init__(
        self,
        config: EngineConfig = DEFAULT_CONFIG,
        enforcement_hook: Optional[Callable[["RecursiveResolver"], bool]] = None,
    ) -> None:
        self._cfg             = config
        self._enforcement_hook = enforcement_hook

    # ── Public Entry Point ────────────────────────────────────────────────────

    def resolve(self, paradox: Paradox) -> ResolutionResult:
        """
        Run recursive resolution on *paradox*.
        Returns a ResolutionResult regardless of how resolution terminates.
        """
        start = time.monotonic()
        seed  = paradox.seed_proposition

        root_node = ParadoxNode(proposition=seed, parent_id=None)

        # State
        visited:      Set[str]                  = set()
        unique_props: Set[str]                  = set()
        branch_trace: List[Tuple[int, str, str]] = []
        stack:        Deque[ParadoxNode]         = deque([root_node])

        iterations   = 0
        cycle_count  = 0
        max_depth    = 0
        halt_reason  = HaltReason.ALL_CYCLES_CLOSED

        # Baseline token set for drift measurement
        baseline_tokens: Set[str] = set(seed.tokens)
        frontier_tokens: Set[str] = set(seed.tokens)
        initial_prop_count        = 1

        cfg_exp  = self._cfg.exploration
        cfg_dft  = self._cfg.drift
        cfg_inf  = self._cfg.inflation

        while stack:
            iterations += 1
            node = stack.pop()
            fp   = node.fingerprint
            depth = node.depth

            # ── Record ────────────────────────────────────────────────────────
            unique_props.add(fp)
            frontier_tokens.update(node.proposition.tokens)
            branch_trace.append((depth, fp[:16], node.proposition.polarity.name))
            if depth > max_depth:
                max_depth = depth

            # ── Hard Halts ────────────────────────────────────────────────────
            elapsed = time.monotonic() - start

            if depth >= cfg_exp.max_depth:
                node.is_contained = True
                halt_reason = HaltReason.DEPTH_LIMIT
                break

            if iterations >= cfg_exp.max_iterations:
                node.is_contained = True
                halt_reason = HaltReason.ITERATION_LIMIT
                break

            if len(stack) >= cfg_exp.max_branches:
                node.is_contained = True
                halt_reason = HaltReason.BRANCH_LIMIT
                break

            if elapsed >= cfg_exp.max_runtime_seconds:
                node.is_contained = True
                halt_reason = HaltReason.RUNTIME_LIMIT
                break

            if len(unique_props) >= cfg_exp.max_propositions:
                node.is_contained = True
                halt_reason = HaltReason.INFLATION_EXCEEDED
                break

            # ── Sampled Checks (every N iterations) ──────────────────────────
            if iterations % cfg_dft.sample_interval == 0:
                drift = _jaccard_distance(baseline_tokens, frontier_tokens)
                if drift >= cfg_dft.hard_ceiling:
                    node.is_contained = True
                    halt_reason = HaltReason.DRIFT_EXCEEDED
                    break
                if drift >= cfg_dft.drift_threshold:
                    # Soft warning — continue but flag
                    node.proposition.metadata = getattr(node.proposition, "metadata", {})

                inflation = len(unique_props) / max(initial_prop_count, 1)
                if inflation >= cfg_inf.inflation_hard_limit:
                    node.is_contained = True
                    halt_reason = HaltReason.INFLATION_EXCEEDED
                    break

            # ── Enforcement Hook ──────────────────────────────────────────────
            if self._enforcement_hook and self._enforcement_hook(self):
                node.is_contained = True
                halt_reason = HaltReason.ENFORCEMENT_HALT
                break

            # ── Cycle Detection ───────────────────────────────────────────────
            if fp in visited:
                node.is_cycle = True
                cycle_count  += 1
                # Close the cycle: mark as PARADOXICAL, do not expand
                node.proposition.polarity = Polarity.PARADOXICAL
                continue

            visited.add(fp)

            # ── Expand ────────────────────────────────────────────────────────
            children = self._expand(node)
            for child in children:
                node.add_child(child)
                stack.append(child)

        # ── Final Metrics ─────────────────────────────────────────────────────
        elapsed_total  = time.monotonic() - start
        drift_final    = _jaccard_distance(baseline_tokens, frontier_tokens)
        inflation_final = len(unique_props) / max(initial_prop_count, 1)

        return ResolutionResult(
            root            = root_node,
            halt_reason     = halt_reason,
            total_nodes     = iterations,
            cycle_count     = cycle_count,
            max_depth_hit   = max_depth,
            unique_props    = unique_props,
            drift_score     = drift_final,
            inflation_ratio = inflation_final,
            elapsed_seconds = elapsed_total,
            iterations      = iterations,
            branch_trace    = branch_trace,
        )

    # ── Expansion Strategies ──────────────────────────────────────────────────

    def _expand(self, node: ParadoxNode) -> List[ParadoxNode]:
        """
        Select and apply the correct expansion strategy for *node*'s
        self-reference class. Returns a list of child ParadoxNodes.
        """
        sr = node.proposition.self_ref
        if sr == SelfRefClass.DIRECT:
            return self._expand_direct(node)
        elif sr == SelfRefClass.INDIRECT:
            return self._expand_indirect(node)
        elif sr == SelfRefClass.STRUCTURAL:
            return self._expand_structural(node)
        elif sr == SelfRefClass.MODAL:
            return self._expand_modal(node)
        else:
            return self._expand_atomic(node)

    def _expand_direct(self, node: ParadoxNode) -> List[ParadoxNode]:
        """
        Direct self-reference (e.g. Liar Paradox).
        Generates exactly one child: the logical negation.
        """
        negated = node.proposition.negate()
        child   = ParadoxNode(
            proposition = negated,
            parent_id   = node.node_id,
        )
        return [child]

    def _expand_indirect(self, node: ParadoxNode) -> List[ParadoxNode]:
        """
        Indirect self-reference (e.g. circular reference chain).
        Generates two children: the original closure and its negation.
        """
        prop  = node.proposition
        # Closure: restates original as confirmed
        closure_text = f"It holds that: {prop.text}"
        closure_prop = Proposition(
            text=closure_text, origin_id=prop.origin_id,
            depth=prop.depth + 1, polarity=prop.polarity
        )
        # Negation branch
        neg_prop = prop.negate()

        return [
            ParadoxNode(proposition=closure_prop, parent_id=node.node_id),
            ParadoxNode(proposition=neg_prop,     parent_id=node.node_id),
        ]

    def _expand_structural(self, node: ParadoxNode) -> List[ParadoxNode]:
        """
        Structural self-reference (e.g. Russell's Paradox).
        Generates membership branch and complement branch.
        """
        prop = node.proposition
        depth = prop.depth + 1
        origin = prop.origin_id

        member_text = (
            f"The entity described by [{prop.text}] is a member of itself."
        )
        complement_text = (
            f"The entity described by [{prop.text}] is NOT a member of itself."
        )
        return [
            ParadoxNode(
                proposition=Proposition(text=member_text, origin_id=origin, depth=depth,
                                        polarity=Polarity.TRUE),
                parent_id=node.node_id,
            ),
            ParadoxNode(
                proposition=Proposition(text=complement_text, origin_id=origin, depth=depth,
                                        polarity=Polarity.FALSE),
                parent_id=node.node_id,
            ),
        ]

    def _expand_modal(self, node: ParadoxNode) -> List[ParadoxNode]:
        """
        Modal self-reference (e.g. Omnipotence Paradox).
        Generates a possibility branch and a necessity branch.
        """
        prop  = node.proposition
        depth = prop.depth + 1
        origin= prop.origin_id

        possible_text  = f"It is possibly true that: {prop.text}"
        necessary_text = f"It is necessarily true that: {prop.text}"
        return [
            ParadoxNode(
                proposition=Proposition(text=possible_text,  origin_id=origin,
                                        depth=depth, polarity=Polarity.INDETERMINATE),
                parent_id=node.node_id,
            ),
            ParadoxNode(
                proposition=Proposition(text=necessary_text, origin_id=origin,
                                        depth=depth, polarity=Polarity.INDETERMINATE),
                parent_id=node.node_id,
            ),
        ]

    def _expand_atomic(self, node: ParadoxNode) -> List[ParadoxNode]:
        """
        No detected self-reference. Mark INDETERMINATE and do not recurse.
        """
        node.proposition.polarity = Polarity.INDETERMINATE
        return []


# ── Helpers ───────────────────────────────────────────────────────────────────

def _jaccard_distance(a: Set[str], b: Set[str]) -> float:
    """
    Semantic drift proxy: Jaccard distance between token sets.
    Returns 0.0 if both sets are identical; 1.0 if they share nothing.
    """
    if not a and not b:
        return 0.0
    union = a | b
    intersection = a & b
    return 1.0 - len(intersection) / len(union)

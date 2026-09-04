import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from enum import Enum

# =====================
# Core Infrastructure
# =====================


def iso_now():
    return datetime.now(timezone.utc).isoformat()


class NodeState(str, Enum):
    LATENT = "LATENT"
    ACTIVE = "ACTIVE"
    DECAYING = "DECAYING"
    PRUNED = "PRUNED"
    QUARANTINED = "VEIL_QUARANTINE"


class NodeClassification(str, Enum):
    ANCHOR = "ANCHOR"
    STANDARD = "STANDARD"
    VARA_PROMOTED = "VARA_PROMOTED"
    OPERATOR_DIRECTIVE = "OPERATOR_DIRECTIVE"
    AUDIT_RECORD = "AUDIT_RECORD"


class Vault:
    """Append-only Node vault matching the canonical Lattice Node Model."""

    DEFAULT_INVARIANT_TAGS = ["I·COH", "II·REV", "III·ATT", "IV·SIL", "V·DEC"]

    def __init__(self, export_path=None, sentinel=None):
        self.nodes = []
        self.export_path = export_path or os.environ.get("LATTICE_VAULT_EXPORT_PATH", "05_runtime/vault_export.json")
        self.sentinel = sentinel

    @property
    def records(self):
        """Compatibility view for older callers; storage is canonical Nodes."""
        return self.nodes

    def store(self, content, classification=NodeClassification.STANDARD.value, state=NodeState.LATENT.value,
              chain_id=None, invariant_tags=None, operator_note=None, decay_rate=None, decay_window=30,
              prune_reason=None):
        node = self._build_node(
            content=content,
            classification=classification,
            state=state,
            chain_id=chain_id,
            invariant_tags=invariant_tags,
            operator_note=operator_note,
            decay_rate=decay_rate,
            decay_window=decay_window,
            prune_reason=prune_reason,
        )
        self.nodes.append(node)
        return node

    def update(self, node_id, content, **metadata):
        ancestor = self.get(node_id, touch=False)
        if ancestor is None:
            raise KeyError(f"node not found: {node_id}")
        return self.store(content, chain_id=ancestor["node_id"], **metadata)

    def get(self, node_id, touch=True):
        for node in self.nodes:
            if node["node_id"] == node_id:
                self._validate_content_hash(node)
                if touch:
                    referenced = self.store(
                        node["content"],
                        classification=node["classification"],
                        state=NodeState.ACTIVE.value,
                        chain_id=node["node_id"],
                        invariant_tags=list(node["invariant_tags"]),
                        operator_note=node.get("operator_note"),
                        decay_rate=node["decay_rate"],
                        decay_window=node["decay_window"],
                    )
                    referenced["reference_count"] = node["reference_count"] + 1
                    return referenced
                return node
        return None

    def retrieve(self, include_pruned=False):
        nodes = self.nodes if include_pruned else [node for node in self.nodes if node["state"] != NodeState.PRUNED.value]
        for node in nodes:
            self._validate_content_hash(node)
        return nodes

    def chain_trace(self, node_id):
        by_id = {node["node_id"]: node for node in self.nodes}
        trace = []
        current = by_id.get(node_id)
        while current is not None:
            self._validate_content_hash(current)
            trace.append(current)
            parent_id = current.get("chain_id")
            current = by_id.get(parent_id) if parent_id else None
        return list(reversed(trace))

    def export(self, file=None):
        export_path = file or self.export_path
        export_node = {
            "node_id": f"export-{uuid.uuid4()}",
            "content": f"Export vault to {export_path}",
            "attention_cost": 0.0,
            "write_planned": True,
            "reversibility": {"chain_id": f"export-chain-{uuid.uuid4()}", "append_only": True, "reversible": True},
        }
        if self.sentinel is not None:
            g3 = self.sentinel._g3_reversibility(export_node)
            self.sentinel._log(export_node, g3)
            if g3["decision"] != "PASS":
                return {"exported": False, "gate": g3, "path": export_path}

        os.makedirs(os.path.dirname(export_path) or ".", exist_ok=True)
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(self.nodes, f, indent=2)
        return {"exported": True, "path": export_path}

    def reset(self):
        self.nodes.clear()
        return "vault reset"

    def _build_node(self, content, classification, state, chain_id, invariant_tags, operator_note,
                    decay_rate, decay_window, prune_reason):
        content_text = content if isinstance(content, str) else json.dumps(content, sort_keys=True)
        if decay_rate is None:
            decay_rate = self._default_decay_rate(classification)
        now = iso_now()
        pruned_at = now if state == NodeState.PRUNED.value else None
        node = {
            "node_id": str(uuid.uuid4()),
            "chain_id": chain_id,
            "content": content_text,
            "content_hash": hashlib.sha256(content_text.encode("utf-8")).hexdigest(),
            "classification": classification,
            "state": state,
            "created_at": now,
            "last_referenced": now,
            "decay_rate": decay_rate,
            "decay_window": decay_window,
            "reference_count": 0,
            "invariant_tags": invariant_tags or list(self.DEFAULT_INVARIANT_TAGS),
            "operator_note": operator_note,
            "pruned_at": pruned_at,
            "prune_reason": prune_reason,
            "pruning": {"eligible": classification not in {NodeClassification.ANCHOR.value, NodeClassification.AUDIT_RECORD.value}, "candidate_at": None},
        }
        node["reversibility"] = {"chain_id": node["chain_id"] or node["node_id"], "append_only": True, "reversible": True}
        node["attention_cost"] = 0.0
        node["write_planned"] = True
        return node

    def _default_decay_rate(self, classification):
        return {
            NodeClassification.ANCHOR.value: 0.0,
            NodeClassification.VARA_PROMOTED.value: 0.5,
            NodeClassification.OPERATOR_DIRECTIVE.value: 0.1,
            NodeClassification.AUDIT_RECORD.value: 0.0,
        }.get(classification, 0.3)

    def _validate_content_hash(self, node):
        actual = hashlib.sha256(node["content"].encode("utf-8")).hexdigest()
        if actual != node["content_hash"]:
            raise ValueError(f"content hash mismatch for node {node['node_id']}")


class Echo:

    def __init__(self):
        self.history = []

    def record(self, data):
        self.history.append(data)

    def trace(self):
        return self.history

    def reset(self):
        self.history.clear()
        return "echo reset"


class Sentinel:
    """Runtime implementation of Governance Gates G1, G2, and G3."""

    def __init__(self, coherence_threshold=0.75, attention_budget=10.0):
        self.coherence_threshold = coherence_threshold
        self.default_attention_budget = attention_budget
        self.attention_budget = attention_budget
        self.attention_spent = 0.0
        self.governance_log = []

    def inspect(self, node, context=None):
        context = context or []
        return self.evaluate_gates(node, context)

    def evaluate_gates(self, node, context):
        g1 = self._g1_coherence(node, context)
        self._log(node, g1)
        if g1["decision"] == "BLOCK":
            node["state"] = NodeState.QUARANTINED.value
            node["quarantine"] = {"gate": "G1", "reason_code": "G1_COHERENCE_VIOLATION"}
            return {"allowed": False, "node": node, "gate": g1}

        g2 = self._g2_attention(node, context)
        self._log(node, g2)
        if g2["decision"] == "SOFT_BLOCK":
            node["state"] = NodeState.LATENT.value
            node["deferred"] = {"gate": "G2", "reason_code": "G2_SOFT_BLOCK"}
            return {"allowed": False, "node": node, "gate": g2}

        g3 = self._g3_reversibility(node)
        self._log(node, g3)
        if g3["decision"] == "BLOCK":
            node["state"] = NodeState.PRUNED.value
            node["write_rejected"] = {"gate": "G3", "reason_code": "G3_REVERSIBILITY_VIOLATION"}
            return {"allowed": False, "node": node, "gate": g3}

        self.attention_spent += node["attention_cost"]
        node["governance"] = [g1, g2, g3]
        return {"allowed": True, "node": node, "gate": g3}

    def _g1_coherence(self, node, context):
        signal = node.get("signal")
        score = 1.0
        reasons = []
        if signal is None or str(signal).strip() == "":
            score -= 0.5
            reasons.append("empty or unsituated signal")
        if isinstance(signal, str) and "contradiction" in signal.lower():
            score -= 0.3
            reasons.append("explicit contradiction marker")
        for existing in context:
            if existing.get("state") in {NodeState.ACTIVE.value, "ANCHOR"}:
                if existing.get("signal") == signal and existing.get("state") == "ANCHOR":
                    continue
        decision = "PASS" if score >= self.coherence_threshold else "BLOCK"
        return {
            "code": "G1_PASS" if decision == "PASS" else "G1_BLOCK",
            "gate": "G1",
            "decision": decision,
            "score": round(score, 3),
            "reason": "; ".join(reasons) or "coherence validated",
        }

    def _g2_attention(self, node, context):
        projected = self.attention_spent + node["attention_cost"]
        decision = "PASS" if projected <= self.attention_budget else "SOFT_BLOCK"
        return {
            "code": "G2_PASS" if decision == "PASS" else "G2_SOFT_BLOCK",
            "gate": "G2",
            "decision": decision,
            "cost": node["attention_cost"],
            "budget": self.attention_budget,
            "projected": round(projected, 3),
            "reason": "within attention budget" if decision == "PASS" else "attention budget exceeded; downgraded to LATENT",
        }

    def _g3_reversibility(self, node):
        planned_write = node.get("write_planned", True)
        if not planned_write:
            return {"code": "G3_AUTO_PASS", "gate": "G3", "decision": "PASS", "reason": "no write planned"}
        metadata = node.get("reversibility", {})
        has_chain = bool(metadata.get("chain_id"))
        append_only = metadata.get("append_only") is True
        reversible = metadata.get("reversible") is True
        decision = "PASS" if has_chain and append_only and reversible else "BLOCK"
        return {
            "code": "G3_PASS" if decision == "PASS" else "G3_BLOCK",
            "gate": "G3",
            "decision": decision,
            "reason": "reversibility confirmed" if decision == "PASS" else "missing chain, append-only, or reversible metadata",
        }

    def _log(self, node, gate_result):
        self.governance_log.append({"node_id": node.get("node_id") or node.get("id"), "gate": gate_result})

    def reset(self):
        self.attention_budget = self.default_attention_budget
        self.attention_spent = 0.0
        self.governance_log.clear()
        return "sentinel reset"


class Pulse:
    def activate(self, signal):
        return {
            "node_id": str(uuid.uuid4()),
            "signal": signal,
            "state": NodeState.ACTIVE.value,
            "created_at": iso_now(),
            "last_referenced": iso_now(),
            "decay_rate": 0.3,
            "decay_window": 30,
            "reversibility": {"chain_id": f"chain-{uuid.uuid4()}", "append_only": True, "reversible": True, "supersedes": None},
            "attention_cost": self._attention_cost(signal),
            "write_planned": True,
        }

    def _attention_cost(self, signal):
        text = "" if signal is None else str(signal)
        context_size = max(1, len(text.split()))
        inference_depth = 1 + min(3, text.count("?") + text.lower().count("because"))
        vault_writes = 1
        vara_hypotheses = 1 if any(marker in text.lower() for marker in ("maybe", "paradox", "curious")) else 0
        return round((context_size * 0.1) + (inference_depth * 0.3) + (vault_writes * 0.5) + (vara_hypotheses * 0.2), 3)


class Threshold:
    def __init__(self, sentinel):
        self.sentinel = sentinel

    def allow(self, node, context=None):
        return self.sentinel.inspect(node, context)


class Veil:
    def __init__(self):
        self.quarantine = []

    def filter(self, data):
        if data.get("state") == NodeState.QUARANTINED.value:
            self.quarantine.append(data)
        return data

    def reset(self):
        self.quarantine.clear()
        return "veil reset"


class Rift:
    def explore(self, data):
        data["rift"] = True
        return data


class Vara:
    def expand(self, data):
        data["vara"] = "expanded"
        return data


class Stumpy:
    invariants = ["coherence", "attention", "reversibility", "silence", "entropy"]

    def __init__(self, vault=None):
        self.vault = vault

    def audit(self, data):
        report = {}
        for inv in self.invariants:
            report[inv] = inv in data
        return report

    def chain_trace(self, node_id):
        if self.vault is None:
            return []
        return self.vault.chain_trace(node_id)


class Agent:
    def act(self, data):
        return {"result": data}


# =====================
# Lattice Engine
# =====================

class Lattice:

    def __init__(self):
        self.sentinel = Sentinel()
        self.vault = Vault(sentinel=self.sentinel)
        self.echo = Echo()
        self.pulse = Pulse()
        self.threshold = Threshold(self.sentinel)
        self.veil = Veil()
        self.rift = Rift()
        self.vara = Vara()
        self.stumpy = Stumpy(self.vault)
        self.agent = Agent()
        self.silent = False

    def process(self, signal):
        """Run the canonical cycle: Pulse → Activation → Evaluation → Decay → Silence."""
        self.silent = False

        # Pulse / Activation: accept salient events as Node-like structures.
        node = self.pulse.activate(signal)

        # Evaluation: Governance Gates G1, G2, G3 are always on.
        evaluation = self.threshold.allow(node, self.vault.retrieve())
        node = evaluation["node"]
        if not evaluation["allowed"]:
            if node["state"] == NodeState.QUARANTINED.value:
                self.veil.filter(node)
            self.echo.record({"result": node, "accepted": False})
            return {"result": node, "accepted": False}

        # Stage 4 execution remains bias-like and ignorable, not a command.
        v = self.veil.filter(node)
        r = self.rift.explore(v)
        x = self.vara.expand(r)
        result = self.agent.act(x)

        # Decay: reduce relevance metadata before append-only storage.
        result["result"] = self.decay(result["result"])

        self.echo.record(result)
        stored_node = self.vault.store(result["result"], state=NodeState.DECAYING.value)
        result["result"] = stored_node

        # Silence: return to low-noise state after each cycle.
        self.silence()
        return result

    def decay(self, node):
        node = dict(node)
        node["state"] = NodeState.DECAYING.value
        node["last_referenced"] = iso_now()
        node["pruning"] = {"eligible": True, "candidate_at": None}
        return node

    def silence(self):
        self.silent = True
        return "silence"

    def reset(self):
        self.vault.reset()
        self.echo.reset()
        self.sentinel.reset()
        self.veil.reset()
        self.silent = True
        return "Echoes return to the dark"


# =====================
# Symbolic Operators
# =====================

def measurement_operator(value):
    return {"measurement": value}


def operator_identity(user):
    return {"operator": user}


# =====================
# Command Parser
# =====================

class CommandParser:

    def __init__(self, lattice):
        self.lattice = lattice

    def parse(self, text):
        if text in {"Echoes return to the dark", "<Lattice:Reset>", "<Silence:Reset>"}:
            return self.lattice.reset()

        if text == "<Silence>":
            return self.lattice.silence()

        if text.startswith("<Signal:Send>"):
            msg = text.split(">", 1)[-1].strip()
            return self.lattice.process(msg)

        if text == "<Vault:Retrieve>":
            return self.lattice.vault.retrieve()

        if text == "<Vault:Export>":
            return self.lattice.vault.export()

        if text == "<Echo:Trace>":
            return self.lattice.echo.trace()

        if text == "<Stumpy:Audit>":
            history = self.lattice.echo.trace()
            data = history[-1] if history else {}
            return self.lattice.stumpy.audit(data)

        if text.startswith("<Stumpy:ChainTrace>"):
            node_id = text.split(">", 1)[-1].strip()
            return self.lattice.stumpy.chain_trace(node_id)

        if text.startswith("→"):
            value = text.replace("→", "").strip()
            return measurement_operator(value)

        if text.startswith("‰"):
            name = text.replace("‰", "").strip()
            return operator_identity(name)

        return "unknown command"


# =====================
# CLI Runtime
# =====================

def run():
    lattice = Lattice()
    parser = CommandParser(lattice)

    print("Lattice Runtime CLI")
    print("Commands:")
    print("  <Signal:Send> message")
    print("  <Vault:Retrieve>")
    print("  <Vault:Export>")
    print("  <Echo:Trace>")
    print("  <Stumpy:Audit>")
    print("  <Silence>")
    print("  <Lattice:Reset>")
    print("  Echoes return to the dark")
    print("  → value  (measurement operator)")
    print("  ‰ name   (operator identity)")
    print("  exit")

    while True:
        cmd = input(">>> ")

        if cmd in {"exit", "Echoes return to the dark"}:
            print(parser.parse("Echoes return to the dark"))
            break

        result = parser.parse(cmd)
        print(result)


if __name__ == "__main__":
    run()

import json
import time
import uuid
from enum import Enum

# =====================
# Core Infrastructure
# =====================

class NodeState(str, Enum):
    LATENT = "LATENT"
    ACTIVE = "ACTIVE"
    DECAYING = "DECAYING"
    PRUNED = "PRUNED"
    QUARANTINED = "VEIL_QUARANTINE"


class Vault:
    def __init__(self):
        self.records = []

    def store(self, data):
        self.records.append(data)
        return "stored"

    def retrieve(self):
        return self.records

    def export(self, file="vault.json"):
        with open(file, "w") as f:
            json.dump(self.records, f, indent=2)
        return "vault exported"

    def reset(self):
        self.records.clear()
        return "vault reset"


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
        self.governance_log.append({"node_id": node.get("id"), "gate": gate_result})

    def reset(self):
        self.attention_budget = self.default_attention_budget
        self.attention_spent = 0.0
        self.governance_log.clear()
        return "sentinel reset"


class Pulse:
    def activate(self, signal):
        return {
            "id": f"node-{uuid.uuid4()}",
            "signal": signal,
            "state": NodeState.ACTIVE.value,
            "created_at": time.time(),
            "updated_at": time.time(),
            "decay": {"rate": 0.1, "salience": 1.0, "last_decay_at": None},
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

    def audit(self, data):
        report = {}
        for inv in self.invariants:
            report[inv] = inv in data
        return report


class Agent:
    def act(self, data):
        return {"result": data}


# =====================
# Lattice Engine
# =====================

class Lattice:

    def __init__(self):
        self.vault = Vault()
        self.echo = Echo()
        self.sentinel = Sentinel()
        self.pulse = Pulse()
        self.threshold = Threshold(self.sentinel)
        self.veil = Veil()
        self.rift = Rift()
        self.vara = Vara()
        self.stumpy = Stumpy()
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
        self.vault.store(result["result"])

        # Silence: return to low-noise state after each cycle.
        self.silence()
        return result

    def decay(self, node):
        node["state"] = NodeState.DECAYING.value
        node["decay"]["salience"] = max(0.0, round(node["decay"]["salience"] - node["decay"]["rate"], 3))
        node["decay"]["last_decay_at"] = time.time()
        node["updated_at"] = node["decay"]["last_decay_at"]
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
